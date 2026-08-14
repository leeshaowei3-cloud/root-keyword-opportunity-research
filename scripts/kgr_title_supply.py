#!/usr/bin/env python3
"""Reduce strict multi-intitle enumerations into title-supply observations.

This module does not fetch Google. It reduces page observations captured by an
authorized browser workflow and keeps classic KGR/allintitle data legacy-only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit, urlunsplit


SKILL_VERSION = "2.0.1"
METHOD_VERSION = "strict_multi_intitle_enumerated_v1"
QUERY_SYNTAX = "explicit_intitle_per_token_v1"
COUNT_METHOD = (
    "paginated_deduplicated_organic_canonical_urls_with_displayed_title_integrity_audit"
)
TOKENIZER_VERSION = "nfkc_unicode_alnum_connectors_v1"
HIGH_BOUNDARY = 0.30
TRACKING_QUERY_KEYS = {"gclid", "fbclid", "srsltid"}
TERMINAL_PAGINATION_EVIDENCE = {
    "explicit_no_results",
    "next_control_absent_after_terminal_page",
    "terminal_page_short_and_no_next",
}


class TitleSupplyObservationError(ValueError):
    """Raised when an observation cannot be interpreted safely."""


def _query_tokens(keyword: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", keyword or "")
    # Unicode letters/numbers form tokens. &, + and # survive only when attached
    # to an alphanumeric token; a standalone connector is never an operator.
    tokens = re.findall(
        r"[^\W_]+(?:[&+#]+[^\W_]+)*[+#]*",
        normalized,
        flags=re.UNICODE,
    )
    if not tokens:
        raise TitleSupplyObservationError("keyword must contain at least one token")
    return tokens


def _match_tokens(value: str) -> set[str]:
    try:
        return {token.casefold() for token in _query_tokens(value)}
    except TitleSupplyObservationError:
        return set()


def displayed_title_matches(keyword: str, displayed_title: str) -> bool:
    """Return true only when every normalized keyword token occurs in the title."""

    required = _match_tokens(keyword)
    observed = _match_tokens(displayed_title)
    return bool(required) and required.issubset(observed)


def displayed_title_looks_truncated(displayed_title: str) -> bool:
    """Detect common ASCII and Unicode visual truncation markers."""

    normalized = unicodedata.normalize("NFKC", displayed_title)
    if "..." in normalized:
        return True
    return any(
        "ELLIPSIS" in unicodedata.name(char, "")
        or "DOT LEADER" in unicodedata.name(char, "")
        for char in normalized
    )


def build_strict_query(keyword: str) -> str:
    """Return one quoted intitle operator per normalized semantic token."""

    return " ".join(
        f'intitle:"{token.replace(chr(34), chr(92) + chr(34))}"'
        for token in _query_tokens(keyword)
    )


def canonicalize_result_url(raw_url: str) -> str:
    """Normalize a final organic canonical URL for cross-page deduplication."""

    value = (raw_url or "").strip()
    parts = urlsplit(value)
    if parts.scheme.casefold() not in {"http", "https"} or not parts.hostname:
        raise TitleSupplyObservationError(
            f"canonical result URL must be an absolute HTTP(S) URL: {raw_url!r}"
        )
    scheme = parts.scheme.casefold()
    hostname = parts.hostname.casefold()
    port = parts.port
    if port is not None and not (
        (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    ):
        hostname = f"{hostname}:{port}"
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.casefold().startswith("utm_")
        and key.casefold() not in TRACKING_QUERY_KEYS
    ]
    query = urlencode(sorted(query_pairs), doseq=True)
    return urlunsplit((scheme, hostname, path, query, ""))


def _provisional_band(ratio: float) -> str:
    if ratio < 0.25:
        return "provisional_strong"
    if ratio <= HIGH_BOUNDARY:
        return "provisional_borderline"
    return "provisional_high"


def _query_context(observation: dict[str, Any]) -> dict[str, Any]:
    raw = observation.get("query_context")
    if not isinstance(raw, dict):
        raise TitleSupplyObservationError("query_context must be an object")
    hl = raw.get("hl")
    gl = raw.get("gl")
    checked_date = raw.get("checked_date")
    if not isinstance(hl, str) or not hl.strip():
        raise TitleSupplyObservationError("query_context.hl must be non-empty")
    if not isinstance(gl, str) or not gl.strip():
        raise TitleSupplyObservationError("query_context.gl must be non-empty")
    if not isinstance(checked_date, str):
        raise TitleSupplyObservationError("query_context.checked_date must be ISO date")
    try:
        dt.date.fromisoformat(checked_date)
    except ValueError as exc:
        raise TitleSupplyObservationError(
            "query_context.checked_date must be ISO date"
        ) from exc
    context = {
        "hl": hl.strip().casefold(),
        "gl": gl.strip().casefold(),
        "device": raw.get("device"),
        "search_type": raw.get("search_type"),
        "pws": raw.get("pws"),
        "filter": raw.get("filter"),
        "nfpr": raw.get("nfpr"),
        "checked_date": checked_date,
    }
    required_fixed = {
        "device": "desktop",
        "search_type": "google_web",
        "pws": 0,
        "filter": 0,
        "nfpr": 1,
    }
    for key, expected in required_fixed.items():
        if context[key] != expected or type(context[key]) is not type(expected):
            raise TitleSupplyObservationError(
                f"query_context.{key} must equal {expected!r}"
            )
    return context


def _require_bool(parent: dict[str, Any], key: str, label: str) -> bool:
    value = parent.get(key)
    if type(value) is not bool:
        raise TitleSupplyObservationError(f"{label}.{key} must be boolean")
    return value


def _single_query_value(parameters: dict[str, list[str]], key: str) -> str:
    values = parameters.get(key)
    if not isinstance(values, list) or len(values) != 1:
        raise TitleSupplyObservationError(f"page_url requires exactly one {key!r} value")
    return values[0]


def _validate_page_url(
    page_url: str,
    *,
    expected_query: str,
    context: dict[str, Any],
    page_number: int,
    page_size: int,
) -> None:
    parts = urlsplit(page_url)
    if parts.scheme.casefold() != "https" or parts.hostname not in {
        "google.com",
        "www.google.com",
    } or parts.path != "/search":
        raise TitleSupplyObservationError(
            f"page {page_number} URL must be a Google HTTPS /search URL"
        )
    parameters = parse_qs(parts.query, keep_blank_values=True)
    allowed_parameters = {"q", "hl", "gl", "pws", "filter", "nfpr", "start", "num"}
    unexpected = sorted(set(parameters) - allowed_parameters)
    if unexpected:
        raise TitleSupplyObservationError(
            f"page {page_number} URL contains unsupported search parameter(s): "
            + ", ".join(unexpected)
        )
    expected_values = {
        "q": expected_query,
        "hl": context["hl"],
        "gl": context["gl"],
        "pws": str(context["pws"]),
        "filter": str(context["filter"]),
        "nfpr": str(context["nfpr"]),
    }
    for key, expected in expected_values.items():
        actual = _single_query_value(parameters, key)
        if actual != expected:
            raise TitleSupplyObservationError(
                f"page {page_number} URL {key!r} does not match query context"
            )
    raw_start = parameters.get("start", ["0"])
    if len(raw_start) != 1:
        raise TitleSupplyObservationError(
            f"page {page_number} URL requires at most one start value"
        )
    try:
        start = int(raw_start[0])
    except ValueError as exc:
        raise TitleSupplyObservationError(
            f"page {page_number} URL start must be an integer"
        ) from exc
    expected_start = (page_number - 1) * page_size
    if start != expected_start:
        raise TitleSupplyObservationError(
            f"page {page_number} URL start={start} does not equal {expected_start}"
        )
    if "num" in parameters and _single_query_value(parameters, "num") != str(page_size):
        raise TitleSupplyObservationError(
            f"page {page_number} URL num does not equal page_size={page_size}"
        )


def _base_result(
    keyword: str, volume: int, query: str, context: dict[str, Any]
) -> dict[str, Any]:
    context_key = json.dumps(
        context, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    return {
        "Keyword": keyword,
        "Volume": volume,
        "SkillVersion": SKILL_VERSION,
        "TitleSupplyMethodVersion": METHOD_VERSION,
        "TitleSupplyTokenizerVersion": TOKENIZER_VERSION,
        "TitleSupplyQuerySyntax": QUERY_SYNTAX,
        "TitleSupplyQuery": query,
        "TitleSupplyCountMethod": COUNT_METHOD,
        "TitleSupplySource": "google_serp_paginated_organic_results",
        "TitleSupplyHL": context["hl"],
        "TitleSupplyGL": context["gl"],
        "TitleSupplyDevice": context["device"],
        "TitleSupplySearchType": context["search_type"],
        "TitleSupplyPws": context["pws"],
        "TitleSupplyFilter": context["filter"],
        "TitleSupplyNfpr": context["nfpr"],
        "TitleSupplyCheckedDate": context["checked_date"],
        "TitleSupplyQueryContextKey": context_key,
        "StrictTitleSupplyUniqueUrlCount": 0,
        "TitleSupplyPageCount": 0,
        "TitleSupplyExhausted": False,
        "TitleSupplyBlocked": False,
        "TitleSupplyCaptcha": False,
        "TitleSupplyQueryIntegrity": "pass",
        "TitleSupplyIntegrityIssueCount": 0,
        "TitleSupplyEarlyStopT": math.floor(HIGH_BOUNDARY * volume) + 1,
        "TitleSupplyCountStatus": "incomplete",
        "StrictTitleSupplyRatio": None,
        "StrictTitleSupplyRoutingBand": "not_assessable_incomplete",
    }


def _method_mismatch(
    result: dict[str, Any], observation: dict[str, Any]
) -> dict[str, Any]:
    result["TitleSupplyMethodVersion"] = observation.get("method_version")
    result["TitleSupplyTokenizerVersion"] = observation.get("tokenizer_version")
    result["TitleSupplyQuerySyntax"] = observation.get("query_syntax")
    result["TitleSupplyQuery"] = observation.get("query")
    result["TitleSupplyCountMethod"] = observation.get("count_method")
    result["TitleSupplyCountStatus"] = "legacy_reference_only"
    result["StrictTitleSupplyRoutingBand"] = "not_assessable_method_mismatch"
    return result


def evaluate_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Reduce ordered pages to exact, lower-bound, blocked, or incomplete state."""

    keyword = observation.get("keyword")
    volume = observation.get("volume")
    if not isinstance(keyword, str):
        raise TitleSupplyObservationError("keyword must be a string")
    if (
        isinstance(volume, bool)
        or not isinstance(volume, int)
        or not 0 < volume <= 250
    ):
        raise TitleSupplyObservationError("volume must be an integer in 1..250")
    expected_query = build_strict_query(keyword)
    query = observation.get("query", expected_query)
    context = _query_context(observation)
    result = _base_result(keyword, volume, expected_query, context)

    if observation.get("method_version") != METHOD_VERSION:
        return _method_mismatch(result, observation)
    if observation.get("query_syntax") != QUERY_SYNTAX:
        return _method_mismatch(result, observation)
    if observation.get("tokenizer_version") != TOKENIZER_VERSION:
        return _method_mismatch(result, observation)
    if observation.get("count_method") != COUNT_METHOD:
        return _method_mismatch(result, observation)
    if query != expected_query or str(query).lstrip().casefold().startswith("allintitle:"):
        return _method_mismatch(result, observation)

    page_size = observation.get("page_size")
    if isinstance(page_size, bool) or not isinstance(page_size, int) or page_size <= 0:
        raise TitleSupplyObservationError("page_size must be a positive integer")

    pages = observation.get("pages")
    if not isinstance(pages, list):
        raise TitleSupplyObservationError("pages must be an ordered array")

    unique_urls: set[str] = set()
    seen_page_urls: set[str] = set()
    seen_organic_page_sets: set[frozenset[str]] = set()
    threshold_count = math.floor(HIGH_BOUNDARY * volume) + 1
    for page_number, page in enumerate(pages, start=1):
        if not isinstance(page, dict):
            raise TitleSupplyObservationError(f"page {page_number} must be an object")
        result["TitleSupplyPageCount"] = page_number

        captcha = _require_bool(page, "captcha", f"page {page_number}")
        blocked = _require_bool(page, "blocked", f"page {page_number}")
        exhausted_flag = _require_bool(page, "exhausted", f"page {page_number}")
        _require_bool(page, "has_next_control", f"page {page_number}")

        if captcha or blocked:
            result["StrictTitleSupplyUniqueUrlCount"] = len(unique_urls)
            result["TitleSupplyBlocked"] = True
            result["TitleSupplyCaptcha"] = captcha
            result["TitleSupplyCountStatus"] = (
                "blocked_captcha" if result["TitleSupplyCaptcha"] else "blocked"
            )
            result["StrictTitleSupplyRoutingBand"] = "not_assessable_blocked"
            return result

        page_url = page.get("page_url")
        if not isinstance(page_url, str) or not page_url.strip():
            raise TitleSupplyObservationError(f"page {page_number} requires page_url")
        _validate_page_url(
            page_url,
            expected_query=expected_query,
            context=context,
            page_number=page_number,
            page_size=page_size,
        )
        canonical_page_url = canonicalize_result_url(page_url)
        if canonical_page_url in seen_page_urls:
            result["StrictTitleSupplyUniqueUrlCount"] = len(unique_urls)
            result["TitleSupplyBlocked"] = True
            result["TitleSupplyCountStatus"] = "blocked_same_page_loop"
            result["StrictTitleSupplyRoutingBand"] = "not_assessable_blocked"
            return result
        seen_page_urls.add(canonical_page_url)

        results = page.get("results")
        if not isinstance(results, list) or any(not isinstance(item, dict) for item in results):
            raise TitleSupplyObservationError(
                f"page {page_number} results must be an array of objects"
            )
        page_organic_urls: set[str] = set()
        page_organic_card_count = 0
        for item in results:
            organic_flag = item.get("organic")
            if type(organic_flag) is not bool:
                raise TitleSupplyObservationError(
                    f"page {page_number} result organic must be boolean"
                )
            result_type = item.get("result_type")
            if not isinstance(result_type, str):
                raise TitleSupplyObservationError(
                    f"page {page_number} result result_type must be string"
                )
            for optional_flag in ("title_unknown", "title_truncated"):
                if optional_flag in item and type(item[optional_flag]) is not bool:
                    raise TitleSupplyObservationError(
                        f"page {page_number} result {optional_flag} must be boolean"
                    )
            if not organic_flag or result_type != "organic":
                continue
            page_organic_card_count += 1
            displayed_title = item.get("displayed_title")
            canonical_url = item.get("canonical_url")
            if not isinstance(canonical_url, str):
                raise TitleSupplyObservationError(
                    f"page {page_number} organic results require canonical_url"
                )
            # The operator result URL belongs to the enumerated supply count.
            # Displayed-title inspection is a whole-observation integrity audit,
            # not a filter that may silently lower that count.
            normalized_result_url = canonicalize_result_url(canonical_url)
            unique_urls.add(normalized_result_url)
            page_organic_urls.add(normalized_result_url)
            title_unknown = (
                not isinstance(displayed_title, str)
                or not displayed_title.strip()
                or item.get("title_unknown") is True
                or item.get("title_integrity") in {"unknown", "unverifiable"}
            )
            title_truncated = item.get("title_truncated") is True or (
                isinstance(displayed_title, str)
                and displayed_title_looks_truncated(displayed_title)
            )
            title_matches = (
                False
                if title_unknown
                else displayed_title_matches(keyword, displayed_title)
            )
            if title_unknown or title_truncated or not title_matches:
                result["TitleSupplyQueryIntegrity"] = "hold"
                result["TitleSupplyIntegrityIssueCount"] += 1

        page_fingerprint = frozenset(page_organic_urls)
        if page_fingerprint and page_fingerprint in seen_organic_page_sets:
            result["StrictTitleSupplyUniqueUrlCount"] = len(unique_urls)
            result["TitleSupplyBlocked"] = True
            result["TitleSupplyCountStatus"] = "blocked_same_results_loop"
            result["StrictTitleSupplyRoutingBand"] = "not_assessable_blocked"
            return result
        if page_fingerprint:
            seen_organic_page_sets.add(page_fingerprint)

        result["StrictTitleSupplyUniqueUrlCount"] = len(unique_urls)
        if result["TitleSupplyQueryIntegrity"] == "hold":
            result["TitleSupplyCountStatus"] = "query_integrity_hold"
            result["StrictTitleSupplyRoutingBand"] = (
                "not_assessable_query_integrity"
            )
            return result
        if exhausted_flag:
            pagination_state = page.get("pagination_state")
            terminal_evidence = page.get("end_of_results_evidence")
            has_next_control = page.get("has_next_control")
            if (
                pagination_state != "end_of_results"
                or terminal_evidence not in TERMINAL_PAGINATION_EVIDENCE
                or has_next_control is not False
            ):
                result["TitleSupplyBlocked"] = True
                result["TitleSupplyCountStatus"] = "not_assessable_terminal_evidence"
                result["StrictTitleSupplyRoutingBand"] = "not_assessable_blocked"
                return result
            if terminal_evidence == "explicit_no_results" and page_organic_card_count:
                result["TitleSupplyBlocked"] = True
                result["TitleSupplyCountStatus"] = "not_assessable_terminal_evidence"
                result["StrictTitleSupplyRoutingBand"] = "not_assessable_blocked"
                return result
            if terminal_evidence == "terminal_page_short_and_no_next":
                if "expected_page_size" in page and page.get("expected_page_size") != page_size:
                    result["TitleSupplyBlocked"] = True
                    result["TitleSupplyCountStatus"] = "not_assessable_terminal_evidence"
                    result["StrictTitleSupplyRoutingBand"] = "not_assessable_blocked"
                    return result
                # Terminal-page shortness is a property of displayed cards, not
                # of the deduplicated numerator. Repeated canonical URLs still
                # occupy separate result slots on the page.
                if page_organic_card_count >= page_size:
                    result["TitleSupplyBlocked"] = True
                    result["TitleSupplyCountStatus"] = "not_assessable_terminal_evidence"
                    result["StrictTitleSupplyRoutingBand"] = "not_assessable_blocked"
                    return result
            ratio = len(unique_urls) / volume
            result["TitleSupplyExhausted"] = True
            result["TitleSupplyCountStatus"] = "exact_exhausted"
            result["StrictTitleSupplyRatio"] = ratio
            result["StrictTitleSupplyRoutingBand"] = _provisional_band(ratio)
            return result
        if len(unique_urls) >= threshold_count:
            result["TitleSupplyCountStatus"] = "lower_bound_gt_0_30"
            result["StrictTitleSupplyRoutingBand"] = "provisional_high"
            return result

    return result


def _load(path: str) -> dict[str, Any]:
    if path == "-":
        payload = json.load(sys.stdin)
    else:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TitleSupplyObservationError("top-level JSON must be an object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    query_parser = subparsers.add_parser("query", help="build the strict multi-intitle query")
    query_parser.add_argument("keyword")
    evaluate_parser = subparsers.add_parser("evaluate", help="reduce a saved page observation")
    evaluate_parser.add_argument("observation", help="JSON path, or '-' for stdin")
    args = parser.parse_args()
    try:
        if args.command == "query":
            print(build_strict_query(args.keyword))
            return 0
        result = evaluate_observation(_load(args.observation))
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["TitleSupplyCountStatus"] in {
            "exact_exhausted",
            "lower_bound_gt_0_30",
        } else 2
    except (OSError, json.JSONDecodeError, TitleSupplyObservationError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
