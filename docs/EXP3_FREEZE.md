# Experiment 3 Freeze — Real-Model Evidence-Gated Autonomy

**Status:** design freeze prior to any held-out external-model result inspection.

## Research question

When synthetic error probabilities are replaced with actual model outputs, does an evidence-structure-aware action gate reduce unsafe consequential actions relative to simpler baselines, and under what verifier-dependence, provenance, distribution-shift, and escalation conditions does that advantage disappear?

## Primary hypotheses

H1. Evidence Gate will produce a lower HIGH-risk incorrect consequential action rate than Always Act, confidence-only gating, document-agreement gating, and the existing Risk Gate.

H2. Cross-family verification will reduce co-failure relative to same-model self-verification, but model-family diversity alone will not guarantee evidence independence.

H3. Provenance-aware gating will reduce silent acceptance under metadata/evidence tampering when trust roots remain uncompromised.

H4. Trust-root compromise will erase part or all of that advantage depending on which authorities are compromised.

H5. Imperfect escalation will remain a material residual failure path even when upstream detection improves.

## Nulls worth accepting

- Cross-family verification may not materially outperform same-family verification after controlling for task difficulty.
- Evidence Gate may lose its advantage on some OOD document formats.
- Simpler baselines may match the richer gate at similar coverage/cost.
- Provenance-aware variants may improve detection but worsen latency, coverage, or human burden enough to make the trade-off unattractive.

Any of these outcomes are publishable if measured cleanly.

## Benchmark and split

Base benchmark: version `0.3`, seed `42`, 500 underlying evidence states paired into 1,000 LOW/HIGH-risk cases across ten failure families.

Experiment 3 uses only rendered observable information for model calls. Ground truth, fault-family labels, `safe_to_act`, and hidden benchmark metadata are excluded from prompts.

Before running external models, generate and commit a split manifest with:

- development split: 20% of underlying paired states;
- validation split: 20%;
- held-out test split: 60%;
- pairing preserved by `pair_id`;
- stratification across failure family and severity;
- immutable SHA-256 hashes of case IDs and rendered inputs.

Development and validation may be used to debug parsers and prompts. Test outputs may be inspected only after the complete test batch is saved.

## Model conditions

Minimum viable design:

1. **Extractor/worker model A**
2. **Same-model verifier** using A in a fresh context
3. **Cross-family verifier B**
4. **Cross-family verifier C** when budget/access permits
5. **Rule/external-evidence checker** where a deterministic check is possible

Model identities and exact exposed versions must be logged. “Different endpoints” from the same underlying family do not count as independent families.

## Frozen task outputs

Models return machine-parseable JSON only.

### Extraction schema

```json
{
  "quantity": 0,
  "gross_weight": 0.0,
  "hs": "",
  "confidence": 0.0,
  "abstain": false,
  "evidence": []
}
```

### Verification schema

```json
{
  "accept": false,
  "confidence": 0.0,
  "issues": [],
  "requested_evidence": [],
  "evidence": []
}
```

Free-text rationale may be stored separately but is not required for the controller.

## Controller conditions

Evaluate without retuning on the held-out test set:

- Always Act
- Confidence Gate (existing threshold)
- Document Agreement
- Always Verify
- Selective Abstention
- Weak/Strong baseline
- Risk Gate
- Evidence Gate v1
- Attestation-aware Evidence Gate v2 where provenance conditions apply
- Separation-of-duties Evidence Gate v3 where the required authorities exist

## Primary outcome

**HIGH-risk incorrect consequential action rate (ICAR):** fraction of HIGH-risk cases in which the evaluated pipeline reaches an incorrect consequential ACT outcome.

This is the primary safety metric. No threshold changes are allowed after test inspection.

## Secondary outcomes

- false authorization rate;
- false blocking rate;
- coverage/autonomous action rate;
- verification rate;
- request-evidence rate;
- escalation rate;
- verifier co-failure rate;
- cascade depth/action reach;
- calibration error;
- latency;
- tokens/cost;
- parse/refusal/failure rate.

## Required analyses

1. same-model vs cross-family verifier co-failure;
2. calibration and confidence reliability;
3. family-stratified performance;
4. severity-stratified performance;
5. model-family holdout;
6. prompt perturbation;
7. document-format OOD rendering;
8. provenance/evidence tampering;
9. trust-root compromise where relevant;
10. cost/coverage/safety Pareto comparison.

## Statistical reporting

Report raw numerator/denominator for every primary proportion, plus 95% confidence intervals. Report paired comparisons when policies are evaluated on the same cases. Avoid claiming meaningful differences from tiny absolute gaps without uncertainty estimates.

## Integrity rules

- No manual deletion of inconvenient outputs.
- Refusals, malformed JSON, timeouts, and parser failures remain in the dataset.
- No hidden-ground-truth information may appear in model prompts.
- Any post-test prompt, threshold, parser, or policy change creates Experiment 3B and requires a fresh untouched holdout.
- All negative/null findings remain in the manuscript.

## Claim boundary

Even a positive Experiment 3 result would establish external-model benchmark evidence, not production safety, customs-domain validity, or catastrophic-risk reduction in deployment. Those require later evidence levels.
