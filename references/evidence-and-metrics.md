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

`canonical_slate = metric_complete + metric_partial + metric_unavailable + metric_invalid + metric_conflict`

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

`DataStatus, InputRowNumber, RawExtraCells, MetricCohortKey, ScoreDomain, SearchLane, WeightVersion, CoverageSignature, LaneScoreStatus, LaneScore, ScoreComponents, RankStability, StrictTitleSupplyCoverageStatus, RankingGroupKey, HeuristicGroupRank, ScaleWindow, NewSiteWindow, BoundaryRatio, TitleSupplyMethodVersion, TitleSupplyTokenizerVersion, TitleSupplyQuerySyntax, TitleSupplyQuery, TitleSupplyCountMethod, ReducerPolicyVersion, TitleSupplyHL, TitleSupplyGL, TitleSupplyDevice, TitleSupplySearchType, TitleSupplyPws, TitleSupplyFilter, TitleSupplyNfpr, TitleSupplyCheckedDate, TitleSupplyQueryContextKey, StrictTitleSupplyUniqueUrlCount, VerifiedMatchingUniqueUrlCount, LowerBoundBasis, TitleSupplyPageCount, TitleSupplyExhausted, TitleSupplyBlocked, TitleSupplyCaptcha, TitleSupplyQueryIntegrity, TitleSupplyIntegrityIssueCount, TitleSupplyEarlyStopT, TitleSupplyCountStatus, StrictTitleSupplyRatio, StrictTitleSupplyRoutingBand, SearchOpportunityHeuristic, KDRoi, KD_effective, RankingStatus, PendingMetrics, eligible, rejection_reason`

Missing Volume/CPC/KD is `pending_metrics`; missing cohort context is `pending_metric_context`. Empty keyword, invalid numbers or dates, extra CSV cells, Volume `<=0`, or negative CPC/KD/intitle are invalid under 1.4.0. A raw zero must still be preserved as the observed value and must not become missing; route zero-volume rows to the explicit invalid/zero-volume ledger. Preserve invalid rows; do not silently coerce or delete them.

## Strict title supply and classic-KGR separation

Method `strict_multi_intitle_enumerated_v1` defines a new title-supply observation. It is not classic KGR:

- A normal Google result estimate from one `allintitle:<phrase>` page is not an acceptable numerator for either this method or a new KGR claim.
- Apply `nfkc_unicode_alnum_connectors_v1`: after NFKC, retain Unicode alphanumeric tokens plus in-token `&`, `+`, and `#`; preserve stopwords and non-ASCII tokens, and discard a standalone `&`. Under `explicit_intitle_per_token_v1`, quote every cleaned token as `intitle:"token"`. Preserve the exact keyword, query, method/tokenizer identity, locale, device, date, and search limitations.
- Record count method `paginated_deduplicated_organic_canonical_urls_with_displayed_title_integrity_audit`; another count method is incompatible rather than comparable.
- Freeze `hl`, `gl`, `device=desktop`, `SearchType=google_web`, `pws=0`, `filter=0`, `nfpr=1`, and checked date into `TitleSupplyQueryContextKey`. Different context keys are separate cohorts: never merge counts or reuse one as the other's observation.
- Enumerate pages and count operator-returned organic canonical URLs before auditing displayed-title integrity. Deduplicate canonical URLs across pages and remove common display-tracking parameters (`utm_*`, `gclid`, `fbclid`, `srsltid`) while retaining business parameters. Do not count ads, modules, result cards, displayed totals, cached links, navigation links, or repeated URLs. Under `ReducerPolicyVersion=verified_visible_title_lower_bound_v1`, also count deduplicated `VerifiedMatchingUniqueUrlCount`: the title is known and every required token is visible. A title with a truncation marker may enter this verified subset only when all required tokens are already visible; truncation still prevents exactness.
- A CAPTCHA, generic block, repeated pagination URL, or identical non-empty organic URL set on different page URLs is not exhaustion. Stop immediately and record `TitleSupplyBlocked=true` plus `StrictTitleSupplyRoutingBand=not_assessable_blocked`; do not infer a ratio or continue automated requests. Mismatched, truncated, and unknown titles remain in the operator-returned URL count and in the integrity ledger. An integrity flag is audit evidence rather than an automatic terminal outcome when the verified subset independently reaches T. If that subset has not reached T, any such issue yields `TitleSupplyCountStatus=query_integrity_hold` and `StrictTitleSupplyRoutingBand=not_assessable_query_integrity`. Never filter questionable URLs out and publish the remainder as an exact ratio or low-supply result.
- Require actual JSON booleans for every page/result flag. Bind each page URL's decoded `q`, `hl`, `gl`, `pws`, `filter`, `nfpr`, and `start` to the observation query/context and continuous page index. Store normalized `pws`, `filter`, and `nfpr` as integers in the observation context even though browser URL parameters are strings. Reject missing-first-page, skipped-page, wrong-query, and cross-context inputs rather than interpreting them.
- Genuine terminal pagination requires `pagination_state=end_of_results`, an allowed end-of-results evidence code, `has_next_control=false`, and no title-integrity issue. Only then may the reducer emit `TitleSupplyCountStatus=exact_exhausted` and, when `0 < Volume <= 250`, `StrictTitleSupplyRatio = StrictTitleSupplyUniqueUrlCount / Volume`. The verified-title rescue never relaxes this exact low-supply rule.
- Terminal evidence must agree with the page: `explicit_no_results` requires zero organic results, and `terminal_page_short_and_no_next` requires an observed page shorter than the frozen page size.
- Compute `T = floor(0.30 × Volume) + 1`. When `VerifiedMatchingUniqueUrlCount` reaches T, stop with `TitleSupplyCountStatus=lower_bound_gt_0_30` and `LowerBoundBasis=verified_matching_unique_urls`, including when other returned titles carry integrity issues. Preserve both the total operator-returned count and the verified count, but leave `StrictTitleSupplyRatio` empty. This is a one-sided proof of high supply, never an exact or low-supply inference.
- v2.0.2 leaves `strict_multi_intitle_enumerated_v1`, `explicit_intitle_per_token_v1`, and `nfkc_unicode_alnum_connectors_v1` unchanged. Compatible v2.0.1 raw pages may be re-reduced without recollection, but derived outputs are policy-versioned: retain the old reducer identity or generate a new artifact with `ReducerPolicyVersion`; never silently overwrite or relabel old derived results.
- Data collected under classic unquoted `allintitle:`, a displayed-total method, another tokenization, or any pre-v2.0.1 method is `legacy_reference_only` / `not_assessable_method_mismatch`. Its reuse is zero under the strict method. Preserve it only as legacy comparison, record the actual migration denominator per batch, and recollect every eligible phrase for strict coverage.
- The strict long-tail reducer rejects Volume above 250. If scale-lane title supply is collected, keep it in a separate out-of-scope artifact with no strict long-tail routing band. A 250–300 soft area may be reviewed, never treated as a pass.
- Preserve `TitleSupplySource`, `TitleSupplyMethodVersion`, `TitleSupplyTokenizerVersion`, `TitleSupplyQuerySyntax`, `TitleSupplyQuery`, `TitleSupplyCountMethod`, `ReducerPolicyVersion`, all frozen query-context fields and key, `StrictTitleSupplyUniqueUrlCount`, `VerifiedMatchingUniqueUrlCount`, `LowerBoundBasis`, `TitleSupplyPageCount`, `TitleSupplyExhausted`, `TitleSupplyBlocked`, `TitleSupplyCaptcha`, `TitleSupplyQueryIntegrity`, `TitleSupplyIntegrityIssueCount`, `TitleSupplyEarlyStopT`, `TitleSupplyCountStatus`, and the market limitation.

For compatible exact observations, use the following provisional routing bands:

- `<0.25`: `provisional_strong`; always route to current SERP;
- `0.25–0.30`, inclusive: `provisional_borderline`; route to SERP unless semantic contamination is already proven;
- `>0.30`: `provisional_high`; do not promote on title-supply grounds.

Compatible early-stop or verified-title rescue observations are `provisional_high` with count status `lower_bound_gt_0_30`. For a rescue, the threshold count is `VerifiedMatchingUniqueUrlCount`, not the larger operator-returned count. They are assessed one-sided high-supply outcomes, not ratios and not KGR measurements.

Strict title-supply coverage is complete only when the report provides these exact denominators:

`canonical slate = metric_complete + metric_partial + metric_unavailable + metric_invalid + metric_conflict`

`promoted phrases -> product families -> canonical keyword slate -> metric-valid phrases -> 0<Volume<=250 phrases -> exact_exhausted + lower_bound_gt_0_30 + missing/blocked/method-mismatch -> provisional strong/borderline/high`

Checking only a manually selected or numerically ranked active pool is `StrictTitleSupplyCoverageStatus=sampled`, never batch-wide completion. Canonical metric rows use `complete|partial|unavailable|invalid|conflict`, retain `volume/kd/cpc` independently as a non-negative number or null, and list every null field in `missing_fields`. Derive the eligible denominator and keyword-ID set from complete or partial rows whose observed Volume satisfies `0 < Volume <= 250`; a partial row with Volume but missing KD/CPC remains eligible. Do not trust a submitted eligible aggregate. The strict record ID set must match it exactly. Conserve `eligible = exact_checked + lower_bound_gt_0_30 + not_assessable_missing_enumeration + not_assessable_blocked + not_assessable_query_integrity + not_assessable_method_mismatch + not_assessable_context_mismatch`. Conservation proves that no row disappeared; it does not prove assessability. `require_all_assessable=true` is mandatory, every observation must use the expected context, exactly one compatible context key is allowed for a non-empty eligible set, strict `hl/gl/device` must equal metric language/market/device, and every not-assessable outcome must be absent before `StrictTitleSupplyEligibleCoverageComplete` or `ActivePoolEligible` can be true. Exact provisional-strong/borderline and primary exact-zero observations also require separately identified same-context exact repeats at `<=0.30`; never substitute a confirmation boolean. Missing Volume or an unavailable enumeration stays missing. Use explicit not-assessable or invalid outcomes rather than silently removing a phrase from the denominator. Do not coerce missing score components to zero or calculate a partial lane score as if it were complete.

## Lane scoring

Assign the lane before scoring and normalize only inside a compatible provider cohort. Use the stage-and-weight routing reference for the weights. Preserve every component, normalization method, missing value, and gate override in `ScoreComponents`.

- `strict_title_supply_longtail` requires compatible strict coverage before lane ranking;
- `scale_search` gives strict title supply zero weight;
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
