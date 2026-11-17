# EGA v1 Research Artifact — Reproducibility Status

## Artifact identity

- **Paper:** Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence
- **Author:** Syed Hafiz Ali
- **Repository:** https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy
- **Version:** Historical v1 artifact plus separately versioned benchmark v0.4 / reconstruction v2
- **Historical benchmark v0.3:** 500 underlying evidence situations paired across LOW/HIGH consequence = 1,000 cases
- **Extended benchmark v0.4:** 700 underlying evidence situations paired across LOW/HIGH consequence = 1,400 cases; 14 fault families
- **Benchmark seed:** 42
- **Historical attestations reported:** 3,675 synthetic Ed25519 attestations in Experiment 2

## Current status

**Not ready for arXiv submission.** The result CSVs are version-controlled and the manuscript claims have been compared against them, but the repository does not yet contain all experiment-runner source needed to regenerate those results.

The current `scripts/reproduce_all.py` command:
1. regenerates the synthetic benchmark;
2. verifies benchmark structure/pair integrity;
3. loads and prints the existing result CSVs.

It does **not** rerun the stochastic verification, OOD, provenance-attack, trust-root-compromise, or separation-of-duties simulations. The CI workflow therefore does not establish full computational reproducibility of Experiments 1B–2E.

## Known policy correction

The high-risk completeness rule previously checked only whether the declaration existed. It now requires invoice, packing list, and declaration. Regression tests cover each missing-document case. The current v0.3 benchmark does not systematically contain missing-invoice and missing-packing-list cases, so the reported historical tables do not evaluate those new cases.

## Existing result files

- `results/exp1/summary.csv`
- `results/exp1/exp1b_stochastic_summary.csv`
- `results/exp1/exp1c_stress_human90.csv`
- `results/exp1/exp1d_ood_summary.csv`
- `results/exp2/deterministic_attack_comparison.csv`
- `results/exp2/EXP2_RESULTS.md`
- `results/exp2/updated_claim_ledger.csv`

These are reported synthetic results, not yet fully regenerated from the repository's current source.

## New reconstruction track

A separately versioned reconstruction now exists:
- Protocol: `experiments/reconstruction_v1/PROTOCOL.md`
- Runner: `scripts/run_reconstruction_v1.py`
- Tests: `tests/test_reconstruction_v1.py`
- Outputs: `results/reconstruction_v1/` (generated in CI and archived as the `ega-reconstruction-v1` artifact)

It covers new versions of 1B, 1C, 1D, and 2B–2E using explicit parameters and 30 seeds per Monte Carlo condition. The verified run [43949299526](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43949299526) passed tests, benchmark integrity checks, the full reconstruction runner, historical-table loading, artifact upload and manuscript compilation. The output manifest is pinned at [manifest-43949299526.json](../results/reconstruction_v1/manifest-43949299526.json), with SHA-256 hashes for all 12 generated CSVs, source commit `b3e07190a6c365daec33ce83f92e53cf3019e7a5`, Python 3.11.18, and 21,500 synthetic signature records created across the repeated 2B–2E sweeps. These outputs are **not** reproductions of the historical result tables. Experiment 1A's original downstream-resolution logic is also not recoverable from the committed source.

The verified CI execution above passed the regression tests, benchmark generation and integrity verification, reconstruction runner, historical table loading, artifact upload, and manuscript build. Later runner revisions must be revalidated on their own latest CI run before these outputs are treated as final.


## Benchmark v0.4 and reconstruction v2

The extended benchmark adds C10 missing invoice, C11 missing packing list, C12 duplicate document kind and C13 corrupted provenance. Its generator and verifier are:
- `scripts/generate_benchmark_v04.py`
- `scripts/verify_benchmark_v04.py`

The generated benchmark counts and raw JSONL SHA-256 hashes are pinned in [data/benchmark_v0.4/manifest.json](../data/benchmark_v0.4/manifest.json). The v0.4 policy regression tests cover all four new cases. A further test deliberately performs a coherent rewrite of the documents, extraction and external measurement, recomputes the unkeyed digest, and confirms the current gate still returns ACT. This is an explicit security limitation: SHA-256 without a trusted signature detects mismatches, not maliciously rewritten evidence.

The v2 reconstruction and sensitivity protocol is documented in `experiments/reconstruction_v2/PROTOCOL.md`; the first results interpretation is in `experiments/reconstruction_v2/RESULTS_REVIEW.md`. It reruns 1B, 1C, 1D and 2B–2E on 700 HIGH-risk v0.4 cases, plus 25 sensitivity conditions (30 seeds each), and writes paired Evidence Gate-minus-baseline differences with SHA-256 output hashes.

The full v2 experiment execution with the coherent-rewrite regression test passed in [run 43952541323](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43952541323); its v0.4 runner, historical-table loading, artifact uploads, execution-status publication and LaTeX compilation all succeeded. The paired sensitivity/output hashes and source provenance are pinned in [manifest-43952541323.json](../results/reconstruction_v2/manifest-43952541323.json).

## Required before submission

1. Recover the historical Experiment 1A downstream-resolution implementation or explicitly retire its numerical comparison; do not infer it from the current policy functions.
2. Compare the new reconstruction protocol against the historical result tables and explain all differences without parameter fitting.
3. Review the new reconstruction's model assumptions and threats to validity independently.
4. Freeze the exact policies, stochastic assumptions, seeds, cost matrix, and attack configurations.
5. Expand document-root threat testing into independently varied capture, extraction, external-sensor and authorization trust-domain compromises; the first combined-compromise experiment is complete but synthetic.
6. Redesign OOD transformations to test meaningful evidence-quality/dependency shifts.
7. Expand sensitivity analysis beyond the current one-factor and selected two-factor sweeps.
8. Reconcile all manuscript tables and claims against newly generated outputs.
9. Independently verify raw data, aggregate tables, output hashes and the full reproduction command.
10. Perform a fresh literature/novelty review and a full manuscript review.

## Claim boundary

The work remains synthetic. It does not establish production safety, real customs performance, frontier-model performance, completed human-subject research, regulatory approval, cryptographic proof of evidence truth, or elimination of trust-root/escalation risk.

Do not submit or describe this work as an arXiv preprint until the reproducibility blockers above are closed and arXiv has actually assigned an identifier.


## Document-root attestation extension (verified 16 November 2026)

The document-root attestation prototype and threat runner are now implemented:
- Implementation: `src/provenance.py`
- Tests: `tests/test_document_root_attestation.py`
- Runner: `scripts/run_document_root_attestation.py`
- Protocol: `experiments/document_root_attestation/PROTOCOL.md`
- Results review: `experiments/document_root_attestation/RESULTS_REVIEW.md`

The full workflow [43955044311](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43955044311) passed, including the document-root runner and manuscript compilation. Its archived artifact is named `ega-document-root-attestation-v1`; the output manifest records source commit `8e2dc845efefb856818ca61011395f8887249b38` and SHA-256 hashes for both CSV outputs.

Across 700 HIGH-risk v0.4 cases, the verifier rejected raw tampering, unsigned coherent rewrites, revoked-key use, cross-tenant reuse and second-use nonce replay in all tested cases. Under the combined scenario of trusted document-root signer compromise plus coordinated upstream rewrites, the forged attestation verified in all 700 cases; the downstream gate authorized 350 ACT decisions, 300 unsafe against benchmark ground truth (42.86% of all HIGH-risk cases; 85.71% of ACT decisions). The 300 unsafe decisions occurred in C1, C2, C4, C6, C9 and C13 (50 each).

This is a conditional synthetic attack outcome under coordinated compromise of the signing authority and upstream evidence channels. It is not a real-world probability or a result about signer-key theft alone. The implementation uses deterministic test keys and process-local replay state; production key custody, authenticated signer enrollment, secure capture, distributed replay protection and operational key management remain unimplemented. The manuscript remains **not ready for arXiv submission**.


## Four-authority Evidence-Trust v2 extension (CI-verified)

- Implementation: `src/evidence_trust_v2.py`
- Runner: `scripts/run_evidence_trust_v2.py`
- Tests: `tests/test_evidence_trust_v2.py`
- Protocol: `experiments/evidence_trust_v2/PROTOCOL.md`
- Results review: `experiments/evidence_trust_v2/RESULTS_REVIEW.md`
- Output guide: `results/evidence_trust_v2/README.md`
- Pinned manifest: `results/evidence_trust_v2/manifest-44025577491.json`
- Verified full CI run: [44025577491](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44025577491)

The experiment evaluates 15 non-empty combinations of CA, IA, IWA and AA compromise, plus an honest baseline and three controls, across 700 HIGH-risk v0.4 cases per scenario. The archived artifact contains 13,300 case-scenario rows and 19 summaries. The full workflow passed tests, benchmark generation/verification, reconstruction and sensitivity runners, document-root v1, evidence-trust v2, historical-table loading, artifact uploads and LaTeX compilation.

Key results: IWA-only compromise produced 50 unsafe ACT decisions (7.14% of all HIGH-risk cases); CA+IWA, CA+IA+IWA, and key-admin trust-store poisoning each produced 300 (42.86%); any scenario including AA produced 600 (85.71%). Source forgery before capture and a disclosed shared-dependency witness produced no ACT in this specific synthetic model.

The witness is an idealized ground-truth-derived record; source and administrative-domain labels are not externally authenticated. The model uses deterministic test keys and does not implement production KMS/HSM custody, authenticated enrollment, durable replay storage, secure capture or operational revocation. The result does not establish real-world independence or production security.

