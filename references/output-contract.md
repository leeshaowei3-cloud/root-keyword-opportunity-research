# Output contract

## Batch summary

Lead with:

- task mode and batch ID;
- root-pool version/hash and selected roots;
- market, language, device;
- channels run and propagation labels;
- planned versus consumed effort;
- per-step completion state;
- raw, review, reject, promotion, metrics, Trends, SERP, and family artifacts;
- conservation checks and unresolved conflicts.

For any strict title-supply claim, also lead with the coverage funnel:

`canonical slate = metric_complete + metric_partial + metric_unavailable + metric_invalid + metric_conflict`

`promoted phrases -> product families -> canonical keyword slate -> metric-valid phrases -> 0<Volume<=250 phrases -> exact_exhausted + lower_bound_gt_0_30 + missing/blocked/query-integrity/method-mismatch -> provisional strong/borderline/high`

For every strict title-supply summary, report method, reducer-policy and tokenizer versions, exact query syntax, count method, frozen `hl`/`gl`/desktop/`google_web`/`pws=0`/`filter=0`/`nfpr=1`/checked-date context and its key, operator-returned unique URL count, `VerifiedMatchingUniqueUrlCount`, `LowerBoundBasis=verified_matching_unique_urls` for a verified lower-bound outcome, exact count, `lower_bound_gt_0_30` count, CAPTCHA/block/loop stops, query-integrity holds, method/context mismatches, and missing observations. Different context keys stay in separate cohorts and cannot share a count. A single displayed `allintitle:` estimate is legacy-only; report the batch-specific classic denominator and strict-method reuse count in the migration ledger. Never label `StrictTitleSupplyRatio` as KGR.

Label coverage `complete`, `partial`, or `sampled`. Never generalize a sample result to the batch.

Also report semantic false-negative audit coverage by stratum and canonical-slate selection coverage, including every `constraint_rescue` phrase and omission reason.

## Product-family record

One row per completed job, not one row per spelling variant:

`FamilyId, Tier, PrimaryKeyword, SecondaryKeywords, User, Moment, Input, Transformation, Output, DigitalDeliverable, SourceTaskModes, SourceBatchIds, DiscoveryChannels, PropagationLabels, EvidenceIds, ArtifactRefs, IndependentSourceCount, SearchLanes, WeightVersion, ScoreRecords, RankStability, StrictTitleSupplyCoverageStatus, MetricObservations, TrendObservations, SerpObservations, ProductEvidenceCoverage, SearchSupport, SearchCounterevidence, ProductSupport, ProductCounterevidence, ImplementationShape, Difficulty, KillRisk, MissingEvidence, CheapestFalsification, ResearchStatus, SelectionPermission, ValidationPermission, DevelopmentPermission`

Keep every provider observation as a child record or separate row. Do not compress incompatible cohorts into one V/KD/CPC triplet. Every evidence record carries `EvidenceDomain=search_intent_supply|product_problem|product_payment|implementation|risk`; SERP-only evidence cannot raise product-evidence coverage.

Compute `IndependentSourceCount` from event lineage. Propagated hits, historical overlap, normalization, and repeated observations from the same source event do not increase it. Preserve keyword-level SERP pass/hold/fail observations; never overwrite mixed family evidence with one optimistic family status.

## Tier semantics

- `deep_research`: concrete task/deliverable plus enough search or market evidence to justify expensive investigation; not a validation license.
- `quick_test`: clear task with a cheap falsification, but important demand, supply, or implementation uncertainty remains.
- `observe`: plausible task or root branch needing more discovery or evidence.
- `counterevidence_hold`: current evidence argues against spending more, but the record and rejection reason remain preserved.

## Required report behavior

- Provide a diversified pool, normally 15–30 families, unless quality evidence supports fewer.
- If passed provisional-strong/borderline strict-title-supply families exceed that capacity, add a `protected_title_supply_annex` and keep it active rather than truncating coverage.
- Show supporting and negative evidence together.
- Explain provider, geography, match, device, and date differences near every numeric comparison.
- Mark incomplete steps one by one.
- Separate historical carry-forward, current independent discovery, and pending exact validation.
- Do not assign a global numeric rank across incompatible cohorts.
- Provide separate `strict_title_supply_longtail`, `scale_search`, `emerging_search`, and `narrow_product_value` views; never merge their weights into one global rank.
- Before the machine gate passes, call the artifact `semantic_preview` or `provisional_family_longlist_view`; never call it an active pool. An active pool is always metric-routed, strict-title-supply-covered, and representative-SERP-gated.
- Do not call a family selected, validated, or build-approved without the corresponding founder/company gate.

Require `ActivePoolEligible, CanonicalSlateFrozen, PrimaryMetricObservationCoverageComplete, StrictTitleSupplyEligibleCoverageComplete, RepresentativeSerpCoverageComplete` in the summary. `ActivePoolEligible` is true only when all four component gates are derived as true from inline records.

- Canonical rows carry `keyword_id, family_id, metric_status, volume, kd, cpc, missing_fields, lanes, metric_context`; `metric_context` contains `market, language, device, provider, match_type, checked_date`. Status is `complete|partial|unavailable|invalid|conflict`. Numeric fields are non-negative numbers or null, and `missing_fields` exactly equals the null field set. A partial row may retain observed Volume while KD/CPC remain missing; it is still strict-title eligible when `0<Volume<=250`. The validator derives all counts, family/lane sets, the eligible denominator, and the single compatible metric context from these rows.
- Strict rows carry `keyword_id, observation_id, outcome, count, context, repeat_observations`. Repeat rows have their own globally unique observation IDs, outcomes, counts, and the same full context. A `repeat_confirmed` boolean is forbidden. Strict keyword IDs must equal the complete/partial metric rows with observed `0<Volume<=250` exactly, not merely match a caller-reported count. Their `hl/gl/device` must match the metric language/market/device.
- SERP plan rows carry `plan_id, keyword_id`; SERP observation rows carry matching `plan_id, status, context`. The context contains `market, language, device, search_type, checked_date, intent_group, page_type`; a `context_compatible` boolean is forbidden. Derive pass/hold/fail, family coverage, and lane coverage from the rows.
- Recompute SHA-256 over each record array using UTF-8 canonical JSON with sorted keys, compact separators, and retained row order. Emit both claimed and computed hashes. This detects stale or accidentally divergent summaries, not a malicious rewrite by someone with write access.

A zero-sized SERP plan, non-matching plan/observation IDs, any nonzero not-assessable strict outcome, missing required repeat, denominator/ID-set mismatch, mixed metric or strict context, incompatible SERP context, or insufficient protected-family/lane coverage makes the corresponding gate false. Conservation alone cannot satisfy a gate.

If a report's denominator, metric routing, or completion claim is later found invalid, mark it `superseded` or `withdrawn` with the reason and replacement artifact. Do not silently overwrite the conclusion while leaving the old report looking current.

## Backup and re-screening

When the founder asks to start fresh, preserve previous batches unchanged. Create a dated inventory plus a recoverable local snapshot or copy, record hashes, and verify it can be read. Record `AllowedInputs` and `ForbiddenInputs` for the new batch so old directories cannot enter through a glob. Run the new batch without reading old keyword content or using old candidates as seeds or priorities.

Freeze the new family list before checking historical overlap. A later old-batch synonym becomes labeled `historical_carry_forward`; it does not increase independent-source count, inherit old metrics, replace the new primary keyword, or create a duplicate family.

When re-screening historical keywords under a newer process, retain their original source, provider cohort, checked date, old conclusion, and missing steps. Do not rewrite them as current independent discoveries or inherit metrics from a shorter, reordered, or synonymous phrase.

Maintain a branch-decision ledger with `RootOrBranch, RootPoolFitness, ProductCandidateFitness, Channel, WindowMetrics, CostUnit, StopReason, RemainingUnvisited, ReopenCondition, EvidenceIds`. Root fitness and candidate fitness are separate: a narrow valuable task may stop branching and still advance to family research.
