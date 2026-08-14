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

For any KGR claim, also lead with the coverage funnel:

`canonical slate = metric_valid + metric_missing + metric_unavailable + metric_invalid + metric_conflict`

`promoted phrases -> product families -> canonical keyword slate -> metric-valid phrases -> 0<Volume<=250 phrases -> allintitle-checked phrases -> KGR bands + not-assessable/invalid counts`

Label coverage `complete`, `partial`, or `sampled`. Never generalize a sample result to the batch.

Also report semantic false-negative audit coverage by stratum and canonical-slate selection coverage, including every `constraint_rescue` phrase and omission reason.

## Product-family record

One row per completed job, not one row per spelling variant:

`FamilyId, Tier, PrimaryKeyword, SecondaryKeywords, User, Moment, Input, Transformation, Output, DigitalDeliverable, SourceTaskModes, SourceBatchIds, DiscoveryChannels, PropagationLabels, EvidenceIds, ArtifactRefs, IndependentSourceCount, SearchLanes, WeightVersion, ScoreRecords, RankStability, KgrCoverageStatus, MetricObservations, TrendObservations, SerpObservations, ProductEvidenceCoverage, SearchSupport, SearchCounterevidence, ProductSupport, ProductCounterevidence, ImplementationShape, Difficulty, KillRisk, MissingEvidence, CheapestFalsification, ResearchStatus, SelectionPermission, ValidationPermission, DevelopmentPermission`

Keep every provider observation as a child record or separate row. Do not compress incompatible cohorts into one V/KD/CPC triplet. Every evidence record carries `EvidenceDomain=search_intent_supply|product_problem|product_payment|implementation|risk`; SERP-only evidence cannot raise product-evidence coverage.

Compute `IndependentSourceCount` from event lineage. Propagated hits, historical overlap, normalization, and repeated observations from the same source event do not increase it. Preserve keyword-level SERP pass/hold/fail observations; never overwrite mixed family evidence with one optimistic family status.

## Tier semantics

- `deep_research`: concrete task/deliverable plus enough search or market evidence to justify expensive investigation; not a validation license.
- `quick_test`: clear task with a cheap falsification, but important demand, supply, or implementation uncertainty remains.
- `observe`: plausible task or root branch needing more discovery or evidence.
- `counterevidence_hold`: current evidence argues against spending more, but the record and rejection reason remain preserved.

## Required report behavior

- Provide a diversified pool, normally 15–30 families, unless quality evidence supports fewer.
- If passed strong/borderline KGR families exceed that capacity, add a `protected_kgr_annex` and keep it active rather than truncating coverage.
- Show supporting and negative evidence together.
- Explain provider, geography, match, device, and date differences near every numeric comparison.
- Mark incomplete steps one by one.
- Separate historical carry-forward, current independent discovery, and pending exact validation.
- Do not assign a global numeric rank across incompatible cohorts.
- Provide separate `kgr_longtail`, `scale_search`, `emerging_search`, and `narrow_product_value` views; never merge their weights into one global rank.
- Before the machine gate passes, call the artifact `semantic_preview` or `provisional_family_longlist_view`; never call it an active pool. An active pool is always metric-routed, KGR-covered, and representative-SERP-gated.
- Do not call a family selected, validated, or build-approved without the corresponding founder/company gate.

Require `ActivePoolEligible, CanonicalSlateFrozen, PrimaryMetricObservationCoverageComplete, KgrEligibleCoverageComplete, RepresentativeSerpCoverageComplete` in the summary. `ActivePoolEligible` is true only when all four component gates are true.

If a report's denominator, metric routing, or completion claim is later found invalid, mark it `superseded` or `withdrawn` with the reason and replacement artifact. Do not silently overwrite the conclusion while leaving the old report looking current.

## Backup and re-screening

When the founder asks to start fresh, preserve previous batches unchanged. Create a dated inventory plus a recoverable local snapshot or copy, record hashes, and verify it can be read. Record `AllowedInputs` and `ForbiddenInputs` for the new batch so old directories cannot enter through a glob. Run the new batch without reading old keyword content or using old candidates as seeds or priorities.

Freeze the new family list before checking historical overlap. A later old-batch synonym becomes labeled `historical_carry_forward`; it does not increase independent-source count, inherit old metrics, replace the new primary keyword, or create a duplicate family.

When re-screening historical keywords under a newer process, retain their original source, provider cohort, checked date, old conclusion, and missing steps. Do not rewrite them as current independent discoveries or inherit metrics from a shorter, reordered, or synonymous phrase.

Maintain a branch-decision ledger with `RootOrBranch, RootPoolFitness, ProductCandidateFitness, Channel, WindowMetrics, CostUnit, StopReason, RemainingUnvisited, ReopenCondition, EvidenceIds`. Root fitness and candidate fitness are separate: a narrow valuable task may stop branching and still advance to family research.
