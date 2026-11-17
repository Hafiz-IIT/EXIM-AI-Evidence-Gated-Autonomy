# Recovered original Experiment 2 artifacts

This directory preserves exact source files from the 12 September 2026 GitHub-ready research snapshot. The original archive was recovered from the user's Library as evidence-gated-autonomy-github-ready.zip (SHA-256: e0003b08d7a4f72d3bfb5134af2430db82d96172e096594795eec1c59a6c2189). Its 32-entry SNAPSHOT_SHA256.json was verified against all 32 files with zero mismatches before extraction.

The original Experiment 2 provenance archive, evidence_gated_autonomy_experiment2_provenance.zip (SHA-256: edbdb53e7363b1eb280ed583225f0e11b46791ed4b4d8477ff93abe8b5b45985), supplied the original 2D per-seed CSV and the seven-row dual-lineage compromise table. The latter is restored at results/exp2/dual_lineage_compromise.csv with SHA-256 8eaa6f1989dd347bb5f88d230b5cb0fbe0e094b7f3841cca7f2bc7a0267a0394.

## What these files are

- src/core.py is the archived original v1 evidence-gate policy implementation.
- src/provenance.py is the archived original Ed25519 signing/verification helper.
- They are preserved under this legacy directory and do not replace the current src/core.py or src/provenance.py.
- Original 2D aggregate and per-seed outputs are restored under results/exp2 and checked by tests.

## What remains missing

Neither recovered ZIP contains the original executable Experiment 2B/2D/2E runner implementing evidence_gate_v2 / evidence_gate_v3. The archives contain protocols, attestation objects, cached case outputs, result CSVs and the original v1/provenance primitives, but not the v2/v3 controller source or a complete runner. We therefore do not reconstruct those functions from prose or label a new implementation as original. Issue #3 remains open until the exact frozen controller code is recovered or the user explicitly authorizes a clearly labeled reconstruction.

These are synthetic historical artifacts. They are not production cryptographic infrastructure or real-world safety evidence.
