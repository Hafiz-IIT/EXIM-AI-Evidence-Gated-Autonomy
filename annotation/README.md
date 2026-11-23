# Independent Human Annotation Protocol v1

## Purpose

Create an independently judged sample of benchmark v0.4 cases to test whether scenario content actually supports the intended evidence, provenance, freshness and action-consequence labels. This is a validation instrument, not a claim that the benchmark is already human-validated.

## Sampling and blinding

- Default sample: 10 underlying pairs per each of 14 scenario families; both LOW- and HIGH-risk action variants are included (280 annotation rows).
- The shareable packet is shuffled and contains only an opaque annotation ID, action context and observable evidence JSON.
- It excludes case ID, pair ID, scenario family, severity, fault description, gold labels and fingerprints.
- Keep `results/annotation_validation/private/annotation_key.csv` restricted to the study owner. Never send it to annotators.
- Each case should be independently reviewed by at least two annotators. Three is preferable for a small pilot.
- Annotators must not see one another's labels before submission. Do not use model-generated labels as ground truth.

## Label rubric

### Evidence sufficiency
- `SUFFICIENT`: the provided documents contain the required information to justify the proposed action.
- `INSUFFICIENT`: a required document or material field is absent or unusable.
- `AMBIGUOUS`: the documents do not support a confident determination.

### Source integrity
- `VALID`: the provided provenance and document instances are internally consistent.
- `INVALID`: provenance is corrupted, inconsistent or otherwise untrustworthy.
- `UNCERTAIN`: the available record is insufficient to judge integrity.

### Document freshness
- `CURRENT`: no material staleness issue is visible.
- `STALE`: a relevant document is out of date for the proposed action.
- `UNKNOWN`: freshness cannot be established from the packet.

### Cross-document consistency
- `CONSISTENT`: material fields agree across relevant documents.
- `CONFLICT`: one or more material fields conflict.
- `NOT_ASSESSABLE`: there is not enough evidence to compare.

### Recommended disposition
- `ACT`: evidence is sufficient, integrity is acceptable, freshness is current, and material fields are consistent for this action.
- `DEFER`: a required evidence item is missing, stale, invalid or materially contradictory; do not execute until corrected.
- `ESCALATE`: evidence is ambiguous, integrity/freshness cannot be determined, or consequence requires independent human judgment.

Also provide confidence from 1 to 5 and a concise rationale. Rationale must cite document types/fields, not invent external facts.

## Adjudication

- Compute nominal Krippendorff's alpha per label field before adjudication.
- Report item count, annotator count, missing labels, observed pair agreement and alpha.
- Review disagreements independently; record adjudicated label and reason in a separate adjudication file.
- Keep pre-adjudication labels unchanged. Never overwrite original ratings with adjudicated values.
- Do not interpret a low alpha as proof that the benchmark is bad without inspecting ambiguous rubric categories and case complexity.

## Reproducibility

Generate the packet after benchmark v0.4 generation:

    python scripts/build_annotation_packet.py --per-family 10 --seed 20261123

The CI artifact contains only the shareable packet and manifest. The private key file is deliberately excluded.

After two or more annotators complete separate copies, concatenate them into long format (one row per annotation ID and annotator) and run:

    python scripts/score_annotation_agreement.py completed_annotations.csv

No annotation results are included in the repository until real independent annotators complete the task.
