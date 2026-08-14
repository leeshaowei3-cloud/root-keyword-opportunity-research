#!/usr/bin/env python3
"""Validate inline evidence before declaring an active research pool.

The validator derives every denominator from rows and verifies SHA-256 over the
canonical JSON encoding of each records array (UTF-8, sorted keys, compact
separators, input row order retained). Minimal schema:

{
  "active_pool_declared": false,
  "canonical_slate": {
    "frozen": true,
    "artifact_sha256": "<sha of records>",
    "records": [
      {"keyword_id":"k1", "family_id":"f1", "metric_status":"partial",
       "volume":100, "kd":null, "cpc":null,
       "missing_fields":["kd","cpc"],
       "lanes":["strict_title_supply_longtail"],
       "metric_context":{"market":"US","language":"en","device":"desktop",
         "provider":"semrush","match_type":"exact","checked_date":"2026-08-14"}}
    ]
  },
  "strict_title_supply": {
    "method_version":"strict_multi_intitle_enumerated_v1",
    "query_syntax":"explicit_intitle_per_token_v1",
    "tokenizer_version":"nfkc_unicode_alnum_connectors_v1",
    "count_method":"paginated_deduplicated_organic_canonical_urls_with_displayed_title_integrity_audit",
    "require_all_assessable":true,
    "observation_artifact_sha256":"<sha of records>",
    "records":[
      {"keyword_id":"k1", "observation_id":"o1",
       "outcome":"exact_exhausted", "count":10,
       "reducer_policy_version":"verified_visible_title_lower_bound_v1",
       "operator_count":10, "verified_count":10,
       "lower_bound_basis":"verified_matching_unique_urls",
       "context":{"hl":"en","gl":"us","device":"desktop",
         "search_type":"google_web","pws":0,"filter":0,"nfpr":1,
         "checked_date":"2026-08-14"},
       "repeat_observations":[
         {"observation_id":"o1-repeat","outcome":"exact_exhausted","count":12,
          "reducer_policy_version":"verified_visible_title_lower_bound_v1",
          "operator_count":12, "verified_count":12,
          "lower_bound_basis":"verified_matching_unique_urls",
          "context":{"hl":"en","gl":"us","device":"desktop",
            "search_type":"google_web","pws":0,"filter":0,"nfpr":1,
            "checked_date":"2026-08-14"}}]}
    ]
  },
  "serp": {
    "sampling_plan_frozen":true,
    "sampling_plan_sha256":"<sha of plan_records>",
    "observation_artifact_sha256":"<sha of observation_records>",
    "plan_records":[{"plan_id":"p1","keyword_id":"k1"}],
    "observation_records":[
      {"plan_id":"p1","status":"pass",
       "context":{"market":"US","language":"en","device":"desktop",
         "search_type":"google_web","checked_date":"2026-08-14",
         "intent_group":"tool","page_type":"tool_page"}}
    ]
  }
}

Canonical metric statuses are complete/partial/unavailable/invalid/conflict.
Every row carries volume/kd/cpc as a non-negative number or null plus an exact
missing_fields ledger. Partial rows may retain an observed Volume while KD/CPC
remain missing. Strict eligibility is derived from complete/partial rows whose
observed Volume satisfies 0 < volume <= 250. A real zero remains an observed
value but is not eligible. Strict record IDs must equal that set exactly.

Threat boundary: inline SHA verification catches stale or accidentally divergent
summaries. It does not prevent an actor with write access from changing records
and recomputing their hashes; external immutable receipts are outside this gate.
"""

from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


class GateInputError(ValueError):
    pass


TITLE_SUPPLY_METHOD_VERSION = "strict_multi_intitle_enumerated_v1"
TITLE_SUPPLY_QUERY_SYNTAX = "explicit_intitle_per_token_v1"
TITLE_SUPPLY_TOKENIZER_VERSION = "nfkc_unicode_alnum_connectors_v1"
TITLE_SUPPLY_COUNT_METHOD = (
    "paginated_deduplicated_organic_canonical_urls_with_displayed_title_integrity_audit"
)
TITLE_SUPPLY_REDUCER_POLICY_VERSION = "verified_visible_title_lower_bound_v1"
TITLE_SUPPLY_LOWER_BOUND_BASIS = "verified_matching_unique_urls"
METRIC_FIELDS = ("volume", "kd", "cpc")
METRIC_STATUSES = {"complete", "partial", "unavailable", "invalid", "conflict"}
NOT_ASSESSABLE_OUTCOMES = {
    "not_assessable_missing_enumeration",
    "not_assessable_blocked",
    "not_assessable_query_integrity",
    "not_assessable_method_mismatch",
    "not_assessable_context_mismatch",
}
EXACT_BANDS = {
    "provisional_strong",
    "provisional_borderline",
    "provisional_high",
}


def records_sha256(records: list[dict[str, Any]]) -> str:
    """Return the artifact digest used by the inline-record contract."""

    encoded = json.dumps(
        records, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _strict_counts(
    row: dict[str, Any], location: str, outcome: str
) -> tuple[int, int, int]:
    """Validate one reducer observation and return count/operator/verified counts.

    ``count`` remains the compact downstream value, but under this policy it is
    always the verified visible-title count.  The larger operator result count
    is retained as provenance and can never satisfy an early-stop threshold.
    """

    if row.get("reducer_policy_version") != TITLE_SUPPLY_REDUCER_POLICY_VERSION:
        raise GateInputError(
            f"{location}.reducer_policy_version must equal "
            f"{TITLE_SUPPLY_REDUCER_POLICY_VERSION!r}"
        )
    if row.get("lower_bound_basis") != TITLE_SUPPLY_LOWER_BOUND_BASIS:
        raise GateInputError(
            f"{location}.lower_bound_basis must equal "
            f"{TITLE_SUPPLY_LOWER_BOUND_BASIS!r}"
        )
    values: dict[str, int] = {}
    for field in ("count", "operator_count", "verified_count"):
        value = row.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise GateInputError(f"{location}.{field} must be non-negative integer")
        values[field] = value
    if values["verified_count"] > values["operator_count"]:
        raise GateInputError(
            f"{location}.verified_count cannot exceed operator_count"
        )
    if values["count"] != values["verified_count"]:
        raise GateInputError(
            f"{location}.count must equal verified_count; operator_count cannot "
            "be used as the lower-bound count"
        )
    if outcome == "exact_exhausted" and (
        values["operator_count"] != values["verified_count"]
    ):
        raise GateInputError(
            f"{location} exact_exhausted requires v1 integrity pass: "
            "operator_count must equal verified_count"
        )
    return values["count"], values["operator_count"], values["verified_count"]


def _mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise GateInputError(f"{key} must be an object")
    return value


def _records(parent: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = parent.get(key)
    if not isinstance(value, list):
        raise GateInputError(f"{key} must be an array")
    if any(not isinstance(row, dict) for row in value):
        raise GateInputError(f"every {key} row must be an object")
    return value


def _identifier(row: dict[str, Any], key: str, location: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise GateInputError(f"{location}.{key} must be a non-empty string")
    return value


def _sha256(parent: dict[str, Any], key: str) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise GateInputError(f"{key} must be a lowercase SHA-256 hex digest")
    return value


def _unique_ids(
    records: list[dict[str, Any]], key: str, location: str
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(records):
        value = _identifier(row, key, f"{location}[{index}]")
        if value in indexed:
            raise GateInputError(f"duplicate {location}.{key}: {value}")
        indexed[value] = row
    return indexed


def _context_key(row: dict[str, Any], location: str) -> str:
    context = _mapping(row, "context")
    expected_keys = {
        "hl", "gl", "device", "search_type", "pws", "filter", "nfpr",
        "checked_date",
    }
    if set(context) != expected_keys:
        raise GateInputError(f"{location}.context must contain exactly {sorted(expected_keys)}")
    for key in ("hl", "gl"):
        if not isinstance(context[key], str) or not context[key].strip():
            raise GateInputError(f"{location}.context.{key} must be non-empty")
    fixed = {
        "device": "desktop",
        "search_type": "google_web",
        "pws": 0,
        "filter": 0,
        "nfpr": 1,
    }
    for key, expected in fixed.items():
        if context[key] != expected or type(context[key]) is not type(expected):
            raise GateInputError(f"{location}.context.{key} must equal {expected!r}")
    checked_date = context["checked_date"]
    if not isinstance(checked_date, str):
        raise GateInputError(f"{location}.context.checked_date must be an ISO date")
    try:
        dt.date.fromisoformat(checked_date)
    except ValueError as exc:
        raise GateInputError(
            f"{location}.context.checked_date must be an ISO date"
        ) from exc
    normalized = dict(context, hl=context["hl"].casefold(), gl=context["gl"].casefold())
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _iso_date(value: Any, location: str) -> str:
    if not isinstance(value, str):
        raise GateInputError(f"{location} must be an ISO date")
    try:
        dt.date.fromisoformat(value)
    except ValueError as exc:
        raise GateInputError(f"{location} must be an ISO date") from exc
    return value


def _metric_context(row: dict[str, Any], location: str) -> dict[str, str]:
    context = _mapping(row, "metric_context")
    expected = {"market", "language", "device", "provider", "match_type", "checked_date"}
    if set(context) != expected:
        raise GateInputError(f"{location}.metric_context must contain exactly {sorted(expected)}")
    normalized: dict[str, str] = {}
    for key in ("market", "language", "device", "provider", "match_type"):
        value = context[key]
        if not isinstance(value, str) or not value.strip():
            raise GateInputError(f"{location}.metric_context.{key} must be non-empty")
        normalized[key] = value.strip().casefold()
    normalized["checked_date"] = _iso_date(
        context["checked_date"], f"{location}.metric_context.checked_date"
    )
    return normalized


def _metric_values(row: dict[str, Any], keyword_id: str) -> dict[str, int | float | None]:
    """Validate normalized metric fields and their explicit missing ledger."""

    values: dict[str, int | float | None] = {}
    for field in METRIC_FIELDS:
        if field not in row:
            raise GateInputError(f"canonical row {keyword_id}.{field} is required")
        value = row[field]
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or (isinstance(value, float) and not math.isfinite(value))
            or value < 0
        ):
            raise GateInputError(
                f"canonical row {keyword_id}.{field} must be a non-negative number or null"
            )
        values[field] = value

    missing_fields = row.get("missing_fields")
    if not isinstance(missing_fields, list):
        raise GateInputError(
            f"canonical row {keyword_id}.missing_fields must be an array"
        )
    if any(field not in METRIC_FIELDS for field in missing_fields):
        raise GateInputError(
            f"canonical row {keyword_id}.missing_fields contains an unknown field"
        )
    if len(set(missing_fields)) != len(missing_fields):
        raise GateInputError(
            f"canonical row {keyword_id}.missing_fields contains duplicates"
        )
    expected_missing = {field for field, value in values.items() if value is None}
    if set(missing_fields) != expected_missing:
        raise GateInputError(
            f"canonical row {keyword_id}.missing_fields must exactly match null metric fields"
        )

    status = row["metric_status"]
    observed_count = len(METRIC_FIELDS) - len(expected_missing)
    if status == "complete" and observed_count != len(METRIC_FIELDS):
        raise GateInputError(
            f"canonical complete row {keyword_id} must observe volume, kd, and cpc"
        )
    if status == "partial" and not 0 < observed_count < len(METRIC_FIELDS):
        raise GateInputError(
            f"canonical partial row {keyword_id} must have both observed and missing fields"
        )
    if status == "unavailable" and observed_count != 0:
        raise GateInputError(
            f"canonical unavailable row {keyword_id} must have all metric fields null"
        )
    return values


def _serp_context(row: dict[str, Any], location: str) -> dict[str, str]:
    context = _mapping(row, "context")
    expected = {
        "market", "language", "device", "search_type", "checked_date",
        "intent_group", "page_type",
    }
    if set(context) != expected:
        raise GateInputError(f"{location}.context must contain exactly {sorted(expected)}")
    normalized: dict[str, str] = {}
    for key in ("market", "language", "device", "search_type", "intent_group", "page_type"):
        value = context[key]
        if not isinstance(value, str) or not value.strip():
            raise GateInputError(f"{location}.context.{key} must be non-empty")
        normalized[key] = value.strip().casefold()
    normalized["checked_date"] = _iso_date(
        context["checked_date"], f"{location}.context.checked_date"
    )
    if normalized["search_type"] != "google_web":
        raise GateInputError(f"{location}.context.search_type must equal 'google_web'")
    return normalized


def _derived_band(count: int, volume: int | float) -> str:
    ratio = count / volume
    if ratio < 0.25:
        return "provisional_strong"
    if ratio <= 0.30:
        return "provisional_borderline"
    return "provisional_high"


def _evaluate(summary: dict[str, Any]) -> dict[str, Any]:
    declared = summary.get("active_pool_declared")
    if not isinstance(declared, bool):
        raise GateInputError("active_pool_declared must be boolean")

    slate = _mapping(summary, "canonical_slate")
    strict = _mapping(summary, "strict_title_supply")
    serp = _mapping(summary, "serp")
    errors: list[str] = []

    canonical_records = _records(slate, "records")
    if not canonical_records:
        raise GateInputError("canonical_slate.records must not be empty")
    canonical_by_id = _unique_ids(canonical_records, "keyword_id", "canonical_slate.records")
    metric_counts: Counter[str] = Counter()
    metric_missing_field_counts: Counter[str] = Counter()
    family_by_keyword: dict[str, str] = {}
    lanes_by_keyword: dict[str, set[str]] = {}
    volume_by_keyword: dict[str, int | float] = {}
    all_families: set[str] = set()
    all_lanes: set[str] = set()
    eligible_ids: set[str] = set()
    narrow_families: set[str] = set()
    metric_contexts: dict[str, dict[str, str]] = {}
    for index, row in enumerate(canonical_records):
        keyword_id = _identifier(row, "keyword_id", f"canonical_slate.records[{index}]")
        family_id = _identifier(row, "family_id", f"canonical_slate.records[{index}]")
        status = row.get("metric_status")
        if status not in METRIC_STATUSES:
            raise GateInputError(f"canonical row {keyword_id} has invalid metric_status")
        lanes = row.get("lanes")
        if not isinstance(lanes, list) or not lanes:
            raise GateInputError(f"canonical row {keyword_id}.lanes must be non-empty array")
        if any(not isinstance(lane, str) or not lane.strip() for lane in lanes):
            raise GateInputError(f"canonical row {keyword_id} has invalid lane")
        if len(set(lanes)) != len(lanes):
            raise GateInputError(f"canonical row {keyword_id} has duplicate lanes")
        metric_values = _metric_values(row, keyword_id)
        metric_missing_field_counts.update(
            field for field, value in metric_values.items() if value is None
        )
        volume = metric_values["volume"]
        if status in {"complete", "partial"} and volume is not None:
            volume_by_keyword[keyword_id] = volume
            if 0 < volume <= 250:
                eligible_ids.add(keyword_id)
        metric_counts[status] += 1
        family_by_keyword[keyword_id] = family_id
        lanes_by_keyword[keyword_id] = set(lanes)
        all_families.add(family_id)
        all_lanes.update(lanes)
        if "narrow_product_value" in lanes:
            narrow_families.add(family_id)
        metric_context = _metric_context(row, f"canonical row {keyword_id}")
        metric_context_key = json.dumps(
            metric_context, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        metric_contexts[metric_context_key] = metric_context

    canonical_claimed_sha = _sha256(slate, "artifact_sha256")
    canonical_computed_sha = records_sha256(canonical_records)
    canonical_artifact_valid = canonical_claimed_sha == canonical_computed_sha
    if not canonical_artifact_valid:
        errors.append("canonical_slate artifact SHA does not match inline records")
    frozen = slate.get("frozen") is True
    if not frozen:
        errors.append("canonical slate is not frozen")
    metric_context_complete = len(metric_contexts) == 1
    if not metric_context_complete:
        errors.append("canonical metric records must use one complete compatible metric_context")
    metric_context = next(iter(metric_contexts.values())) if metric_context_complete else None

    method_valid = (
        strict.get("method_version") == TITLE_SUPPLY_METHOD_VERSION
        and strict.get("query_syntax") == TITLE_SUPPLY_QUERY_SYNTAX
        and strict.get("tokenizer_version") == TITLE_SUPPLY_TOKENIZER_VERSION
        and strict.get("count_method") == TITLE_SUPPLY_COUNT_METHOD
    )
    if not method_valid:
        errors.append("strict title-supply method/query/tokenizer/count contract mismatch")
    require_all_assessable = strict.get("require_all_assessable")
    if not isinstance(require_all_assessable, bool):
        raise GateInputError("strict_title_supply.require_all_assessable must be boolean")
    if not require_all_assessable:
        errors.append("strict_title_supply.require_all_assessable must be true")

    strict_records = _records(strict, "records")
    strict_by_id = _unique_ids(strict_records, "keyword_id", "strict_title_supply.records")
    strict_ids = set(strict_by_id)
    strict_ids_match = strict_ids == eligible_ids
    if not strict_ids_match:
        errors.append(
            "strict keyword IDs must exactly equal metric-derived 0<Volume<=250 eligible IDs"
        )
    outcome_counts: Counter[str] = Counter()
    band_counts: Counter[str] = Counter()
    strict_context_keys: set[str] = set()
    protected_families: set[str] = set()
    repeat_complete = True
    all_strict_observation_ids: set[str] = set()
    operator_total = 0
    verified_total = 0
    for keyword_id, row in strict_by_id.items():
        if "repeat_confirmed" in row:
            raise GateInputError(
                f"strict row {keyword_id} must use repeat_observations, not repeat_confirmed"
            )
        primary_observation_id = _identifier(
            row, "observation_id", f"strict row {keyword_id}"
        )
        if primary_observation_id in all_strict_observation_ids:
            raise GateInputError(
                f"duplicate strict observation_id: {primary_observation_id}"
            )
        all_strict_observation_ids.add(primary_observation_id)
        repeats = _records(row, "repeat_observations")
        if keyword_id not in eligible_ids:
            continue
        outcome = row.get("outcome")
        if outcome not in {"exact_exhausted", "lower_bound_gt_0_30", *NOT_ASSESSABLE_OUTCOMES}:
            raise GateInputError(f"strict row {keyword_id} has invalid outcome")
        count, operator_count, verified_count = _strict_counts(
            row, f"strict row {keyword_id}", outcome
        )
        operator_total += operator_count
        verified_total += verified_count
        primary_context_key = _context_key(row, f"strict row {keyword_id}")
        strict_context_keys.add(primary_context_key)
        outcome_counts[outcome] += 1
        volume = volume_by_keyword[keyword_id]
        primary_band: str | None = None
        if outcome == "exact_exhausted":
            primary_band = _derived_band(count, volume)
            band_counts[primary_band] += 1
            if primary_band in {"provisional_strong", "provisional_borderline"}:
                protected_families.add(family_by_keyword[keyword_id])
        elif outcome == "lower_bound_gt_0_30":
            threshold = math.floor(0.30 * volume) + 1
            if verified_count < threshold:
                raise GateInputError(
                    f"strict row {keyword_id} verified_count is below early-stop threshold"
                )
            band_counts["provisional_high"] += 1

        compatible_exact_repeat = False
        for repeat_index, repeat in enumerate(repeats):
            location = f"strict row {keyword_id}.repeat_observations[{repeat_index}]"
            repeat_id = _identifier(repeat, "observation_id", location)
            if repeat_id in all_strict_observation_ids:
                raise GateInputError(f"duplicate strict observation_id: {repeat_id}")
            all_strict_observation_ids.add(repeat_id)
            repeat_outcome = repeat.get("outcome")
            if repeat_outcome not in {
                "exact_exhausted", "lower_bound_gt_0_30", *NOT_ASSESSABLE_OUTCOMES
            }:
                raise GateInputError(f"{location}.outcome is invalid")
            _, _, repeat_verified_count = _strict_counts(
                repeat, location, repeat_outcome
            )
            repeat_context_key = _context_key(repeat, location)
            if repeat_context_key != primary_context_key:
                raise GateInputError(f"{location}.context must equal the primary context")
            if repeat_outcome == "lower_bound_gt_0_30":
                threshold = math.floor(0.30 * volume) + 1
                if repeat_verified_count < threshold:
                    raise GateInputError(
                        f"{location} verified_count is below early-stop threshold"
                    )
            if (
                repeat_outcome == "exact_exhausted"
                and repeat_verified_count / volume <= 0.30
            ):
                compatible_exact_repeat = True
        confirmation_required = (
            primary_band in {"provisional_strong", "provisional_borderline"}
            or count == 0
        )
        if confirmation_required and not compatible_exact_repeat:
            repeat_complete = False

    strict_claimed_sha = _sha256(strict, "observation_artifact_sha256")
    strict_computed_sha = records_sha256(strict_records)
    strict_artifact_valid = strict_claimed_sha == strict_computed_sha
    if not strict_artifact_valid:
        errors.append("strict title-supply artifact SHA does not match inline records")
    context_complete = len(strict_context_keys) == (1 if eligible_ids else 0)
    if not context_complete:
        errors.append("strict title-supply records must use exactly one complete query context")
    strict_metric_context_compatible = context_complete and metric_context_complete
    if eligible_ids and strict_metric_context_compatible:
        strict_context = json.loads(next(iter(strict_context_keys)))
        strict_metric_context_compatible = (
            strict_context["hl"] == metric_context["language"]
            and strict_context["gl"] == metric_context["market"]
            and strict_context["device"] == metric_context["device"]
        )
    if not eligible_ids:
        strict_metric_context_compatible = metric_context_complete
    if not strict_metric_context_compatible:
        errors.append(
            "strict title-supply hl/gl/device must match the canonical metric language/market/device"
        )
    not_assessable = sum(outcome_counts[name] for name in NOT_ASSESSABLE_OUTCOMES)
    assessability_complete = require_all_assessable and not_assessable == 0
    if not assessability_complete:
        errors.append("all strict-title eligible records must be assessable")
    if not repeat_complete:
        errors.append(
            "exact strong/borderline and primary zero-count observations require at least one same-context exact repeat at <=0.30"
        )

    plan_frozen = serp.get("sampling_plan_frozen") is True
    if not plan_frozen:
        errors.append("SERP sampling plan is not frozen")
    plan_records = _records(serp, "plan_records")
    observation_records = _records(serp, "observation_records")
    plan_by_id = _unique_ids(plan_records, "plan_id", "serp.plan_records")
    observation_by_id = _unique_ids(
        observation_records, "plan_id", "serp.observation_records"
    )
    plan_keyword_ids: set[str] = set()
    plan_families: set[str] = set()
    covered_lanes: set[str] = set()
    for plan_id, row in plan_by_id.items():
        keyword_id = _identifier(row, "keyword_id", f"SERP plan {plan_id}")
        if keyword_id not in canonical_by_id:
            raise GateInputError(f"SERP plan {plan_id} references unknown keyword_id")
        if keyword_id in plan_keyword_ids:
            raise GateInputError(f"SERP plan repeats keyword_id {keyword_id}")
        plan_keyword_ids.add(keyword_id)
        plan_families.add(family_by_keyword[keyword_id])
        covered_lanes.update(lanes_by_keyword[keyword_id])
    plan_observation_ids_match = set(plan_by_id) == set(observation_by_id)
    if not plan_observation_ids_match:
        errors.append("SERP plan IDs and observation IDs must match exactly")
    serp_status_counts: Counter[str] = Counter()
    serp_checked_dates: set[str] = set()
    serp_context_compatible = metric_context_complete
    for plan_id, row in observation_by_id.items():
        if "context_compatible" in row:
            raise GateInputError(
                f"SERP observation {plan_id} must provide context, not context_compatible"
            )
        status = row.get("status")
        if status not in {"pass", "hold", "fail"}:
            raise GateInputError(f"SERP observation {plan_id} has invalid status")
        serp_context = _serp_context(row, f"SERP observation {plan_id}")
        serp_checked_dates.add(serp_context["checked_date"])
        if metric_context is None or any(
            serp_context[key] != metric_context[key]
            for key in ("market", "language", "device")
        ):
            serp_context_compatible = False
        serp_status_counts[status] += 1
    serp_same_day = len(serp_checked_dates) == (1 if observation_records else 0)
    if not serp_same_day:
        errors.append("all SERP observations in the batch must share one checked_date")

    plan_claimed_sha = _sha256(serp, "sampling_plan_sha256")
    plan_computed_sha = records_sha256(plan_records)
    observation_claimed_sha = _sha256(serp, "observation_artifact_sha256")
    observation_computed_sha = records_sha256(observation_records)
    serp_artifacts_valid = (
        plan_claimed_sha == plan_computed_sha
        and observation_claimed_sha == observation_computed_sha
    )
    if plan_claimed_sha != plan_computed_sha:
        errors.append("SERP plan artifact SHA does not match inline records")
    if observation_claimed_sha != observation_computed_sha:
        errors.append("SERP observation artifact SHA does not match inline records")

    checked = len(observation_records)
    minimum_family_coverage = min(30, len(all_families))
    family_coverage_complete = (
        len(plan_families) >= minimum_family_coverage
        and protected_families.issubset(plan_families)
        and narrow_families.issubset(plan_families)
    )
    lane_coverage_complete = covered_lanes == all_lanes
    derived_bounds_valid = (
        len(plan_families) <= checked
        and len(plan_families) <= len(all_families)
        and len(covered_lanes) <= checked
        and len(covered_lanes) <= len(all_lanes)
    )
    if not family_coverage_complete:
        errors.append(
            "SERP plan must cover min(30,family_total), every strict strong/borderline family, and every narrow_product_value family"
        )
    if not lane_coverage_complete:
        errors.append("SERP plan must cover every non-empty canonical lane")
    if not derived_bounds_valid:
        errors.append("SERP derived family/lane counts exceed checked or canonical bounds")
    if not serp_context_compatible:
        errors.append(
            "every SERP observation market/language/device must match the metric cohort"
        )

    gates = {
        "CanonicalSlateFrozen": frozen and canonical_artifact_valid,
        "PrimaryMetricObservationCoverageComplete": metric_context_complete,
        "StrictTitleSupplyEligibleCoverageComplete": (
            method_valid
            and strict_artifact_valid
            and strict_ids_match
            and context_complete
            and strict_metric_context_compatible
            and assessability_complete
            and repeat_complete
        ),
        "RepresentativeSerpCoverageComplete": (
            plan_frozen
            and serp_artifacts_valid
            and plan_observation_ids_match
            and serp_context_compatible
            and serp_same_day
            and family_coverage_complete
            and lane_coverage_complete
            and derived_bounds_valid
        ),
    }
    active_pool_eligible = all(gates.values()) and not errors
    if declared and not active_pool_eligible:
        errors.append("active_pool_declared is forbidden while ActivePoolEligible=false")

    return {
        "ActivePoolEligible": active_pool_eligible,
        "gates": gates,
        "coverage": {
            "canonical_total": len(canonical_records),
            "canonical_family_total": len(all_families),
            "canonical_lane_set": sorted(all_lanes),
            "canonical_metric_status_counts": dict(sorted(metric_counts.items())),
            "canonical_metric_missing_field_counts": dict(
                sorted(metric_missing_field_counts.items())
            ),
            "canonical_metric_context_count": len(metric_contexts),
            "canonical_artifact_sha256_computed": canonical_computed_sha,
            "metric_derived_strict_eligible": len(eligible_ids),
            "strict_keyword_ids_match": strict_ids_match,
            "strict_outcome_counts": dict(sorted(outcome_counts.items())),
            "strict_band_counts": dict(sorted(band_counts.items())),
            "strict_operator_count_total": operator_total,
            "strict_verified_count_total": verified_total,
            "strict_context_count": len(strict_context_keys),
            "strict_metric_context_compatible": strict_metric_context_compatible,
            "strict_repeat_confirmation_complete": repeat_complete,
            "strict_artifact_sha256_computed": strict_computed_sha,
            "serp_plan_count": len(plan_records),
            "serp_checked": checked,
            "serp_status_counts": dict(sorted(serp_status_counts.items())),
            "serp_checked_date_count": len(serp_checked_dates),
            "serp_distinct_family_checked": len(plan_families),
            "serp_minimum_family_required": minimum_family_coverage,
            "serp_covered_lanes": sorted(covered_lanes),
            "serp_plan_sha256_computed": plan_computed_sha,
            "serp_observation_sha256_computed": observation_computed_sha,
        },
        "errors": errors,
    }


def evaluate(summary: dict[str, Any]) -> dict[str, Any]:
    """Return a fail-closed result for valid or structurally invalid input."""

    try:
        if not isinstance(summary, dict):
            raise GateInputError("top-level JSON must be an object")
        return _evaluate(summary)
    except GateInputError as exc:
        return {
            "ActivePoolEligible": False,
            "gates": {
                "CanonicalSlateFrozen": False,
                "PrimaryMetricObservationCoverageComplete": False,
                "StrictTitleSupplyEligibleCoverageComplete": False,
                "RepresentativeSerpCoverageComplete": False,
            },
            "coverage": {},
            "errors": [str(exc)],
        }


def _load(path: str) -> dict[str, Any]:
    if path == "-":
        raw = json.load(sys.stdin)
    else:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise GateInputError("top-level JSON must be an object")
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", help="stage summary JSON path, or '-' for stdin")
    args = parser.parse_args()
    try:
        result = evaluate(_load(args.summary))
    except (OSError, json.JSONDecodeError, GateInputError) as exc:
        result = {"ActivePoolEligible": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ActivePoolEligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
