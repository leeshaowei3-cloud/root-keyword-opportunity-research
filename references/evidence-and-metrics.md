# Evidence and metrics contract

## Collection identity

Freeze before network access:

- `task_mode`, `batch_id`, created/updated time and immutable fingerprint;
- root-pool version, row count, path and SHA-256;
- roots, strategy, direction, protected question-word set;
- country/market, locale/language, device;
- endpoint/tool version, depth/children/query settings;
- output and append-only raw-event paths;
- expected steps and current status.

Preserve the wrapper manifest fields rather than rebuilding a thinner summary:

`task_mode, batch_id, root_pool, market, language, device, created_at, updated_at, batch_fingerprint, immutable_context, status, classification, counts_as_demand_evidence, expected_steps, root_runs, budget_history, budget_per_root, mode, expansion, market_context, source_pool, roots, merged_output, metrics_template, step_completion, next_gate, analysis_artifacts`

Each root run retains:

`root, status, collection_status, strategy, direction, question_words, initial_query_count, attempted_now, completed_now, processed_total, queued_remaining, unrun_total, budget, budget_reached, failed_total, new_suggestions, unique_suggestions_total, run_fingerprint, raw_events, output, state, metrics_template, scoring_status, elapsed_seconds`

Do not overwrite an old root-run snapshot with later batch analysis. `complete_for_collected_raw` means only that the raw data already collected was processed; it does not mean the remaining query graph was collected.

The total budget belongs to execution history, not the immutable fingerprint. It may increase for resume. Never lower it below completed work or treat exhaustion as completion.

## Raw event minimum

Record success, zero-result, and failure events:

`event_id`, stable query/result key, batch/task/pool, root, query, query kind, direction, depth, original suggestions, source channel, propagation label, market, language, device, started/completed time, attempt, status, error, and recursive parent evidence when applicable.

Text pools and deduplicated lists are reproducible derived views. Preserve multiple source events for the same normalized keyword.

## Cleaning and promotion

Maintain mutually exclusive rule-pass, review, and reject ledgers. Assert:

`unique_raw = rule_pass + review + reject`

Promotion requires the original `promotion_id`, keyword, rule status, category, sources, task type, input, output, digital deliverable, disposition, and review reason. Duplicate or conflicting decisions fail before output. Only promoted rows can create enrichment templates.

Current CSV contracts:

- clean review: `keyword, category, sources`;
- clean rejected: `keyword, reason, sources`;
- clean audit: `keyword, status, category, reason, sources`;
- promotion: `promotion_id, keyword, rule_status, category, sources, task_type, input, output, digital_deliverable, disposition, review_reason`.

The promotion ledger covers clean rule-pass and review rows, not automatic rejects. Assert:

`promotion_rows + clean_rejected = accounted_unique`

and:

`promoted + review + rejected + pending = promotion_rows`

`promotion_id` is the stable hash of keyword, rule status, category, and sources. Changing any of those provenance fields invalidates the decision. Require `review_reason` operationally even where an older CLI version does not.

## Metric observations

Required context for a comparable observation:

`Keyword, Market, Language, Device, MetricSource, MatchType, CheckedAt, Volume, CPC, KD`

Preserve raw provider display values and normalized values. `0` is valid. Blank, dash, unavailable, and parse failure remain missing/invalid and must not become zero.

Metric observation coverage is conserved across the full canonical slate:

`canonical_slate = metric_valid + metric_missing + metric_unavailable + metric_invalid + metric_conflict`

Coverage is complete when every canonical phrase has one of those explicit outcomes in the declared primary cohort. It does not require inventing numeric values for unavailable phrases.

Canonicalize aliases case-insensitively. Preserve unknown columns. Conflicting aliases or same-normalized-keyword rows with conflicting non-empty values must fail or enter a conflict ledger; never last-write-wins. Normalize Unicode and whitespace for identity, but preserve the original surface form, punctuation, digits/versions, brand casing, and word order for audit; do not “repair” malformed fragments into invented keywords.

Define:

For keyword-finder 1.4.0 compatibility:

`MetricCohortKey = market | language | device | provider | match_type | exact CheckedAt`

A future time-window cohort must be explicitly versioned and must not be silently substituted for the exact-date key.

Never mix provider fields into a synthetic row. Semrush Volume plus Ahrefs KD is not a cohort. Ads close variants are not exact Semrush observations. Similarweb Global is not Semrush US.

## Ranking views

Within each metric cohort produce:

- Volume descending;
- KD ascending;
- CPC descending.

Use a configurable boundary ratio, default `0.20`, as a soft `core / near / outside` review zone. It is not a deletion rule.

Preserve the current 1.4.0 compatibility defaults unless a batch explicitly versions different values:

- scale core: Volume `>= 30000`, KD `<= 60`, CPC `>= 0.01`;
- scale near band at 20%: Volume `24000–<30000`, KD `>60–72`, CPC `0.008–<0.01`;
- new-site core: KD `<= 29`, CPC `>= 0.10`;
- new-site near band at 20%: KD `>29–34.8`, CPC `0.08–<0.10`.

For a combined window, any outside component makes the row outside; otherwise any near component makes it near; only all-core components produce core. These are historical comparison windows, not permanent product-selection criteria.

The compatibility heuristic is:

`SearchOpportunityHeuristic = KDRoi = Volume × CPC ÷ max(KD, 1)`

It is a descriptive acquisition heuristic, not an eligibility, demand, payment, or build gate.

The scored audit must retain the original input order and all rows, adding:

`DataStatus, InputRowNumber, RawExtraCells, MetricCohortKey, ScoreDomain, SearchLane, WeightVersion, CoverageSignature, LaneScoreStatus, LaneScore, ScoreComponents, RankStability, KgrCoverageStatus, RankingGroupKey, HeuristicGroupRank, ScaleWindow, NewSiteWindow, BoundaryRatio, TitleSupplyRatio, KGR, KGRApplicability, KGRStatus, SearchOpportunityHeuristic, KDRoi, KD_effective, RankingStatus, PendingMetrics, eligible, rejection_reason`

Missing Volume/CPC/KD is `pending_metrics`; missing cohort context is `pending_metric_context`. Empty keyword, invalid numbers or dates, extra CSV cells, Volume `<=0`, or negative CPC/KD/intitle are invalid under 1.4.0. A raw zero must still be preserved as the observed value and must not become missing; route zero-volume rows to the explicit invalid/zero-volume ledger. Preserve invalid rows; do not silently coerce or delete them.

## KGR and title supply

- KGR is calculated only when `0 < Volume <= 250` and a valid non-negative `intitle` exists.
- `KGR = intitle / Volume`.
- Above 250, retain `TitleSupplyRatio` but mark KGR `out_of_scope`.
- A 250–300 soft area may be marked `near_applicability_review`, never KGR PASS.
- Preserve `IntitleSource`, `IntitleCheckedAt`, `IntitleQuerySyntax`, and `IntitleMarketLimitation`.

With default KGR threshold `0.25` and boundary ratio `0.20`:

- `<0.25`: `strong_kgr`; always route to current SERP;
- `0.25–<0.30`: `borderline_kgr`; route to SERP unless semantic contamination is already proven;
- `0.30–1.00`: `secondary_kgr`; sample when task clarity or trend evidence is strong;
- `>1.00`: `no_kgr_advantage`; do not promote on KGR grounds.

KGR coverage is complete only when the report provides these exact denominators:

`canonical slate = metric_valid + metric_missing + metric_unavailable + metric_invalid + metric_conflict`

`promoted phrases -> product families -> canonical keyword slate -> metric-valid phrases -> 0<Volume<=250 phrases -> allintitle-checked phrases -> strong/borderline/secondary/no-advantage`

Checking only a manually selected or numerically ranked active pool is `KgrCoverageStatus=sampled`, never batch-wide completion. Missing Volume or an unavailable result count stays missing. Use `not_assessable_missing_volume`, `not_assessable_missing_intitle`, or `invalid_zero_volume` rather than silently removing the phrase from the denominator. Do not coerce missing score components to zero or calculate a partial lane score as if it were complete.

## Lane scoring

Assign the lane before scoring and normalize only inside a compatible provider cohort. Use the stage-and-weight routing reference for the weights. Preserve every component, normalization method, missing value, and gate override in `ScoreComponents`.

- `kgr_longtail` requires KGR coverage before lane ranking;
- `scale_search` gives KGR zero weight;
- `emerging_search` protects new terms from missing-metric penalties;
- `narrow_product_value` is a product-research hypothesis and must not be presented as a low-competition SEO opportunity.

Each score record requires `ScoreDomain, Lane, Keyword, MetricCohortKey, RankingGroupKey, CoverageSignature, ScoreStatus, Score`. Never select the maximum across lanes or generate a family-level composite/global score.

A SERP `fail` overrides a numeric search-acquisition score. Product-research scoring remains separate and incomplete when problem or payment evidence is absent.

## Trends context

Required row-level fields:

`TrendStatus, TrendSource, TrendMarket, TrendWindow, TrendSearchType, TrendQueryType, TrendComparisonGroup, TrendCheckedAt, TrendArtifact`

Google Trends values are relative within the selected query group, geography, time window, and search type. Do not compare raw 0–100 values across different groups. Top and Rising answer different questions. Seven-day scans and twelve-month newness checks remain separate observations.

## SERP gate

Required fields:

`SerpChecked, SerpGateStatus, SerpMarket, SerpLanguage, SerpDevice, SerpSearchType, SerpCheckedAt, IntentGroup, PageType, DirectToolCount, BrandStrength, GapSummary`

Every evidence item also carries `EvidenceDomain`, one of `search_intent_supply`, `product_problem`, `product_payment`, `implementation`, or `risk`. SERP observations are `search_intent_supply`; they cannot increase `ProductEvidenceCoverage` or product scores.

`SerpGateStatus` is `pass`, `hold`, or `fail`. A ranking group exists only when gate=pass, the SERP context matches the metric context, the date is valid, search type is present, and intent/page type are present.

`RankingGroupKey = MetricCohortKey | SERP market | language | device | search type | date | intent group | page type`

The current metric cohort has no search-type field. Record the batch's explicit `MetricSearchTypeMapping` when deciding whether a SERP vertical is compatible; do not infer compatibility merely because `SerpSearchType` is non-empty.

Rank the heuristic only inside the same RankingGroupKey. A failed or negative SERP remains counterevidence and never receives a heuristic rank.

## Similarweb and other supplemental sources

Store Similarweb as an independent observation with provider, geography, period, match type, device, clicks/searches where available, zero-click share, KD/CPC if displayed, competing domains, and access limitations.

Global-versus-US differences support only hypotheses such as regional concentration, device mismatch, language mismatch, or provider-model mismatch. Confirm a US conclusion with a US-compatible cohort or first-party data.

For provider imports, preserve input ordinal and every raw display field such as raw intent, volume, KD, CPC, update time, unavailable marker, and source context before normalization. Never modify the raw file in place.

For Trends artifacts, preserve the provider's `GroupKey`/comparison group and `QueryType`; never compare relative indices across those groups. For provisional SERP review files, preserve `ReviewStatus`, `ProvisionalGate`, observed supply, gap hypothesis, and evidence. Map a provisional gate to final `SerpGateStatus` explicitly; never equate the two silently.

## Collection and conservation status

- `not_started`: no query processed.
- `partial_failure`: unresolved failed items exist.
- `complete`: no unrun query remains in the declared graph.
- `partial_manual_cap`: stopped by `max_queries`.
- `partial_budget_exhausted`: stopped by budget while unrun work remains.

`attempted_now`, `completed_now`, and `processed_total` are different counters. `queued_remaining` excludes failures; `unrun_total` is the deduplicated union of pending and failed work. `budget_reached` never means complete.

Cleaning conservation uses whitespace-folded, case-insensitive unique inputs:

`rule_pass + review + reject = accounted_unique`

## Evidence limits

Autocomplete, Trends, Ads, Semrush, Ahrefs, Similarweb, KGR, KDRoi, domains, and SERPs can prioritize research. None alone or together is sufficient proof of recurring pain, willingness to pay, product selection, validation permission, or development permission.
