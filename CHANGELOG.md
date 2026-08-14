# Changelog

## 2.0.2

- Keep `strict_multi_intitle_enumerated_v1`, `explicit_intitle_per_token_v1`, and `nfkc_unicode_alnum_connectors_v1` unchanged; add `ReducerPolicyVersion=verified_visible_title_lower_bound_v1` to version derived semantics.
- Add `VerifiedMatchingUniqueUrlCount`, deduplicated from known displayed titles in which every required token is visible. A visibly complete but truncated title may support this lower bound while remaining ineligible for exactness.
- Permit `lower_bound_gt_0_30` when the verified count reaches `T=floor(0.30×Volume)+1`, even if other returned titles have integrity issues; record `LowerBoundBasis=verified_matching_unique_urls` and never calculate a ratio for this outcome.
- Keep exact low-supply inference fail-closed: genuine exhaustion and a clean full title audit remain mandatory, and questionable URLs cannot be filtered away to reduce an exact numerator.
- Allow compatible v2.0.1 raw pages to be deterministically re-reduced, while requiring old and new derived artifacts to retain their reducer policy identity rather than being silently relabeled.

## 2.0.1

- Add `strict_multi_intitle_enumerated_v1` and name its exact metric `StrictTitleSupplyRatio`; explicitly prohibit calling it classic KGR.
- Use query syntax `explicit_intitle_per_token_v1` and tokenizer `nfkc_unicode_alnum_connectors_v1`; quote every cleaned token, preserve in-token `&`/`+`/`#`, and discard standalone `&`.
- Count and deduplicate operator-returned organic canonical URLs before auditing displayed-title integrity; remove common display-tracking parameters while preserving business parameters.
- Freeze `hl`, `gl`, desktop, Google Web, `pws=0`, `filter=0`, `nfpr=1`, and checked date; forbid count reuse across different context keys.
- Record genuine exhaustion as exact; stop at `T=floor(0.30×Volume)+1` as `lower_bound_gt_0_30` without inventing a ratio.
- Stop immediately on CAPTCHA/block, reject repeated page URLs and repeated organic-result sets as exhaustion, require explicit terminal evidence, and auto-hold ellipsized or mismatched displayed titles rather than silently undercounting.
- Keep all eight existing unquoted-classic observations as legacy comparison with reuse `0/8`.
- Preserve `<0.25`, inclusive `0.25–0.30`, and `>0.30` only as provisional routing bands.
- Require zero missing, blocked, query-integrity, and method-mismatch outcomes before strict-title coverage can pass the active-pool gate; conservation alone is insufficient.
- Bind the strict eligible denominator and keyword-ID set to canonical complete/partial metric rows with observed `0<Volume<=250`; preserve Volume/KD/CPC independently with an exact missing-field ledger and require one complete primary-metric cohort.
- Bind strict `hl/gl/device` to the primary metric language/market/device and fail closed on cross-cohort title-supply evidence.
- Replace `repeat_confirmed` and `context_compatible` booleans with uniquely identified repeat observations and complete SERP context rows; derive repeat confirmation, provider-context compatibility, family coverage, and lane coverage.
- Recompute SHA-256 over canonical, strict, SERP-plan, and SERP-observation record arrays; document that this detects stale or divergent summaries rather than providing an immutable external receipt.
- Require SERP plan/observation ID equality and coverage of `min(30, family_total)`, every protected title-supply family, every narrow-product family, and every non-empty lane.
- Reject non-boolean schema flags, non-contiguous or cross-context Google page URLs, contradictory terminal evidence, and `Volume>250`; preserve the actual identity of legacy method-mismatch observations.
- Use raw organic result-card count, rather than deduplicated URL count, to validate short terminal pages.
- Add 69 offline tests for query construction, tokenizer edge cases, URL canonicalization, title integrity, deduplication, terminal-card semantics, early stopping, blocks, legacy-method rejection, partial metrics, cross-cohort rejection, repeat observations, metric/SERP contexts, and fail-closed gate conservation.

## 2.0.0

- Delay narrowing until the full canonical slate has metric and KGR coverage.
- Add lane-specific routing, stage-gate validation, false-negative auditing, and research-only permission boundaries.
