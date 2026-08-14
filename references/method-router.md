# Method router

## Principle

Maximize recall before expensive validation. Route each source to the question it can answer; do not create a global source hierarchy.

| Question | Primary method | What it cannot prove |
|---|---|---|
| How do people phrase the root? | bidirectional autocomplete, platform autocomplete | volume, payment, product gap |
| What adjacent concepts are emerging? | Google Trends Top/Rising | absolute volume, durable demand |
| What semantic expressions did spelling expansion miss? | Google Ads discovery | exact volume for a new term, product value |
| What keywords/pages/sites appear to receive traffic? | Semrush, Ahrefs, Similarweb | actual first-party traffic or payment |
| What is the current search intent and supply? | live SERP | willingness to pay |
| Is there a concrete paid problem? | real inputs, complaints, workarounds, pricing, payment test | search scalability |

## Discovery lanes

### Root-first lane

- Initial seeds: registered versioned roots only.
- Expansion: A–Z/digits/questions in both directions, then root-originated related channels.
- Recursive roots: verified natural child plus explicit allowed record.
- Forbidden seed sources: daily radar, forums, GitHub, rankings, historical candidates, official-change feeds.

### External-signal lane

- Starts from dated external change, complaint, launch, community signal, or trend event.
- Must use its own task mode and batch.
- May later be compared with root-first at family level, never relabeled as root-first discovery.

### Candidate-validation lane

- Starts only after the founder selects a candidate or explicitly requests research on it.
- Uses current SERP, official facts, user problems, alternatives, payment evidence, and falsification tests.
- Does not backfill discovery independence.

## Channel escalation

1. Run the deterministic A–Z baseline broadly.
2. Measure branch yield and semantic breadth.
3. Use Trends for broad/fast-changing branches.
4. Use Ads discovery for semantically sparse or synonym-heavy branches.
5. Inspect competitor/page traffic words when a concrete task or site appears.
6. Use platform autocomplete only for platform-native user moments.
7. Spend live SERP effort on task-shaped terms and a deliberate sample of uncertain branches.
8. Use real problem/payment evidence only after product-family formation or founder-directed validation.

## Metric timing and lane routing

Use this order; do not turn it into a keyword-level Top-N funnel:

`semantic promotion -> product-family clustering -> full canonical keyword slate -> primary metric cohort for the full slate -> strict-title-supply/scale/emerging/narrow-value lane routing -> Trends and live SERP -> active research pool`

- `StrictTitleSupplyRatio` is an early, provisional routing observation for the complete eligible long-tail lane, not classic KGR and not a post-hoc audit of phrases that survived another ranking. Under `ReducerPolicyVersion=verified_visible_title_lower_bound_v1`, a deduplicated verified-title subset may also prove only `lower_bound_gt_0_30` with `LowerBoundBasis=verified_matching_unique_urls`; it never creates an exact ratio or a low-supply inference.
- Volume, KD, and CPC may describe and route phrases only after semantic promotion; they do not decide whether a phrase expresses a real digital task.
- Trends has high weight only in the emerging lane and a modest stability role elsewhere.
- A current SERP is the final search-acquisition gate. It may defeat a numeric score, but cannot prove payment or product demand.
- Product/problem evidence is scored separately from search acquisition and cannot be backfilled with SEO metrics.
- Build the 15–30 family pool only after the full canonical slate has been routed. Keep overflow, counterevidence, and every provisionally qualifying strict-title-supply phrase in the versioned longlist.

Never claim a batch-wide absence of low-title-supply phrases from an active-pool sample. The denominator must cover every metric-filled canonical phrase with `0 < Volume <= 250`. Only `strict_multi_intitle_enumerated_v1` observations are compatible, and their derived artifacts must identify the reducer policy. v2.0.2 leaves collection method, query syntax, and tokenizer unchanged, so compatible v2.0.1 raw pages may be re-reduced; old derived results remain versioned evidence and must not be silently relabeled. Unquoted-classic observations are never reused under this method and remain legacy comparison only; preserve their actual count in the batch migration ledger.

## Propagation labels

- `independent`: the source produced the term without being fed that term from another source.
- `propagated`: a term from source A was fed to source B and then returned.
- `corroborating`: source B independently exposes a compatible observation about the same term.
- `derived`: normalization, clustering, or inference created the record.

Never count propagated hits as independent multi-source discovery.

## Conflict handling

- Same provider and same cohort: reconcile duplicates and reject conflicting duplicate values.
- Different market/device/date/match/provider: retain separate observations.
- Global stronger than US: write a market-distribution hypothesis, not a US-demand conclusion.
- High volume and hostile SERP: retain both; discovery strength does not override supply counterevidence.
- Low volume and clear costly task: retain as a narrow-value hypothesis; do not delete because it cannot branch.
- High branching and low task density: retain as a hub-root candidate, not automatically as a product.
