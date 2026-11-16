# EGA Reconstruction v1 — Output Guide

This directory is populated by `python scripts/run_reconstruction_v1.py` and by the GitHub Actions artifact `ega-reconstruction-v1`.

**Important:** these are newly generated simulations under `experiments/reconstruction_v1/PROTOCOL.md`. They are not reproductions of the historical CSVs in `results/exp1/` and `results/exp2/`.

## Generated files

| File | Contents |
|---|---|
| `exp1b_seed_results.csv` | Per-seed, per-policy Monte Carlo outcomes for optimistic/moderate/harsh downstream reliability |
| `exp1b_summary.csv` | Mean, SD and 95% t intervals for Experiment 1B |
| `exp1c_seed_results.csv` | Per-seed adversarial metadata/provenance stress results |
| `exp1c_summary.csv` | Experiment 1C aggregate results |
| `exp1d_seed_results.csv` | Per-seed nuisance, confidence, provenance-dropout and compound-shift results |
| `exp1d_summary.csv` | Experiment 1D aggregate results |
| `exp2_unsigned_attack_cases.csv` | Per-case v1/v2 decisions and signature-binding validity |
| `exp2_unsigned_attack_summary.csv` | Deterministic unsigned-attack comparison |
| `exp2c_seed_results.csv` | Per-seed 90%-accurate escalation outcomes after tamper detection |
| `exp2c_summary.csv` | Experiment 2C aggregate results |
| `exp2d_trust_root_summary.csv` | Role-specific trust-root compromise outcomes |
| `exp2e_dual_lineage_summary.csv` | Dual-lineage separation-of-duties compromise outcomes |
| `manifest.json` | Protocol identity, seed count, experiment names and generated-file inventory |

## Interpretation cautions

- A Monte Carlo confidence interval describes variation across the specified simulation seeds, not uncertainty about real-world performance.
- The downstream reviewer and retrieval mechanisms are stylized assumptions, not measured human or model behavior.
- The OOD transformations are initial stress probes; a shift that does not worsen ICAR is a negative result about that particular shift design, not proof of robustness.
- The provenance model uses deterministic synthetic Ed25519 test keys and simplified trust roles. It is not a production PKI security evaluation.
- Read the protocol before interpreting any result. Do not copy these numbers into the manuscript until independent review and claim reconciliation are complete.
