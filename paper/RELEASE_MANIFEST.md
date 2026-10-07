# v1 Release Manifest

## Frozen research artifact

- **Paper:** Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence
- **Author:** Syed Hafiz Ali
- **Repository:** https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy
- **Version:** v1 manuscript / Experiments 1A–2E
- **Benchmark:** 500 unique evidence situations × LOW/HIGH consequence pairing = 1,000 cases
- **Benchmark seed:** 42
- **Attestations:** 3,675 synthetic Ed25519 attestations in Experiment 2
- **Primary reproducibility commands:**
  - `python scripts/generate_benchmark.py`
  - `python scripts/verify_benchmark.py`
  - `python scripts/reproduce_tables.py`

## Evidence freeze

The manuscript claims were cross-checked against the version-controlled result files:

- `results/exp1/summary.csv`
- `results/exp1/exp1b_stochastic_summary.csv`
- `results/exp1/exp1c_stress_human90.csv`
- `results/exp1/exp1d_ood_summary.csv`
- `results/exp2/deterministic_attack_comparison.csv`
- `results/exp2/EXP2_RESULTS.md`

The checked-in CI workflow regenerates the benchmark, verifies its integrity, reproduces publication tables, and compiles `paper/main.tex`.

## CI verification

A successful manuscript build was verified before this release preparation on commit:

`c0a09bdaefec6148431de0deee8cb60a60f760ed`

Run:
https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/37621905014

A subsequent CI revision also uploads the compiled PDF as a workflow artifact so the final submission source can be inspected independently.

## Claim boundary

This v1 release does **not** claim:

- real-world or production safety;
- validation on real customs data;
- frontier-model evaluation;
- completed human-subject research;
- regulatory approval;
- cryptographic proof of evidence truth;
- elimination of trust-root or escalation risk.

## arXiv source boundary

The intended arXiv source package contains only the manuscript compilation inputs:

- `paper/main.tex`
- `paper/references.bib`

Repository notes, benchmark caches, credentials, private material, and unrelated project files are excluded.

## Post-submission update

After arXiv assigns the public identifier, update:

1. `README.md`
2. `CITATION.cff`
3. `paper/ARXIV_METADATA.md`
4. the portfolio/research index

with the exact arXiv identifier and public abstract URL.

Do not describe the work as an arXiv preprint with an identifier until arXiv has actually assigned one.
