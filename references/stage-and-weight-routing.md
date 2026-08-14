# Stage and weight routing

## Core rule

Do not narrow to an active pool before the full canonical keyword slate has comparable metrics and every strict-title-supply-eligible phrase has an explicit compatible outcome. Metrics answer different questions at different stages; do not blend them into one universal score.

Maintain three protected search-acquisition lanes and one parallel product-research lane:

- `strict_title_supply_longtail`: natural task phrases with `0 < Volume <= 250`;
- `scale_search`: phrases with `Volume > 250`;
- `emerging_search`: new/rising phrases with unavailable or immature volume;
- `narrow_product_value`: a concrete costly task that may have weak search acquisition; this is a product-research lane and never shares a numeric comparison with the three search lanes.

A family may appear in more than one lane, but each score retains its domain, lane, keyword, and cohort. Never let one lane's weights erase another lane, take the maximum across lanes, or generate a global family score.

## Stage order

| Stage | Action | Allowed narrowing |
|---|---|---|
| 0. Discovery | Collect broad autocomplete and justified adjacent-channel phrases | Remove only exact technical duplicates from derived views; preserve raw events |
| 1. Semantic promotion | Require user/moment/input/transformation/output/deliverable; reject navigation, physical services, manuals, malformed phrases and unsafe claims; then audit stratified false negatives | Hard semantic gate only; no Volume, KD, CPC, title-supply or Trends weights |
| 2. Family and keyword slate | Cluster all promoted phrases; retain one natural primary, up to two standard variants, and every protected constraint-rescue phrase | Do not create the 15-30 active pool yet; preserve the full family longlist and canonical slate |
| 3. Metric enrichment | Give every canonical phrase a valid provider observation or explicit missing/unavailable/invalid/conflict record in the declared cohort | Split into lanes; do not use thresholds to delete rows |
| 4. Strict title supply and Trends routing | Enumerate every eligible phrase under the versioned strict method; inspect trend/newness for scale and emerging lanes | Advance protected candidates to SERP sampling; do not call a product winner |
| 5. Live SERP | Check intent, direct tools, brands, result types and unfinished work | `fail` removes a phrase from the search-acquisition pool; retain it as counterevidence or product-only hypothesis |
| 6. Portfolio selection | Compare only within compatible lane/cohort, then build a diversified family pool | Select research priorities; never grant validation or development permission |

## Strict title-supply coverage gate

Use method `strict_multi_intitle_enumerated_v1` consistently:

1. Apply tokenizer `nfkc_unicode_alnum_connectors_v1`: after NFKC, retain Unicode alphanumeric tokens plus in-token `&`, `+`, and `#`; preserve token order, stopwords, and non-ASCII tokens, but discard a standalone `&`.
2. Use query syntax `explicit_intitle_per_token_v1` and quote every cleaned token. For example, `p&l maker & converter` becomes `intitle:"p&l" intitle:"maker" intitle:"converter"`.
3. Freeze and record `hl`, `gl`, `device=desktop`, `SearchType=google_web`, `pws=0`, `filter=0`, `nfpr=1`, and checked date. Treat each resulting query-context key as a separate cohort; never merge or reuse observations across keys.
4. Enumerate result pages. Count and deduplicate operator-returned organic canonical URLs before auditing displayed-title integrity. Remove display-tracking parameters including `utm_*`, `gclid`, `fbclid`, and `srsltid`, while retaining business parameters. With `ReducerPolicyVersion=verified_visible_title_lower_bound_v1`, separately deduplicate URLs whose known displayed titles visibly contain every required token as `VerifiedMatchingUniqueUrlCount`. A truncated title qualifies for that verified subset only when all required tokens are already visible; it remains an integrity issue for exactness.
5. Treat pagination as exhausted only when the raw page records `pagination_state=end_of_results`, one allowed end-of-results evidence code, and `has_next_control=false`. A displayed-title mismatch, explicit truncation flag, detected ellipsis, or unknown title remains recorded in the integrity ledger. If the verified subset does not prove high supply, any such issue yields `not_assessable_query_integrity`; retain every operator-returned URL but never calculate an exact ratio or infer low supply. CAPTCHA, generic block pages, repeated page URLs, and identical non-empty organic URL sets on different pagination URLs are blocked outcomes, never exhaustion.
6. Compute `T = floor(0.30 × Volume) + 1`. If `VerifiedMatchingUniqueUrlCount >= T`, stop and record `TitleSupplyCountStatus=lower_bound_gt_0_30` plus `LowerBoundBasis=verified_matching_unique_urls`, even when other titles have integrity issues. Leave `StrictTitleSupplyRatio` empty. The rescue proves only the one-sided high-supply lower bound.
7. Only genuine exhaustion with no title-integrity issue produces `StrictTitleSupplyRatio = StrictTitleSupplyUniqueUrlCount / Volume`. Never filter questionable URLs out to manufacture an exact low count.
8. Stop immediately on CAPTCHA or another block and record `not_assessable_blocked`; do not retry aggressively or infer a count.
9. Treat any older/different method, query syntax, tokenizer, or count method as `not_assessable_method_mismatch`; treat a mixed or incompatible query context as `not_assessable_context_mismatch`. Unquoted-classic observations have zero reuse under the strict method and remain legacy comparison only; report the actual migration denominator in each batch.

For exact strict observations, use these provisional routing bands only:

- `< 0.25`: `provisional_strong`; always advance to a live SERP check.
- `0.25–0.30`, inclusive: `provisional_borderline`; advance unless obvious semantic contamination exists.
- `> 0.30`: `provisional_high`; do not promote on title-supply grounds.

For a non-exhausted early stop or verified-title rescue, retain both the operator-returned and verified unique counts and record `lower_bound_gt_0_30`, but do not manufacture an exact ratio. The count used to prove T is the verified count. `StrictTitleSupplyRatio` is not classic KGR under any outcome.

- `Volume > 250`: strict long-tail routing is not applicable; retain any compatible title-supply observation separately.
- `Volume 250-300`: optional title-supply review, never a routing pass.

Do not conclude that a batch has no low-title-supply opportunities unless the metric-observation conservation and all of these counts are reported and complete:

`canonical slate = metric_complete + metric_partial + metric_unavailable + metric_invalid + metric_conflict`

`promoted phrases -> product families -> canonical keyword slate -> metric-valid phrases -> 0<Volume<=250 phrases -> exact_exhausted + lower_bound_gt_0_30 + missing/blocked/method-mismatch -> provisional strong/borderline/high`

Also report `not_assessable_missing_volume`, `not_assessable_missing_enumeration`, `not_assessable_blocked`, `not_assessable_query_integrity`, `not_assessable_method_mismatch`, and `invalid_zero_volume`. An active-pool sample is not a valid denominator for a batch-wide title-supply conclusion. Missing search volume or an unavailable enumeration remains missing, not zero.

Repeat anomalous exact zero counts and every provisional strong/borderline result on dated runs using the same method and context. Preserve each observation and use the median only across compatible exact `StrictTitleSupplyRatio` runs; a single threshold-side result may route provisionally but must carry lower confidence.

## Search-acquisition weights

Use percentile or bounded normalized values inside one compatible provider cohort. Apply these defaults only after a valid SERP observation exists. A SERP `fail` overrides the numeric score.

### Strict title-supply long-tail lane

| Signal | Weight |
|---|---:|
| Live SERP accessibility and unfinished work | 35 |
| Strict enumerated title scarcity | 30 |
| Provider KD | 15 |
| Volume within the long-tail cohort | 10 |
| Trend stability or useful emergence | 5 |
| CPC/commercial search context | 5 |

Before full SERP review, use provisional strict-title-supply bands as protected routing rules rather than inventing a partial weighted score. A `provisional_strong` phrase cannot be removed merely because CPC is zero, KD is missing, or another family has higher volume.

### Scale-search lane

| Signal | Weight |
|---|---:|
| Live SERP accessibility and unfinished work | 35 |
| Provider KD | 20 |
| Volume | 20 |
| CPC/commercial search context | 15 |
| Trend stability or growth | 10 |

Strict title-supply weight is zero in this lane. A high-volume phrase with hostile SERP remains counterevidence even when its arithmetic score is high.

### Emerging-search lane

| Signal | Weight |
|---|---:|
| Trend shape and persistence | 35 |
| Live SERP whitespace and entrant age | 30 |
| Recency/newness confidence | 15 |
| KD, when a compatible value exists | 10 |
| CPC, when available | 5 |
| Volume, when mature enough to interpret | 5 |

Do not coerce missing new-term metrics to zero. Recheck the lane on a dated cadence.

## Product-research weights

Keep product research separate from search acquisition. Search evidence may route research but cannot fill these fields.

| Signal | Weight |
|---|---:|
| Repeated problem or unfinished-job evidence | 30 |
| Payment, replacement cost or committed-use evidence | 20 |
| Task and portable deliverable clarity | 15 |
| Access to real inputs and measurable output quality | 15 |
| Implementation and maintenance fit | 10 |
| Inverse liability/compliance/platform risk | 10 |

Do not produce a complete product score while problem or payment evidence is missing. Mark coverage and confidence instead. A narrow product-value family may survive high title supply, but it must not be marketed as a low-competition SEO opportunity.

Admit a family to `narrow_product_value` when it has a concrete professional user and moment, domain-specific input, non-trivial transformation, a portable hard-format deliverable, and at least one plausible error, replacement, compliance, or delay cost. This admission reserves a current intent/SERP check and the cheapest permitted problem falsification; it does not assert that the cost or payment evidence exists. Missing problem/payment evidence remains pending rather than scoring zero.

## Weight governance

The tables above are versioned default priors, not universal truths or hard eligibility thresholds.

- Apply hard semantic, cohort, strict-title-supply-coverage, and SERP gates before any weighted comparison.
- Do not renormalize a score around missing components. Mark it `incomplete_components` and preserve the missing field.
- Record `WeightVersion`, component normalization, source confidence, freshness, and every gate override.
- Run a sensitivity check by varying each non-zero weight by roughly 20% and renormalizing the complete vector. If a family's tier or top group changes materially, mark `RankStability=unstable` and present the evidence rather than a precise rank.
- Calibrate future weights from observed Search Console impressions/clicks, ranking movement, retention, validation outcomes, and false positives across multiple batches. Do not rewrite weights from one social case study or one successful site.
- A lane score orders research inside that lane. It never overrides another lane, grants a company permission, or substitutes for the product-research evidence score.
- Every score record must retain `ScoreDomain, Lane, Keyword, MetricCohortKey, RankingGroupKey, CoverageSignature, ScoreStatus, Score`. `ScoreDomain` is either `search_acquisition` or `product_research`.
- SERP-only evidence may improve only `search_acquisition`; it must not increase `ProductEvidenceCoverage` or the product score.

## Pool construction

Build the 15-30 active research families only after lane routing and representative SERPs:

- preserve every `provisional_strong` phrase and its family unless SERP fails;
- retain the best scale-search families by compatible cohort and SERP gate;
- reserve space for emerging-search and narrow-product-value hypotheses;
- keep all overflow and counterevidence in the versioned longlist;
- never use fixed family count, diversity, implementation ease or CPC to remove the only provisional-strong phrase before SERP review.

If passed provisional-strong/borderline families exceed the presentation capacity, publish a 15-30 comparison core plus a `protected_title_supply_annex`. The annex is still active search research and remains in coverage counts.

The machine gate is:

`ActivePoolEligible = CanonicalSlateFrozen && PrimaryMetricObservationCoverageComplete && StrictTitleSupplyEligibleCoverageComplete && RepresentativeSerpCoverageComplete`

`StrictTitleSupplyEligibleCoverageComplete` requires both denominator conservation and complete assessability. The validator derives the denominator from canonical inline rows whose metric status is complete or partial and whose observed Volume satisfies `0 < Volume <= 250`; a partial row with valid Volume remains eligible even when KD/CPC are null. It does not trust a submitted `strict_title_supply.eligible` aggregate. The set of strict record keyword IDs must equal that derived set exactly. With `require_all_assessable=true`, every eligible phrase must resolve to `exact_exhausted` or `lower_bound_gt_0_30`, every observation must use the expected context, exactly one compatible context key must be present for a non-empty eligible set, and strict `hl/gl/device` must match the primary metric language/market/device. A lower-bound row must use its verified-title count, never the larger operator-returned count, to satisfy T. Every exact provisional-strong/borderline result and every primary exact zero requires at least one separate, uniquely identified, same-context exact repeat whose ratio remains `<=0.30`; a `repeat_confirmed` boolean is not evidence. Any missing enumeration, block, unresolved `not_assessable_query_integrity`, method/context mismatch, or absent repeat makes this gate false. A fully recorded batch of not-assessable outcomes is conserved but is not coverage-complete.

`PrimaryMetricObservationCoverageComplete` is derived from canonical rows: every row must carry a complete `market/language/device/provider/match_type/checked_date` metric context and the batch must contain exactly one compatible normalized context key. Each row also carries non-negative-or-null `volume/kd/cpc` plus a `missing_fields` set that exactly matches its null fields. `complete` has all three values, `partial` has both observed and missing fields, and `unavailable` has all three null. Missing or unavailable values remain explicit rather than disappearing or becoming zero.

`RepresentativeSerpCoverageComplete` requires frozen non-empty plan and observation record arrays whose plan-ID sets match exactly and whose SHA-256 values are recomputed from the inline arrays. Each SERP observation must contain real `market/language/device/search_type/checked_date/intent_group/page_type` context; a `context_compatible` boolean is rejected. The plan must cover at least `min(30, family_total)` families, every provisional-strong/borderline family, every `narrow_product_value` family, and every non-empty lane. All SERP observations share one date and match the primary metric market/language/device. A zero-sized or self-reported one-row plan never passes.

Artifact SHA checks catch stale or accidentally divergent summaries. They do not protect against an actor who can rewrite both records and hashes; an immutable external receipt is outside this local gate.

When false, output only a `semantic_preview` or `provisional_family_longlist_view`; do not use `active-pool` in a filename, status, or report title.

Record `Lane, WeightVersion, LaneScoreStatus, LaneScore, ScoreComponents, RankStability, StrictTitleSupplyCoverageStatus, SerpGateStatus, ProductEvidenceCoverage` for every active or held family.
