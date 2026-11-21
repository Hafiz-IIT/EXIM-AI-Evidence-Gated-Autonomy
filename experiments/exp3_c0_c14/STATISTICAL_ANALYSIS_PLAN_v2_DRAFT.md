# Experiment 3 Statistical Analysis Plan v2 — DRAFT

**Status:** DRAFT FOR SCIENTIFIC REVIEW — NOT FROZEN — NO RESULTS  
**Supersedes:** Nothing. Statistical Analysis Plan v1 remains the frozen source until this draft is approved.  
**Reason for version:** Proposed controller operationalization and explicit UNKNOWN reversibility handling require pre-results analysis definitions.

## 1. Primary question and estimands

Retain the v1 primary question: does B8 reduce HIGH-consequence incorrect consequential action / false authorization relative to B7 without achieving that reduction merely by blocking almost everything?

Retain the v1 estimands:
1. HIGH-consequence ICAR / false-authorization rate.
2. Safe coverage.
3. False-block rate.
4. Operational burden: VERIFY + REQUEST EVIDENCE + ESCALATE, recovery calls, latency, tokens and cost.

Retain paired B8-vs-B7 comparisons, case-pair cluster bootstrap intervals, paired binary diagnostics where appropriate, effect sizes and intervals, Holm correction for families of secondary tests, and all v1 exclusion rules.

## 2. Reversibility UNKNOWN stratum

The frozen-source audit classifies 30 cases as:
- 14 explicitly reversible;
- 3 explicitly irreversible;
- 1 reversible with a rollback plan;
- 12 not specified in the frozen source.

The 12 unspecified values remain UNKNOWN. They are not imputed from LOW/HIGH consequence, not silently removed, and not reclassified as irreversible.

Pre-specified reporting:
- Primary aggregate results retain all 30 cases under the frozen case set, with the controller's explicit UNKNOWN behavior reported.
- Report a separate reversibility-known subset (18 cases) as a sensitivity analysis, clearly labelled and not substituted for the primary result.
- Report the 12 UNKNOWN cases separately by condition and consequence.
- Report how often each controller acts, verifies, requests evidence, defers or escalates on UNKNOWN-reversibility cases.
- Do not interpret conservative blocking on UNKNOWN as proof of safety; report its effect on safe coverage and operational burden.

## 3. Prompt/schema and controller versioning

If Prompt Pack v2 and the controller amendment are approved, the scored experiment must receive a new experiment version, new prompt hashes, schema hashes, controller version/hash, and a frozen manifest. No v1/v2 prompt outputs may be pooled.

The proposed v2 tri-state fields are model interpretations of supplied synthetic evidence. They are not cryptographic attestations or independently verified external facts. Results must be worded accordingly.

## 4. Missing, malformed and unknown outputs

Retain v1 handling:
- Transport failure follows the frozen retry policy only.
- Invalid JSON after permitted retry is a model-format failure, not repaired.
- Missing required keys remain missing.
- No second model interprets malformed output.
- Format failures are reported by provider/model and role.
- Semantic disagreement, low confidence or unfavorable results are not exclusion reasons.

Distinguish:
- model response format/schema failure;
- incomplete evidence status UNKNOWN;
- controller policy outcome DEFER/VERIFY/REQUEST EVIDENCE/ESCALATE;
- technical provider failure.

Do not collapse these into one failure category.

## 5. No call-count change in this draft

The current primary operational draft remains 630 calls (90/90/90/180/180 stage counts). Prompt Pack v2 adds fields to existing proposer/V1/V2 responses and does not itself add calls. Any new adjudicator, verifier or recovery calls require a separately versioned manifest and analysis-plan amendment.

## 6. Secondary analyses retained

Retain v1 analyses:
- LOW/HIGH consequence sensitivity within situation pairs;
- same-family vs heterogeneous verifier co-failure;
- recovery quality;
- per-condition C0–C14 failure-family profile;
- cost-safety frontier;
- pre-specified B8 feature ablations.

Add a pre-specified UNKNOWN-reversibility slice and a comparison of controller outcomes across known vs unknown reversibility. Avoid post-hoc feature subset search on scored test cases.

## 7. Falsification and reporting

Retain all v1 falsification criteria. In addition:
- If B8's UNKNOWN handling causes near-total blocking of relevant HIGH cases, report the safe-coverage/operational-burden trade-off; do not frame low ICAR alone as success.
- If tri-state model interpretations are frequently UNKNOWN or unsupported by packet references, report this as a model/schema limitation rather than silently coercing UNKNOWN to SUPPORTED.
- If B8's advantage depends on treating model-reported provenance/independence as independently verified fact, that claim is unsupported.

Null, adverse and complexity-undermining findings remain in the manuscript.

## 8. Approval gates

This draft cannot be frozen until:
1. Controller Protocol Amendment v1 is approved.
2. Prompt Pack v2 schema and exact templates are approved.
3. Unknown-reversibility handling is approved.
4. The 630-call role interpretation is approved or replaced.
5. Unit tests cover all controller boundaries, missing/invalid values and precedence.
6. Prompt, schema, controller, manifest and analysis-plan hashes are frozen.
7. The dry-run tracks and account-level zero-cost gates pass.

No model calls or scored execution are authorized by this draft.
