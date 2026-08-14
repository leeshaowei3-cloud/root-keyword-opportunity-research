#!/usr/bin/env python3
"""Validate the denominator gates required before declaring an active pool.

Input is a JSON file (or '-' for stdin) with this minimum shape:

{
  "active_pool_declared": false,
  "canonical_slate": {
    "frozen": true,
    "total": 355,
    "metric_valid": 300,
    "metric_missing": 20,
    "metric_unavailable": 25,
    "metric_invalid": 5,
    "metric_conflict": 5
  },
  "kgr": {
    "eligible": 120,
    "checked_numeric": 115,
    "strong": 8,
    "borderline": 4,
    "secondary": 23,
    "no_advantage": 80,
    "not_assessable_missing_intitle": 5
  },
  "serp": {"representative_required": 42, "representative_checked": 42}
}

Coverage means every denominator has an explicit outcome. It does not convert a
missing metric or unavailable allintitle count into zero.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class GateInputError(ValueError):
    pass


def _mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise GateInputError(f"{key} must be an object")
    return value


def _count(parent: dict[str, Any], key: str) -> int:
    value = parent.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise GateInputError(f"{key} must be a non-negative integer")
    return value


def evaluate(summary: dict[str, Any]) -> dict[str, Any]:
    slate = _mapping(summary, "canonical_slate")
    kgr = _mapping(summary, "kgr")
    serp = _mapping(summary, "serp")

    frozen = slate.get("frozen") is True
    total = _count(slate, "total")
    metric_keys = (
        "metric_valid",
        "metric_missing",
        "metric_unavailable",
        "metric_invalid",
        "metric_conflict",
    )
    metric_counts = {key: _count(slate, key) for key in metric_keys}
    metric_outcomes = sum(metric_counts.values())
    metric_conserved = metric_outcomes == total

    eligible = _count(kgr, "eligible")
    checked_numeric = _count(kgr, "checked_numeric")
    band_keys = ("strong", "borderline", "secondary", "no_advantage")
    band_counts = {key: _count(kgr, key) for key in band_keys}
    band_conserved = sum(band_counts.values()) == checked_numeric
    not_assessable = _count(kgr, "not_assessable_missing_intitle")
    kgr_outcomes_conserved = checked_numeric + not_assessable == eligible
    kgr_within_metrics = eligible <= metric_counts["metric_valid"]
    kgr_coverage_complete = (
        band_conserved and kgr_outcomes_conserved and kgr_within_metrics
    )

    serp_required = _count(serp, "representative_required")
    serp_checked = _count(serp, "representative_checked")
    serp_complete = serp_checked >= serp_required

    gates = {
        "CanonicalSlateFrozen": frozen,
        "PrimaryMetricObservationCoverageComplete": metric_conserved,
        "KgrEligibleCoverageComplete": kgr_coverage_complete,
        "RepresentativeSerpCoverageComplete": serp_complete,
    }
    active_pool_eligible = all(gates.values())
    declared = summary.get("active_pool_declared") is True

    errors: list[str] = []
    if not frozen:
        errors.append("canonical slate is not frozen")
    if not metric_conserved:
        errors.append(
            f"metric outcomes {metric_outcomes} do not conserve canonical total {total}"
        )
    if not band_conserved:
        errors.append("KGR band counts do not conserve checked_numeric")
    if not kgr_outcomes_conserved:
        errors.append("numeric and not-assessable KGR outcomes do not conserve eligible")
    if not kgr_within_metrics:
        errors.append("KGR eligible exceeds metric_valid")
    if not serp_complete:
        errors.append(
            f"representative SERP coverage {serp_checked}/{serp_required} is incomplete"
        )
    if declared and not active_pool_eligible:
        errors.append("active_pool_declared is forbidden while ActivePoolEligible=false")

    return {
        "ActivePoolEligible": active_pool_eligible,
        "gates": gates,
        "coverage": {
            "canonical_total": total,
            "metric_outcomes": metric_outcomes,
            "kgr_eligible": eligible,
            "kgr_checked_numeric": checked_numeric,
            "kgr_not_assessable_missing_intitle": not_assessable,
            "serp_required": serp_required,
            "serp_checked": serp_checked,
        },
        "errors": errors,
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
        print(json.dumps({"ActivePoolEligible": False, "errors": [str(exc)]}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ActivePoolEligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
