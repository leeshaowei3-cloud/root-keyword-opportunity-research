# Release notes

## v2.0.2 — verified-title high-supply rescue

This patch keeps collection method `strict_multi_intitle_enumerated_v1`, query syntax `explicit_intitle_per_token_v1`, tokenizer `nfkc_unicode_alnum_connectors_v1`, and the frozen Google context unchanged. It adds `ReducerPolicyVersion=verified_visible_title_lower_bound_v1` so derived semantics are reproducible independently of the raw collection identity.

The reducer continues to count and retain every operator-returned organic canonical URL. It also deduplicates `VerifiedMatchingUniqueUrlCount`: URLs whose known displayed titles visibly contain every required token. A truncated title may contribute to this verified subset only when all required tokens are already visible; truncation remains an integrity issue for exactness. When the verified count reaches `T=floor(0.30×Volume)+1`, the reducer may emit `lower_bound_gt_0_30` with `LowerBoundBasis=verified_matching_unique_urls`, even if other returned titles are mismatched, truncated, or unknown. This is only a one-sided proof of high supply and never produces a ratio.

The exact path remains fail-closed. Exact low-supply inference still requires genuine pagination exhaustion and a clean displayed-title audit for the full operator-returned unique URL set. If the verified count stays below T, any mismatch, truncation, or unknown title remains `not_assessable_query_integrity`; questionable URLs may never be filtered out to manufacture a low count.

Compatible v2.0.1 raw pages can be deterministically re-reduced without recollection because collection semantics did not change. Existing derived artifacts retain their original policy identity; a v2.0.2 re-reduction must write a new policy-versioned artifact rather than silently relabeling the old result.

This is a research-method patch. It does not grant product selection, validation, development, or release permission.

## v2.0.1 — strict multi-intitle title-supply enumeration

This patch introduces method `strict_multi_intitle_enumerated_v1`. Its exact metric is `StrictTitleSupplyRatio`; it is not classic KGR. Query syntax `explicit_intitle_per_token_v1` quotes every cleaned token. Tokenizer `nfkc_unicode_alnum_connectors_v1` retains Unicode alphanumerics plus in-token `&`, `+`, and `#` after NFKC, while discarding standalone `&`.

The method counts and deduplicates operator-returned organic canonical URLs, removing common display-tracking parameters while preserving business parameters. Displayed titles are then an integrity audit, not a count filter: any mismatch, explicit or detected Unicode truncation, or unknown title holds the whole observation. Its URL count remains visible for audit, but it produces no ratio or low-supply inference. Typed schema booleans and each saved page URL's query, context, and continuous pagination offset are validated. Exact exhaustion requires an explicit terminal state, semantically consistent end-of-results evidence, and an absent next control. Short-terminal evidence uses the raw organic result-card count, not the deduplicated URL numerator, so repeated URLs cannot manufacture a short final page. A non-exhausted enumeration stops at `T=floor(0.30×Volume)+1` as `lower_bound_gt_0_30`, with no ratio. CAPTCHA/block, repeated page URLs, and repeated non-empty organic result sets are non-assessable. The strict reducer rejects `Volume>250`, and legacy/method-mismatch outputs preserve their actual evidence identity.

Every observation freezes `hl`, `gl`, desktop device, `SearchType=google_web`, `pws=0`, `filter=0`, `nfpr=1`, and checked date into a query-context key. Counts from different keys are incompatible and cannot be merged or reused.

The `<0.25`, inclusive `0.25–0.30`, and `>0.30` ranges are retained only as provisional routing bands. The eight existing unquoted-classic observations are retained for legacy comparison but have reuse `0/8` under the new method. Offline tests cover tokenization, compound quoting, tracking-aware URL deduplication, title integrity, exact exhaustion, boundary behavior, early stopping, blocks, legacy-method rejection, and stage-gate conservation.

The active-pool gate now accepts inline evidence records rather than aggregate self-reports. It recomputes record-array SHA-256 values and derives the eligible keyword-ID set from canonical `complete|partial|unavailable|invalid|conflict` observations. Volume/KD/CPC remain independent non-negative-or-null fields with an exact `missing_fields` ledger; partial rows with observed Volume remain in the strict denominator. The gate enforces one complete primary-metric cohort, binds strict `hl/gl/device` to its language/market/device, and rejects `repeat_confirmed` or `context_compatible` booleans as substitutes for evidence. Exact provisional-strong/borderline and primary zero observations require separately identified same-context exact repeats. The SERP plan and observation ID sets must match exactly; the real observation contexts must match the metric market/language/device, share one date, and cover at least `min(30, family_total)`, every protected title-supply family, every narrow-product family, and every non-empty lane. Conservation still records every eligible phrase, but any missing enumeration, block, query-integrity hold, method/context mismatch, missing repeat, or insufficient SERP coverage prevents `ActivePoolEligible`.

The release contains 69 offline regression tests: 30 for strict title-supply reduction and 39 for the fail-closed stage gate. The SHA contract catches stale or accidentally divergent local summaries; it is not presented as an immutable receipt against an actor with write access.

This is a research-method patch. It does not grant product selection, validation, development, or release permission.
