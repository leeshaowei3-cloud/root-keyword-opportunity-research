# Resource allocation and stopping

## Default portfolio of effort

Use ranges as planning defaults, then adapt:

- 40–60%: broad automated baseline across all selected roots;
- 25–40%: deepen high-yield roots, semantic clusters, and concrete task branches;
- 10–20%: sample low-yield, unfamiliar, contradictory, or anomalous branches.

These are not fixed quotas. Reallocate after every collection window.

Under the current bidirectional configuration, the deterministic floor is about 87 initial queries per root. Finish and verify this floor by direction and expansion kind before calling the baseline complete. The historical 120-per-root value is only a safe first-run cap: it usually buys the floor plus roughly 33 adaptive queries, and a remaining queue still means partial.

For large runs, use a global budget rather than pretending every root deserves the same depth. A practical first round is roughly 60% baseline / 30% high-yield deepening / 10% contrarian sampling; after the floor is covered, shifting toward 40% baseline-completion / 50% productive branches / 10% exploration is reasonable. Keep a per-root ceiling so generic roots cannot consume the batch.

## Branch measurements

For a window of completed queries, retain the numerator and denominator:

- `new_keyword_rate = newly seen normalized keywords / returned normalized keywords`;
- `duplicate_rate = repeated normalized occurrences / all normalized occurrences`;
- `query_yield = newly seen normalized keywords / successful queries`;
- `active_branch_ratio = branches producing at least one new keyword / branches queried`;
- `semantic_breadth = count of materially different task clusters`;
- `opportunity_density = semantically promotable task keywords / unique discovered keywords`;
- `channel_marginal_gain = unique useful additions / channel cost unit`.

Also record failure rate, zero-result rate, semantic-drift rate, and unvisited queue size. Do not collapse these into one score.

## Routing decisions

- High lexical and semantic breadth: cluster materially different completed jobs, then deepen representative branches inside each cluster; never limit an entire broad root to two or three branches.
- High lexical breadth but low opportunity density: keep as a hub root, reduce expensive validation.
- Low breadth but clear input/output/deliverable: move the keyword to product-family research even if recursion stops.
- Low breadth and uncertain meaning: sample one alternate channel or SERP before holding.
- High duplicate rate with stable clusters: stop the branch and preserve pending scope.
- Semantic drift: split into a new proposed branch; do not contaminate the original family.

## Semantic false-negative audit

Conservation does not prove semantic recall. Before metric enrichment, sample review and reject strata by root, decision reason, and semantic category. As a starting audit design, inspect roughly 5-10% of review, 3-5% of semantic rejects, and a reason-stratified sample of automatic rejects. Retain actual numerators and denominators.

If more than roughly 2% of a sampled stratum are clear digital tasks, or any severe/valuable task class is systematically missed, reopen the full stratum or a precisely defined affected rule and rerun promotion. These are versioned audit controls, not universal truths; change them only with recorded evidence.

## Stop protocol

Evaluate in windows rather than one query at a time. Normally stop deeper recursion after two consecutive windows show no material new task cluster and low marginal gain, or when safety/cost limits are reached. For fast-changing Trends branches, shorten the review interval; for stable evergreen roots, allow larger windows.

Every stop record must include:

- branch/root and channel;
- window size and observed metrics;
- `stop_reason`;
- remaining unvisited work;
- whether the status is `saturated`, `sampled_hold`, `semantic_drift`, `budget_partial`, or `complete_for_current_scope`;
- what new evidence would reopen it.

Never say “until no more words exist.” Search systems are open-ended. Completion always means complete for a declared scope.

A useful evaluation tranche is about 20 completed queries, but version it as an operating parameter rather than a truth. A branch may be deprioritized after two consecutive tranches with fewer than two new product families, more than 90% family duplication, or more than 60% navigation/brand/malformed noise. These are starting controls derived from current practice, not evidence of universal optimum; retain raw counts and allow override with a recorded reason.

Define the channel cost unit in each batch—API/browser calls, elapsed minutes, dollars, or reviewer minutes—before comparing marginal gain across channels.

Default recursion is two semantic levels after the initial root. Continue deeper only when the branch keeps producing materially different product families or strong problem/payment leads. Legacy exhaustive expansion is a coverage-audit tool, not the default production method.

## Metric and validation allocation

Discovery budget and validation budget are separate. Do not spend all validation effort on a fixed Top-N created before metrics.

1. Give every phrase in the frozen canonical keyword slate one primary comparable metric observation where the provider permits it.
2. Give 100% of metric-filled phrases with `0 < Volume <= 250` a `strict_multi_intitle_enumerated_v1` check. Use unchanged query syntax `explicit_intitle_per_token_v1` and tokenizer `nfkc_unicode_alnum_connectors_v1`, plus `ReducerPolicyVersion=verified_visible_title_lower_bound_v1`; quote every cleaned token, retain in-token `&`/`+`/`#`, and discard standalone `&`. Require typed booleans and bind each page URL to the strict query, frozen context, and continuous pagination offset. Count and deduplicate all operator-returned organic canonical URLs, then separately count unique URLs whose visible known titles contain every required token. A truncated title can support this verified lower bound only when all tokens are already visible, but it still cannot support exactness. At `VerifiedMatchingUniqueUrlCount >= T=floor(0.30×Volume)+1`, stop as `lower_bound_gt_0_30` with `LowerBoundBasis=verified_matching_unique_urls` and without a ratio; this is a one-sided high-supply rescue even if other titles have integrity issues. Below T, any mismatch, truncation, or unknown title remains a whole-query hold. Exact low supply still requires genuine exhaustion, a clean title audit, semantically consistent terminal evidence, and an absent next control; never filter questionable URLs out of an exact numerator. Stop on CAPTCHA, blocks, repeated page URLs, or repeated organic-result sets. The reducer rejects `Volume>250`; optional scale-lane title observations stay in a separate out-of-scope artifact. Raw v2.0.1 pages may be re-reduced without recollection because collection semantics are unchanged, but every derived artifact must retain or declare its reducer policy version. This is a coverage obligation, not a weighted sampling budget.
3. Repeat anomalous exact zero counts and every `provisional_strong` or `provisional_borderline` observation with the same method/context, preserving each dated observation; use the median only across compatible exact `StrictTitleSupplyRatio` runs. Unquoted-classic observations have zero reuse under this method and remain legacy-only; keep their batch-specific migration count in the audit ledger.
4. Give every `provisional_strong` and `provisional_borderline` phrase a current SERP check. Retain exact or lower-bound `provisional_high` outcomes as counterevidence; sample them only when task clarity or other evidence independently warrants it.
5. Give every admitted `narrow_product_value` family a current intent/SERP check and the cheapest permitted problem falsification; absence of problem/payment evidence stays pending, not zero.
6. Spend remaining SERP capacity across representative `scale_search` and `emerging_search` families, plus a title-supply/anomaly sample from scale search, preserving family and task diversity.
7. Use Ahrefs, Similarweb, competitor-page analysis, and expensive browser review later and selectively at keyword-family or domain level; do not spend them uniformly on every raw phrase.

If a provider limit interrupts enrichment, preserve the unfilled slate and resume it before declaring the active pool final. A `semantic_preview` or `provisional_family_longlist_view` may be shown, but it must not constrain the enrichment denominator and must not use `active-pool`, `title-supply-complete`, or `fully-ranked` in its filename, status, or title.

## Candidate-pool capacity

Aim for 15–30 distinct product families so the founder has genuine choice. Protect diversity across task types, user moments, implementation difficulty, and evidence maturity.

Suggested research allocation:

- 3–6 `deep_research` families;
- 5–10 `quick_test` families;
- 5–12 `observe` families;
- any number of `counterevidence_hold` records kept outside the active count.

Do not force weak terms into the pool. If fewer than 15 survive, report which roots/channels were not explored sufficiently and run another discovery allocation before lowering semantic quality.

The 15–30 target is applied only after lane routing and representative SERPs. It must not cap the canonical slate, the strict-title-supply-eligible set, or the versioned longlist.

When passed provisional-strong/borderline strict-title-supply families exceed 30, place the overflow in a `protected_title_supply_annex` rather than deleting it. The annex consumes validation capacity and remains part of the active research denominator.
