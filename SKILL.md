---
name: root-keyword-opportunity-research
description: 从版本化词根池出发，编排 Autocomplete、Google Trends、Google Ads、Semrush、Ahrefs、Similarweb 与实时 SERP 的高召回关键词机会发现；动态分配扩展和验证资源，完整覆盖严格多 intitle 标题供给枚举，隔离指标 cohort，并形成可追溯、分赛道的 research-only 产品族候选池。用户要求词根扩展、关键词研究、旧词重筛、跨来源比对、递归与停止判断或组装 15–30 个产品族时使用；不得把严格标题供给比率冒充经典 KGR，也不得把 SEO 指标当成需求、付款或开发许可。
---

# Keyword Opportunity Orchestrator

Method contract: `v2.0.2`.

Build a high-recall discovery system first, then spend validation effort selectively. Treat A–Z as the deterministic baseline, not the boundary of what can be discovered.

## Load context

1. Read workspace `AGENTS.md` and the project instructions it routes to.
2. Read the current company state before recommending or changing a candidate. Default to `research-only` when no permission exists.
3. Read [references/method-router.md](references/method-router.md) before choosing channels or allocating effort.
4. Read [references/stage-and-weight-routing.md](references/stage-and-weight-routing.md) before metric gating, strict title-supply allocation, active-pool construction, or ranking.
5. Read [references/evidence-and-metrics.md](references/evidence-and-metrics.md) before collecting metrics, comparing providers, or scoring.
6. Read [references/resource-allocation.md](references/resource-allocation.md) before recursion, stopping, or batch planning.
7. Read [references/output-contract.md](references/output-contract.md) before writing a batch, shortlist, or final report.
8. For live autocomplete collection, also use the installed `keyword-finder` Skill. For current SERP mapping, also use `opc-search-demand-mapper`. For product opportunity claims, also use `opc-opportunity-intelligence`.

## Non-negotiable separation

Maintain separate ledgers for `root_keyword_discovery`, `daily_keyword_radar`, and `candidate_search_validation`. Each keeps its own `task_mode`, `batch_id`, raw inputs, source channel, provenance, rejects, metrics, completion states, and conclusions.

Do not use daily-radar, forum, GitHub, Product Hunt, Toolify, rankings, reviews, official changes, or historical candidates to seed or secretly prioritize a root-first batch. An orchestrated report may compare separately produced lanes at the product-family layer, but must label their origins and must not present cross-lane overlap as independent discovery.

Do not change company candidate selection, validation permission, or development permission unless the founder explicitly decides.

## Workflow

### 1. Declare the batch before collection

Report `task_mode`, batch ID, registered root-pool version/hash, market, language, device, selected roots, channels, planned depth, initial resource allocation, and expected steps. Write the manifest before the first network call.

For root-first work, initial roots come only from the registered versioned pool. A secondary root requires a verified parent event and explicit recursion permission. Cross-channel phrases may become candidate keywords or proposed secondary roots, but never silently enter the canonical root pool.

### 2. Run the broad baseline

Run bidirectional autocomplete for every selected root: root before and after A–Z, digits, and the protected baseline question words. Preserve zero-result and failed queries. Use the workspace root-radar wrapper so raw collection does not create a metrics sheet prematurely.

Treat the current per-root budget of 120 as a compatibility safety limit, not a research optimum. The present baseline graph is about 87 initial queries per root; complete that inexpensive floor across the declared roots before concentrating deep-validation spend. Schedule and report coverage by direction and expansion kind so budget truncation cannot systematically starve prefix, digit, or question probes.

Do not semantically reject during collection. Normalize reversibly, deduplicate only as a derived view, and keep every raw occurrence with query, root, direction, expansion kind, market, language, device, time, and source.

### 3. Measure branching before narrowing

After the first pass, calculate lexical branching, semantic breadth, active-branch ratio, new-keyword rate, duplicate rate, opportunity density, and per-channel marginal gain. These diagnose where to spend the next unit of effort; they are not eligibility gates.

Classify branches as:

- `broad_high_yield`: many new terms across several task clusters;
- `broad_low_opportunity`: broad vocabulary but few concrete digital tasks;
- `narrow_high_value`: little further branching but a clear task and deliverable;
- `uncertain`: sparse, unfamiliar, or contradictory evidence needing a sample;
- `saturated_or_drifted`: repeated terms or intent outside the current family.

Never delete a commercially interesting narrow keyword merely because it cannot become a root. Root-pool fitness and product-candidate fitness are different decisions.

### 4. Allocate deeper discovery dynamically

Use A–Z to guarantee cheap coverage, then choose the next channel by the unanswered question:

- Google Trends Top/Rising: related concepts, recent emergence, and temporal shape;
- Google Ads discovery: semantic expressions and close variants not exposed by spelling expansion;
- Google related searches: adjacent search formulations and entities;
- Semrush/Ahrefs: keyword variants, competitor/page traffic terms, estimated scale and competition;
- Similarweb: traffic/click distribution, competing sites, geography or device hypotheses;
- YouTube/TikTok/platform autocomplete: platform-native wording when the task is native there;
- live SERP: current intent, supply, direct-tool saturation, brands, and unfinished task gaps.

Return a promising child to its originating channel first. Expand it across other channels only when a concrete unanswered question justifies the cost. Record whether a hit is `independent`, `propagated`, or `corroborating`.

For each materially different semantic cluster, choose representative branches; do not cap a broad root to two or three branches in total. Use a parent orchestration batch with separately traceable baseline and deepening child runs when the collection wrapper cannot vary per-root budgets inside one immutable batch.

### 5. Stop by marginal information gain

Budgets are safety limits, not evidence that a branch is complete. Budget exhaustion means `partial_budget_exhausted` with the remaining queue preserved.

Continue a branch while it produces new task clusters, useful expressions, or materially different evidence. Stop or sample when consecutive windows show low marginal gain, high duplication, stable clusters, or clear semantic drift. Record the observed metrics, window size, reason, and unvisited scope. Use flexible ranges from the resource reference; do not turn them into permanent hard gates.

### 6. Clean and promote after discovery breadth is visible

Apply the reversible three-way split: rule-pass, review, reject. Assert exact conservation and mutual exclusivity. Preserve ambiguous or unfamiliar phrases in review.

Before freezing the family slate, run a stratified false-negative audit across review and reject strata by root, reason, and semantic class. If a stratum contains a material rate of clear digital-task misses, reopen and re-review that entire stratum. Record the sample denominator, misses, and expansion decision; do not assume a clean rule is safe merely because conservation arithmetic passes.

Only a provenance-bound semantic promotion may enter metric enrichment. A promoted row needs `task_type`, `input`, `output`, `digital_deliverable`, and `disposition=promoted`. Game builds, physical repair, industrial parts, manuals, reviews, navigation, and local services stay review/rejected unless a concrete digital task and portable result are established.

### 7. Build the full family longlist and canonical keyword slate

Cluster all promoted phrases before any numeric shortlist. For every product family retain a natural primary phrase plus up to two standard materially different long-tail expressions. Add a protected `constraint_rescue` phrase beyond that limit whenever it is the only expression of a distinct input, format, error, batch, platform, safety, size, or workflow constraint. Preserve the rest as traceable aliases and record why each phrase was selected or omitted.

Freeze the full family longlist and canonical keyword slate before creating a 15–30 family active pool. Do not use implementation ease, diversity caps, Volume, KD, CPC, strict title-supply routing, or Trends to shrink the slate at this stage.

Before the final gate, call any convenience view a `semantic_preview` or `provisional_family_longlist_view`, never an active pool. It must not limit the denominator used for metric enrichment, strict title-supply enumeration, or representative SERP coverage.

### 8. Enrich the full slate and route metric lanes

Keep provider observations separate. A metric cohort requires market, language, device, source, match type, and checked date. Zero is a value; missing is missing. Preserve raw provider values, normalized values, unavailable values, extra columns, and conflicts.

Give every phrase in the canonical slate either a valid primary-cohort observation or an explicit same-cohort missing, unavailable, invalid, or conflict record before narrowing to an active pool. Route search phrases into `strict_title_supply_longtail`, `scale_search`, or `emerging_search`; maintain `narrow_product_value` as a separate product-research lane. A family may occupy multiple lanes without one lane erasing another.

Within each cohort produce independent Volume-desc, KD-asc, and CPC-desc views. Apply the 20% boundary as a soft review band. Check every metric-filled phrase with `0 < Volume <= 250` under method `strict_multi_intitle_enumerated_v1`, query syntax `explicit_intitle_per_token_v1`, tokenizer `nfkc_unicode_alnum_connectors_v1`, count method `paginated_deduplicated_organic_canonical_urls_with_displayed_title_integrity_audit`, and reducer policy `verified_visible_title_lower_bound_v1` before any active-pool claim. The collection method, query syntax, and tokenizer are unchanged from v2.0.1. Freeze and record `hl`, `gl`, `device=desktop`, `SearchType=google_web`, normalized integer `pws=0`, `filter=0`, `nfpr=1`, and checked date; different context keys are separate cohorts and cannot be merged or reused. Require schema booleans to be actual booleans. Bind every saved Google page URL to the exact strict query, frozen context, and continuous zero-based pagination offset. After NFKC, retain Unicode alphanumeric tokens and the in-token connectors `&`, `+`, and `#`; discard a standalone `&`. Emit every cleaned token as a quoted operator such as `intitle:"token"`. Paginate and first count deduplicated operator-returned organic canonical URLs, stripping display-tracking parameters while preserving business query parameters; separately count deduplicated `VerifiedMatchingUniqueUrlCount`, whose known displayed title visibly contains every required token. A truncated title may contribute to this verified lower bound only when every required token is already visible; the truncation remains an integrity issue and cannot support exactness. Use `T = floor(0.30 × Volume) + 1`. When `VerifiedMatchingUniqueUrlCount >= T`, record `lower_bound_gt_0_30` with `LowerBoundBasis=verified_matching_unique_urls` and leave `StrictTitleSupplyRatio` empty, even if other returned titles are mismatched, truncated, or unknown. Integrity flags remain visible as audit evidence but are not terminal for this one-sided rescue. This rescue proves only high supply from the verified subset; it never filters questionable URLs into an exact low count. If the verified count is below T, any mismatch, automatic or explicit truncation, or unknown title leaves the outcome `not_assessable_query_integrity`; all operator-returned URLs remain visible for audit. A block, CAPTCHA, repeated page URL, or repeated organic-result set is also not exhaustion. Accept exhaustion only with a terminal pagination state, a semantically consistent allowed end-of-results evidence code, an explicitly absent next control, and no title-integrity issue. Only that fully verified exhaustion yields an exact `StrictTitleSupplyRatio`; v2.0.2 does not relax exact low-supply inference. Reject this strict reducer for `Volume > 250`. Treat `<0.25`, `0.25–0.30`, and `>0.30` only as provisional routing bands. Do not call this ratio KGR. Raw v2.0.1 pages may be deterministically re-reduced because collection semantics did not change, but every derived artifact must record `ReducerPolicyVersion`; never silently relabel an old derived result. Any observation collected with classic unquoted `allintitle:` syntax or another method is legacy comparison only and has zero reuse under this method; preserve its actual method/query/count identity and record migration counts in the batch artifact. Never average or splice fields from different providers.

Do not claim that a batch has low title supply from a final-pool sample. Report the complete denominator from promoted phrases through exact, verified-title lower-bound, blocked, missing, unresolved integrity-hold, method-mismatch, and context-mismatch strict title-supply outcomes. Conservation is necessary but not sufficient for the active-pool gate: `require_all_assessable=true` is mandatory, every eligible phrase must be exact or `lower_bound_gt_0_30`, and any not-assessable outcome keeps `StrictTitleSupplyEligibleCoverageComplete=false`.

### 9. Validate Trends and live SERPs by lane

Store full Trends and SERP context at row level. A checked SERP is not a passed SERP. Only `SerpGateStatus=pass` under matching market, language, device, search type, date, intent group, and page type permits heuristic group ranking. Negative SERPs remain valuable counterevidence.

Apply weights only inside the lane and compatible cohort defined by the stage-and-weight reference. Before SERP review, the provisional strict title-supply bands are protected routing rules rather than a partial weighted score. A provisional-strong phrase always receives a current SERP check before it can be dropped from the search-acquisition pool.

Use Similarweb Global versus Semrush US only to form a `market_mismatch_hypothesis`; it cannot prove that Americans lack curiosity or replace US data.

### 10. Construct the diversified active research pool

Compare only inside compatible lanes and cohorts, then construct the active pool at product-family level. Cluster by shared user, moment, input, transformation, and deliverable—not merely by shared root or implementation library. Separate extraction, conversion, transcription, OCR, and segmentation when their completed jobs differ.

Set `ActivePoolEligible=true` only from inline evidence rows, never from caller-supplied aggregate counts or compatibility booleans. Recompute the canonical, strict-observation, SERP-plan, and SERP-observation SHA-256 values from their record arrays. Every canonical row uses `complete|partial|unavailable|invalid|conflict`, keeps `volume/kd/cpc` as a non-negative number or null, and lists exactly the null fields in `missing_fields`; a partial row may preserve Volume while KD/CPC remain missing. Derive the strict denominator from complete or partial rows whose observed Volume satisfies `0 < Volume <= 250`; the strict keyword-ID set must equal that set exactly. Require one complete compatible primary-metric cohort and bind the strict `hl/gl/device` to its language/market/device; require one strict query-context key, actual repeat-observation records for every exact provisional-strong/borderline or primary zero result, and zero not-assessable strict outcomes. Freeze a SERP plan whose plan IDs exactly match observation IDs and whose real context rows match the metric market/language/device; it must cover at least `min(30, family_total)` families, every protected strict-title-supply family, every `narrow_product_value` family, and every non-empty lane. SHA verification prevents stale or accidentally divergent summaries; it is not an immutable external receipt. When any derived gate is false, do not create an `active-pool` file, status, or report title.

Before writing an active pool, run `python3 scripts/validate_stage_gate.py <stage-summary.json>`. Treat a non-zero exit as a hard stop for active-pool naming and final-pool claims; preserve the preview and unresolved denominators instead.

Normally return 15–30 research-only product families across tiers: `deep_research`, `quick_test`, `observe`, and `counterevidence_hold`. Do not pad with garbage to hit a quota; if fewer survive, state the shortfall and which discovery branches remain unvisited. Preserve alternate phrases inside each family rather than manufacturing duplicate products or pages.

If passed provisional-strong/borderline strict-title-supply families alone exceed 30, keep a 15–30 comparison core plus a `protected_title_supply_annex`; the annex remains active search research and is not silently discarded to satisfy presentation capacity.

Keep every qualifying family in a versioned longlist even when only 15–30 appear in the active comparison pool. The active-pool size is a decision-aid target, not a deletion rule.

For every family include the strongest supporting evidence, strongest counterevidence, implementation shape, missing evidence, and cheapest falsification. Search data may prioritize research but never proves demand, payment, product choice, validation permission, or development permission.

## Conflict rule

Sources do not compete for universal authority. Each answers a typed question. Compare only observations that answer the same question under compatible scope. Otherwise preserve both and label the difference `scope_mismatch`, `temporal_mismatch`, `method_mismatch`, `propagated_overlap`, or `unresolved`.

When advice conflicts, retain the stable principle, mark its operating boundary, and test the uncertain parameter. Social or founder case studies may suggest tactics and priors, but do not become numeric gates or population success rates without a stable denominator.

## Completion language

Report every step as `pending`, `partial`, `complete`, `not_applicable`, or `blocked`, with evidence artifacts. Distinguish at least:

- `autocomplete_complete`;
- `multi_channel_discovery_complete`;
- `metric_enrichment_complete`;
- `serp_validation_complete`;
- `product_family_pool_complete`.

Represent each step structurally as `{status, planned, completed, failed, unvisited, reason, artifacts, reopen_condition}` rather than encoding counts inside free-form status strings.

Never claim the whole process is complete because A–Z finished, the budget was consumed, or metrics were filled.
