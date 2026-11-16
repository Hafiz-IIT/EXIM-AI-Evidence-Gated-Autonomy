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

## Required before submission

1. Reconstruct and commit runners for every reported experiment.
2. Freeze the exact policies, stochastic assumptions, seeds, cost matrix, and attack configurations.
3. Add missing-invoice, missing-packing-list, duplicate-document, and malformed-provenance scenarios.
4. Rerun all experiments against a versioned benchmark/policy release.
5. Reconcile all manuscript tables and claims against newly generated outputs.
6. Add independent verification of the raw data, aggregate tables, and output hashes.
7. Perform a fresh literature/novelty review and a full manuscript review.

## Claim boundary

The work remains synthetic. It does not establish production safety, real customs performance, frontier-model performance, completed human-subject research, regulatory approval, cryptographic proof of evidence truth, or elimination of trust-root/escalation risk.

Do not submit or describe this work as an arXiv preprint until the reproducibility blockers above are closed and arXiv has actually assigned an identifier.
