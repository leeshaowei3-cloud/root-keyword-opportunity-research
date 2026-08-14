import unittest

from scripts.validate_stage_gate import evaluate, records_sha256


def context():
    return {
        "hl": "en", "gl": "us", "device": "desktop",
        "search_type": "google_web", "pws": 0, "filter": 0, "nfpr": 1,
        "checked_date": "2026-08-14",
    }


def metric_context():
    return {
        "market": "US", "language": "en", "device": "desktop",
        "provider": "semrush", "match_type": "exact",
        "checked_date": "2026-08-14",
    }


def serp_context():
    return {
        "market": "US", "language": "en", "device": "desktop",
        "search_type": "google_web", "checked_date": "2026-08-14",
        "intent_group": "tool", "page_type": "tool_page",
    }


def rehash(summary, *sections):
    if not sections or "canonical" in sections:
        records = summary["canonical_slate"]["records"]
        summary["canonical_slate"]["artifact_sha256"] = records_sha256(records)
    if not sections or "strict" in sections:
        records = summary["strict_title_supply"]["records"]
        summary["strict_title_supply"]["observation_artifact_sha256"] = records_sha256(records)
    if not sections or "serp" in sections:
        serp = summary["serp"]
        serp["sampling_plan_sha256"] = records_sha256(serp["plan_records"])
        serp["observation_artifact_sha256"] = records_sha256(serp["observation_records"])


def valid_summary():
    lanes = {
        1: ["strict_title_supply_longtail"], 2: ["strict_title_supply_longtail"],
        3: ["scale_search"], 4: ["emerging_search"],
        5: ["strict_title_supply_longtail"], 6: ["scale_search"],
        7: ["strict_title_supply_longtail"], 8: ["scale_search"],
        9: ["narrow_product_value"], 10: ["scale_search"],
    }
    canonical = []
    for index in range(1, 21):
        family_number = index if index <= 10 else index - 10
        canonical.append({
            "keyword_id": f"k{index}",
            "family_id": f"f{family_number}",
            "metric_status": "complete",
            "volume": 100 if index <= 8 else 500,
            "kd": 20,
            "cpc": 1.25,
            "missing_fields": [],
            "lanes": lanes[family_number],
            "metric_context": metric_context(),
        })
    counts = [10, 25, 40, 40, 40, 40, 31, 31]
    outcomes = ["exact_exhausted"] * 6 + ["lower_bound_gt_0_30"] * 2
    strict = [
        {
            "keyword_id": f"k{index}", "observation_id": f"o{index}",
            "outcome": outcomes[index - 1], "count": counts[index - 1],
            "reducer_policy_version": "verified_visible_title_lower_bound_v1",
            "operator_count": counts[index - 1],
            "verified_count": counts[index - 1],
            "lower_bound_basis": "verified_matching_unique_urls",
            "context": context(),
            "repeat_observations": ([{
                "observation_id": f"r{index}", "outcome": "exact_exhausted",
                "count": 12 if index == 1 else 28,
                "reducer_policy_version": "verified_visible_title_lower_bound_v1",
                "operator_count": 12 if index == 1 else 28,
                "verified_count": 12 if index == 1 else 28,
            "lower_bound_basis": "verified_matching_unique_urls",
                "context": context(),
            }] if index <= 2 else []),
        }
        for index in range(1, 9)
    ]
    plans = [{"plan_id": f"p{i}", "keyword_id": f"k{i}"} for i in range(1, 11)]
    observations = [
        {"plan_id": f"p{i}", "status": ("pass", "hold", "fail")[i % 3],
         "context": serp_context()}
        for i in range(1, 11)
    ]
    summary = {
        "active_pool_declared": True,
        "canonical_slate": {"frozen": True, "records": canonical},
        "strict_title_supply": {
            "method_version": "strict_multi_intitle_enumerated_v1",
            "query_syntax": "explicit_intitle_per_token_v1",
            "tokenizer_version": "nfkc_unicode_alnum_connectors_v1",
            "count_method": "paginated_deduplicated_organic_canonical_urls_with_displayed_title_integrity_audit",
            "require_all_assessable": True,
            "records": strict,
        },
        "serp": {
            "sampling_plan_frozen": True,
            "plan_records": plans,
            "observation_records": observations,
        },
    }
    rehash(summary)
    return summary


class StageGateInlineEvidenceTest(unittest.TestCase):
    def assert_blocked(self, summary, fragment=None):
        result = evaluate(summary)
        self.assertFalse(result["ActivePoolEligible"])
        self.assertTrue(result["errors"])
        if fragment:
            self.assertTrue(any(fragment in error for error in result["errors"]), result)

    def test_valid_inline_evidence_passes_and_derives_counts(self):
        result = evaluate(valid_summary())
        self.assertTrue(result["ActivePoolEligible"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["coverage"]["canonical_total"], 20)
        self.assertEqual(result["coverage"]["canonical_family_total"], 10)
        self.assertEqual(result["coverage"]["metric_derived_strict_eligible"], 8)
        self.assertEqual(result["coverage"]["strict_band_counts"]["provisional_strong"], 1)

    def test_active_pool_declared_must_be_strict_boolean(self):
        summary = valid_summary()
        summary["active_pool_declared"] = 1
        self.assert_blocked(summary, "must be boolean")

    def test_aggregate_self_reports_cannot_override_rows(self):
        summary = valid_summary()
        summary["canonical_slate"].update(total=1, family_total=1, metric_valid=1)
        summary["strict_title_supply"].update(eligible=1, exact_checked=1)
        summary["serp"].update(representative_required=1, representative_checked=1)
        result = evaluate(summary)
        self.assertTrue(result["ActivePoolEligible"])
        self.assertEqual(result["coverage"]["canonical_total"], 20)

    def test_artifact_sha_is_recomputed(self):
        summary = valid_summary()
        summary["canonical_slate"]["records"][0]["volume"] = 101
        self.assert_blocked(summary, "artifact SHA")

    def test_strict_artifact_sha_is_recomputed(self):
        summary = valid_summary()
        row = summary["strict_title_supply"]["records"][0]
        row.update(count=11, operator_count=11, verified_count=11)
        self.assert_blocked(summary, "artifact SHA")

    def test_strict_reducer_policy_fields_are_required(self):
        for field in (
            "reducer_policy_version", "operator_count", "verified_count",
            "lower_bound_basis",
        ):
            with self.subTest(field=field):
                summary = valid_summary()
                del summary["strict_title_supply"]["records"][2][field]
                rehash(summary, "strict")
                self.assert_blocked(summary, field)

    def test_operator_count_cannot_impersonate_verified_lower_bound(self):
        summary = valid_summary()
        row = summary["strict_title_supply"]["records"][6]
        row.update(operator_count=31, verified_count=30, count=31)
        rehash(summary, "strict")
        self.assert_blocked(summary, "count must equal verified_count")

    def test_verified_count_at_threshold_passes_lower_bound_gate(self):
        summary = valid_summary()
        row = summary["strict_title_supply"]["records"][6]
        row.update(operator_count=40, verified_count=31, count=31)
        rehash(summary, "strict")
        result = evaluate(summary)
        self.assertTrue(result["ActivePoolEligible"], result)

    def test_operator_at_threshold_but_verified_below_threshold_fails(self):
        summary = valid_summary()
        row = summary["strict_title_supply"]["records"][6]
        row.update(operator_count=31, verified_count=30, count=30)
        rehash(summary, "strict")
        self.assert_blocked(summary, "verified_count is below early-stop threshold")

    def test_verified_count_cannot_exceed_operator_count(self):
        summary = valid_summary()
        row = summary["strict_title_supply"]["records"][6]
        row.update(operator_count=30, verified_count=31, count=31)
        rehash(summary, "strict")
        self.assert_blocked(summary, "cannot exceed operator_count")

    def test_exact_low_requires_v1_integrity_count_equality(self):
        summary = valid_summary()
        row = summary["strict_title_supply"]["records"][2]
        row.update(operator_count=41, verified_count=40, count=40)
        rehash(summary, "strict")
        self.assert_blocked(summary, "v1 integrity pass")

    def test_serp_artifact_sha_is_recomputed(self):
        summary = valid_summary()
        summary["serp"]["observation_records"][0]["status"] = "fail"
        self.assert_blocked(summary, "artifact SHA")

    def test_strict_ids_must_exactly_equal_metric_eligible_ids(self):
        summary = valid_summary()
        summary["strict_title_supply"]["records"].pop()
        rehash(summary, "strict")
        self.assert_blocked(summary, "exactly equal")

    def test_duplicate_keyword_id_is_structural_failure(self):
        summary = valid_summary()
        summary["canonical_slate"]["records"][1]["keyword_id"] = "k1"
        rehash(summary, "canonical")
        self.assert_blocked(summary, "duplicate")

    def test_wrong_method_cannot_pass(self):
        summary = valid_summary()
        summary["strict_title_supply"]["method_version"] = "classic_kgr"
        self.assert_blocked(summary, "contract mismatch")

    def test_wrong_tokenizer_contract_cannot_pass(self):
        summary = valid_summary()
        summary["strict_title_supply"]["tokenizer_version"] = "legacy_tokenizer"
        self.assert_blocked(summary, "contract mismatch")

    def test_multiple_contexts_cannot_pass(self):
        summary = valid_summary()
        row = summary["strict_title_supply"]["records"][1]
        row["context"]["gl"] = "gb"
        row["repeat_observations"][0]["context"]["gl"] = "gb"
        rehash(summary, "strict")
        self.assert_blocked(summary, "exactly one complete query context")

    def test_uniform_strict_context_must_match_metric_cohort(self):
        summary = valid_summary()
        for row in summary["strict_title_supply"]["records"]:
            row["context"]["hl"] = "fr"
            row["context"]["gl"] = "gb"
            for repeat in row["repeat_observations"]:
                repeat["context"]["hl"] = "fr"
                repeat["context"]["gl"] = "gb"
        rehash(summary, "strict")
        result = evaluate(summary)
        self.assertFalse(result["ActivePoolEligible"])
        self.assertFalse(
            result["gates"]["StrictTitleSupplyEligibleCoverageComplete"]
        )
        self.assertFalse(
            result["coverage"]["strict_metric_context_compatible"]
        )
        self.assertTrue(
            any("must match the canonical metric" in error for error in result["errors"])
        )

    def test_metric_context_must_be_single_compatible_cohort(self):
        summary = valid_summary()
        summary["canonical_slate"]["records"][0]["metric_context"]["market"] = "GB"
        rehash(summary, "canonical")
        result = evaluate(summary)
        self.assertFalse(result["ActivePoolEligible"])
        self.assertFalse(result["gates"]["PrimaryMetricObservationCoverageComplete"])
        self.assertTrue(any("compatible metric_context" in error for error in result["errors"]))

    def test_metric_context_date_must_be_iso(self):
        summary = valid_summary()
        summary["canonical_slate"]["records"][0]["metric_context"]["checked_date"] = "today"
        rehash(summary, "canonical")
        self.assert_blocked(summary, "must be an ISO date")

    def test_all_missing_outcomes_cannot_pass(self):
        summary = valid_summary()
        for row in summary["strict_title_supply"]["records"]:
            row["outcome"] = "not_assessable_missing_enumeration"
            row.update(count=0, operator_count=0, verified_count=0)
        rehash(summary, "strict")
        self.assert_blocked(summary, "must be assessable")

    def test_require_all_assessable_cannot_be_disabled(self):
        summary = valid_summary()
        summary["strict_title_supply"]["require_all_assessable"] = False
        self.assert_blocked(summary, "must be true")

    def test_strong_or_borderline_exact_requires_repeat_confirmation(self):
        summary = valid_summary()
        summary["strict_title_supply"]["records"][0]["repeat_observations"] = []
        rehash(summary, "strict")
        self.assert_blocked(summary, "same-context exact repeat at <=0.30")

    def test_zero_exact_requires_repeat_confirmation(self):
        summary = valid_summary()
        row = summary["strict_title_supply"]["records"][2]
        row.update(count=0, operator_count=0, verified_count=0)
        row["repeat_observations"] = []
        rehash(summary, "strict")
        self.assert_blocked(summary, "same-context exact repeat at <=0.30")

    def test_repeat_above_point_thirty_does_not_confirm(self):
        summary = valid_summary()
        repeat = summary["strict_title_supply"]["records"][0]["repeat_observations"][0]
        repeat.update(count=31, operator_count=31, verified_count=31)
        rehash(summary, "strict")
        self.assert_blocked(summary, "same-context exact repeat at <=0.30")

    def test_repeat_observation_ids_are_globally_unique(self):
        summary = valid_summary()
        summary["strict_title_supply"]["records"][1]["repeat_observations"][0]["observation_id"] = "r1"
        rehash(summary, "strict")
        self.assert_blocked(summary, "duplicate strict observation_id")

    def test_repeat_confirmed_boolean_is_rejected(self):
        summary = valid_summary()
        summary["strict_title_supply"]["records"][0]["repeat_confirmed"] = True
        rehash(summary, "strict")
        self.assert_blocked(summary, "not repeat_confirmed")

    def test_required_one_serp_bypass_is_ignored(self):
        summary = valid_summary()
        summary["serp"]["plan_records"] = summary["serp"]["plan_records"][:1]
        summary["serp"]["observation_records"] = summary["serp"]["observation_records"][:1]
        summary["serp"]["representative_required"] = 1
        rehash(summary, "serp")
        self.assert_blocked(summary, "min(30,family_total)")

    def test_serp_plan_and_observation_ids_must_match_exactly(self):
        summary = valid_summary()
        summary["serp"]["observation_records"][0]["plan_id"] = "other"
        rehash(summary, "serp")
        self.assert_blocked(summary, "match exactly")

    def test_serp_must_cover_protected_family(self):
        summary = valid_summary()
        summary["serp"]["plan_records"][1]["keyword_id"] = "k11"
        rehash(summary, "serp")
        self.assert_blocked(summary, "strong/borderline family")

    def test_serp_must_cover_narrow_family(self):
        summary = valid_summary()
        summary["serp"]["plan_records"][8]["keyword_id"] = "k20"
        rehash(summary, "serp")
        self.assert_blocked(summary, "narrow_product_value")

    def test_serp_must_cover_every_lane(self):
        summary = valid_summary()
        summary["canonical_slate"]["records"][19]["lanes"] = ["new_lane"]
        rehash(summary, "canonical")
        self.assert_blocked(summary, "every non-empty canonical lane")

    def test_serp_context_must_be_compatible(self):
        summary = valid_summary()
        summary["serp"]["observation_records"][0]["context"]["market"] = "GB"
        rehash(summary, "serp")
        self.assert_blocked(summary, "must match the metric cohort")

    def test_serp_observations_must_share_one_date(self):
        summary = valid_summary()
        summary["serp"]["observation_records"][0]["context"]["checked_date"] = "2026-08-13"
        rehash(summary, "serp")
        self.assert_blocked(summary, "share one checked_date")

    def test_serp_intent_and_page_type_must_be_nonempty(self):
        summary = valid_summary()
        summary["serp"]["observation_records"][0]["context"]["intent_group"] = ""
        rehash(summary, "serp")
        self.assert_blocked(summary, "intent_group must be non-empty")

    def test_serp_context_compatible_boolean_is_rejected(self):
        summary = valid_summary()
        summary["serp"]["observation_records"][0]["context_compatible"] = True
        rehash(summary, "serp")
        self.assert_blocked(summary, "must provide context")

    def test_lane_count_cannot_exceed_checked(self):
        summary = valid_summary()
        summary["serp"]["plan_records"] = summary["serp"]["plan_records"][:1]
        summary["serp"]["observation_records"] = summary["serp"]["observation_records"][:1]
        summary["canonical_slate"]["records"][0]["lanes"] = ["a", "b"]
        rehash(summary)
        self.assert_blocked(summary, "exceed checked")

    def test_partial_with_volume_and_missing_kd_cpc_remains_strict_eligible(self):
        summary = valid_summary()
        row = summary["canonical_slate"]["records"][0]
        row.update(
            metric_status="partial",
            kd=None,
            cpc=None,
            missing_fields=["kd", "cpc"],
        )
        rehash(summary, "canonical")
        result = evaluate(summary)
        self.assertTrue(result["ActivePoolEligible"], result)
        self.assertEqual(result["coverage"]["metric_derived_strict_eligible"], 8)
        self.assertEqual(
            result["coverage"]["canonical_metric_status_counts"],
            {"complete": 19, "partial": 1},
        )
        self.assertEqual(
            result["coverage"]["canonical_metric_missing_field_counts"],
            {"cpc": 1, "kd": 1},
        )

    def test_explicit_unavailable_metrics_preserve_row_coverage(self):
        summary = valid_summary()
        row = summary["canonical_slate"]["records"][19]
        row.update(
            metric_status="unavailable",
            volume=None,
            kd=None,
            cpc=None,
            missing_fields=["volume", "kd", "cpc"],
        )
        rehash(summary, "canonical")
        result = evaluate(summary)
        self.assertTrue(result["ActivePoolEligible"], result)
        self.assertTrue(
            result["gates"]["PrimaryMetricObservationCoverageComplete"]
        )
        self.assertEqual(
            result["coverage"]["canonical_metric_status_counts"],
            {"complete": 19, "unavailable": 1},
        )
        self.assertEqual(
            result["coverage"]["canonical_metric_missing_field_counts"],
            {"cpc": 1, "kd": 1, "volume": 1},
        )

    def test_missing_fields_must_exactly_match_null_values(self):
        summary = valid_summary()
        row = summary["canonical_slate"]["records"][0]
        row.update(
            metric_status="partial",
            kd=None,
            cpc=0,
            missing_fields=["kd", "cpc"],
        )
        rehash(summary, "canonical")
        self.assert_blocked(summary, "must exactly match null metric fields")

    def test_partial_requires_both_observed_and_missing_fields(self):
        summary = valid_summary()
        row = summary["canonical_slate"]["records"][0]
        row.update(metric_status="partial", missing_fields=[])
        rehash(summary, "canonical")
        self.assert_blocked(summary, "must have both observed and missing fields")

    def test_real_zero_volume_is_preserved_but_not_strict_eligible(self):
        summary = valid_summary()
        summary["canonical_slate"]["records"][7]["volume"] = 0
        summary["strict_title_supply"]["records"] = [
            row
            for row in summary["strict_title_supply"]["records"]
            if row["keyword_id"] != "k8"
        ]
        rehash(summary, "canonical", "strict")
        result = evaluate(summary)
        self.assertTrue(result["ActivePoolEligible"], result)
        self.assertEqual(result["coverage"]["metric_derived_strict_eligible"], 7)

    def test_missing_volume_cannot_be_encoded_as_zero(self):
        summary = valid_summary()
        row = summary["canonical_slate"]["records"][0]
        row.update(
            metric_status="partial",
            volume=0,
            missing_fields=["volume"],
        )
        rehash(summary, "canonical")
        self.assert_blocked(summary, "must exactly match null metric fields")

    def test_legacy_valid_metric_status_is_rejected(self):
        summary = valid_summary()
        summary["canonical_slate"]["records"][0]["metric_status"] = "valid"
        rehash(summary, "canonical")
        self.assert_blocked(summary, "invalid metric_status")

    def test_active_true_never_coexists_with_errors(self):
        candidates = [valid_summary()]
        broken = valid_summary()
        broken["serp"]["sampling_plan_frozen"] = False
        candidates.append(broken)
        for summary in candidates:
            result = evaluate(summary)
            self.assertFalse(result["ActivePoolEligible"] and result["errors"])


if __name__ == "__main__":
    unittest.main()
