# Stage and weight routing

## Core rule

Do not narrow to an active pool before the full canonical keyword slate has comparable metrics and every KGR-eligible phrase has been checked. Metrics answer different questions at different stages; do not blend them into one universal score.

Maintain three protected search-acquisition lanes and one parallel product-research lane:

- `kgr_longtail`: natural task phrases with `0 < Volume <= 250`;
- `scale_search`: phrases with `Volume > 250`;
- `emerging_search`: new/rising phrases with unavailable or immature volume;
- `narrow_product_value`: a concrete costly task that may have weak search acquisition; this is a product-research lane and never shares a numeric comparison with the three search lanes.

A family may appear in more than one lane, but each score retains its domain, lane, keyword, and cohort. Never let one lane's weights erase another lane, take the maximum across lanes, or generate a global family score.

## Stage order

| Stage | Action | Allowed narrowing |
|---|---|---|
| 0. Discovery | Collect broad autocomplete and justified adjacent-channel phrases | Remove only exact technical duplicates from derived views; preserve raw events |
| 1. Semantic promotion | Require user/moment/input/transformation/output/deliverable; reject navigation, physical services, manuals, malformed phrases and unsafe claims; then audit stratified false negatives | Hard semantic gate only; no Volume, KD, CPC, KGR or Trends weights |
| 2. Family and keyword slate | Cluster all promoted phrases; retain one natural primary, up to two standard variants, and every protected constraint-rescue phrase | Do not create the 15-30 active pool yet; preserve the full family longlist and canonical slate |
| 3. Metric enrichment | Give every canonical phrase a valid provider observation or explicit missing/unavailable/invalid/conflict record in the declared cohort | Split into lanes; do not use thresholds to delete rows |
| 4. KGR and Trends routing | Check every KGR-eligible phrase; inspect trend/newness for scale and emerging lanes | Advance protected candidates to SERP sampling; do not call a product winner |
| 5. Live SERP | Check intent, direct tools, brands, result types and unfinished work | `fail` removes a phrase from the search-acquisition pool; retain it as counterevidence or product-only hypothesis |
| 6. Portfolio selection | Compare only within compatible lane/cohort, then build a diversified family pool | Select research priorities; never grant validation or development permission |

## KGR coverage gate

Use the standard unquoted syntax consistently: `allintitle:<keyword phrase>`.

- `< 0.25`: `strong_kgr`; always advance to a live SERP check.
- `0.25-<0.30`: `borderline_kgr`; advance unless obvious semantic contamination exists.
- `0.30-1.00`: `secondary_kgr`; sample when the task or trend is strong.
- `> 1.00`: `no_kgr_advantage`; do not promote on KGR grounds.
- `Volume > 250`: `kgr_not_applicable`; retain title-supply ratio only.
- `Volume 250-300`: optional title-supply review, never KGR pass.

Do not conclude that a batch has no KGR opportunities unless the metric-observation conservation and all of these counts are reported and complete:

`canonical slate = metric_valid + metric_missing + metric_unavailable + metric_invalid + metric_conflict`

`promoted phrases -> product families -> canonical keyword slate -> metric-valid phrases -> 0<Volume<=250 phrases -> allintitle-checked phrases -> strong/borderline/secondary/no-advantage`

Also report `not_assessable_missing_volume`, `not_assessable_missing_intitle`, and `invalid_zero_volume`. An active-pool sample is not a valid denominator for a batch-wide KGR conclusion. Missing search volume or an unavailable Google count remains missing, not zero.

Repeat anomalous zero counts and every apparent strong/borderline KGR result on dated runs using the same syntax and context. Preserve each observation and use the median of valid runs for a continuous KGR value; a single stable threshold-side result may route a phrase provisionally but must carry lower confidence.

## Search-acquisition weights

Use percentile or bounded normalized values inside one compatible provider cohort. Apply these defaults only after a valid SERP observation exists. A SERP `fail` overrides the numeric score.

### KGR long-tail lane

| Signal | Weight |
|---|---:|
| Live SERP accessibility and unfinished work | 35 |
| KGR/title scarcity | 30 |
| Provider KD | 15 |
| Volume within the long-tail cohort | 10 |
| Trend stability or useful emergence | 5 |
| CPC/commercial search context | 5 |

Before full SERP review, use KGR bands as protected routing rules rather than inventing a partial weighted score. A `strong_kgr` phrase cannot be removed merely because CPC is zero, KD is missing, or another family has higher volume.

### Scale-search lane

| Signal | Weight |
|---|---:|
| Live SERP accessibility and unfinished work | 35 |
| Provider KD | 20 |
| Volume | 20 |
| CPC/commercial search context | 15 |
| Trend stability or growth | 10 |

KGR weight is zero in this lane. A high-volume phrase with hostile SERP remains counterevidence even when its arithmetic score is high.

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

Do not produce a complete product score while problem or payment evidence is missing. Mark coverage and confidence instead. A narrow product-value family may survive weak KGR, but it must not be marketed as a low-competition SEO opportunity.

Admit a family to `narrow_product_value` when it has a concrete professional user and moment, domain-specific input, non-trivial transformation, a portable hard-format deliverable, and at least one plausible error, replacement, compliance, or delay cost. This admission reserves a current intent/SERP check and the cheapest permitted problem falsification; it does not assert that the cost or payment evidence exists. Missing problem/payment evidence remains pending rather than scoring zero.

## Weight governance

The tables above are versioned default priors, not universal truths or hard eligibility thresholds.

- Apply hard semantic, cohort, KGR-coverage, and SERP gates before any weighted comparison.
- Do not renormalize a score around missing components. Mark it `incomplete_components` and preserve the missing field.
- Record `WeightVersion`, component normalization, source confidence, freshness, and every gate override.
- Run a sensitivity check by varying each non-zero weight by roughly 20% and renormalizing the complete vector. If a family's tier or top group changes materially, mark `RankStability=unstable` and present the evidence rather than a precise rank.
- Calibrate future weights from observed Search Console impressions/clicks, ranking movement, retention, validation outcomes, and false positives across multiple batches. Do not rewrite weights from one social case study or one successful site.
- A lane score orders research inside that lane. It never overrides another lane, grants a company permission, or substitutes for the product-research evidence score.
- Every score record must retain `ScoreDomain, Lane, Keyword, MetricCohortKey, RankingGroupKey, CoverageSignature, ScoreStatus, Score`. `ScoreDomain` is either `search_acquisition` or `product_research`.
- SERP-only evidence may improve only `search_acquisition`; it must not increase `ProductEvidenceCoverage` or the product score.

## Pool construction

Build the 15-30 active research families only after lane routing and representative SERPs:

- preserve every `strong_kgr` phrase and its family unless SERP fails;
- retain the best scale-search families by compatible cohort and SERP gate;
- reserve space for emerging-search and narrow-product-value hypotheses;
- keep all overflow and counterevidence in the versioned longlist;
- never use fixed family count, diversity, implementation ease or CPC to remove the only strong KGR phrase before SERP review.

If passed strong/borderline KGR families exceed the presentation capacity, publish a 15-30 comparison core plus a `protected_kgr_annex`. The annex is still active search research and remains in coverage counts.

The machine gate is:

`ActivePoolEligible = CanonicalSlateFrozen && PrimaryMetricObservationCoverageComplete && KgrEligibleCoverageComplete && RepresentativeSerpCoverageComplete`

When false, output only a `semantic_preview` or `provisional_family_longlist_view`; do not use `active-pool` in a filename, status, or report title.

Record `Lane, WeightVersion, LaneScoreStatus, LaneScore, ScoreComponents, RankStability, KgrCoverageStatus, SerpGateStatus, ProductEvidenceCoverage` for every active or held family.
