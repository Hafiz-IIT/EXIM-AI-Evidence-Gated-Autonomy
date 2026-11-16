# EGA v1 Research Artifact — Reproducibility Status

## Artifact identity

- **Paper:** Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence
- **Author:** Syed Hafiz Ali
- **Repository:** https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy
- **Version:** v1 synthetic benchmark and reported Experiments 1A–2E
- **Benchmark:** 500 underlying evidence situations paired across LOW/HIGH consequence = 1,000 cases
- **Benchmark seed:** 42
- **Attestations reported:** 3,675 synthetic Ed25519 attestations in Experiment 2

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

It covers new versions of 1B, 1C, 1D, and 2B–2E using explicit parameters and 30 seeds per Monte Carlo condition. These outputs are **not** reproductions of the historical result tables. Experiment 1A's original downstream-resolution logic is also not recoverable from the committed source.

The first clean CI execution passed the regression tests, benchmark generation and integrity verification, reconstruction runner, historical table loading, artifact upload, and manuscript build. Later runner revisions must be revalidated on their own latest CI run before these outputs are treated as final.

## Required before submission

1. Recover the historical Experiment 1A downstream-resolution implementation or explicitly retire its numerical comparison; do not infer it from the current policy functions.
2. Compare the new reconstruction protocol against the historical result tables and explain all differences without parameter fitting.
3. Review the new reconstruction's model assumptions and threats to validity independently.
4. Freeze the exact policies, stochastic assumptions, seeds, cost matrix, and attack configurations.
3. Add missing-invoice, missing-packing-list, duplicate-document, and malformed-provenance scenarios.
4. Rerun all experiments against a versioned benchmark/policy release.
5. Reconcile all manuscript tables and claims against newly generated outputs.
6. Add independent verification of the raw data, aggregate tables, and output hashes.
10. Perform a fresh literature/novelty review and a full manuscript review.

## Claim boundary

The work remains synthetic. It does not establish production safety, real customs performance, frontier-model performance, completed human-subject research, regulatory approval, cryptographic proof of evidence truth, or elimination of trust-root/escalation risk.

Do not submit or describe this work as an arXiv preprint until the reproducibility blockers above are closed and arXiv has actually assigned an identifier.
