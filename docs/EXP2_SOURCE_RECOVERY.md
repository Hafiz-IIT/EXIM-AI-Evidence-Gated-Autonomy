# Experiment 2 source and artifact recovery

## Recovered on 18 November 2026

Two original archives dated 12 September 2026 were recovered from the user's Library:

- evidence-gated-autonomy-github-ready.zip — SHA-256 e0003b08d7a4f72d3bfb5134af2430db82d96172e096594795eec1c59a6c2189
- evidence_gated_autonomy_experiment2_provenance.zip — SHA-256 edbdb53e7363b1eb280ed583225f0e11b46791ed4b4d8477ff93abe8b5b45985

The GitHub-ready snapshot's 32 recorded file hashes were independently checked against the extracted archive: 32/32 matched. The exact archived v1 controller and generic Ed25519 helper are preserved under legacy/experiment2_original/src/ and are not substituted for the current src modules.

The missing results/exp2/dual_lineage_compromise.csv is restored with SHA-256 8eaa6f1989dd347bb5f88d230b5cb0fbe0e094b7f3841cca7f2bc7a0267a0394. The original trust-root compromise table, dual-lineage stochastic summary and 30-seed per-seed CSV are also restored. Regression tests verify all hashes and recompute the stochastic summary from the per-seed data.

## Unresolved source-level gap

The two archives do not contain an executable Experiment 2B/2D/2E runner or the original evidence_gate_v2 / evidence_gate_v3 controller functions. They contain the v1 core, generic signing helpers, signed sample attestations, cached case outputs, JSONL case records, protocols and result tables. This is not enough to reconstruct the exact historical v2/v3 logic without inventing implementation details.

Accordingly, issue #3 is only partially resolved:
- recovered: missing original CSV and source snapshots;
- still missing: exact frozen v2/v3 controller/runner source and an execution path that reproduces all historical 2B/2D/2E tables.

Do not label a later implementation as the original controller. A separate, explicitly named reconstruction can be considered only after the recovered artifacts and assumptions are fully documented.
