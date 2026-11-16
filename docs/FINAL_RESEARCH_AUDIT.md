# Evidence-Gated Autonomy — Experiment 1A–1D Final Research Audit

## 1A — deterministic synthetic benchmark
500 unique underlying evidence situations, paired into 1,000 LOW/HIGH action cases.
Evidence Gate: 0/500 HIGH-risk unsafe ACT decisions in the deterministic environment.
This result is intentionally treated as a sanity/proof-of-concept result only.

## 1B — imperfect stochastic verification/retrieval/escalation
30 Monte Carlo seeds per regime.
Evidence Gate mean HIGH-risk ICAR:
- optimistic: 0.0186 ± 0.0052
- moderate: 0.0610 ± 0.0115
- harsh: 0.1309 ± 0.0131

Moderate Risk Gate ICAR: 0.1655.

## 1C — adversarial evidence/provenance stress
The method's main discovered vulnerability is reliance on trustworthy evidence metadata.
Dependency spoofing and external-evidence masking materially increase ICAR; combined metadata/evidence spoofing reaches ~24% in the current stress design.

## 1D — OOD / compound shift
Frozen policies evaluated under nuisance shift, overconfidence, provenance dropout, and compound shift.
Compound shift:
- Evidence Gate: 0.1195
- Risk Gate: 0.1851
- Confidence-only: 0.7660

## Interpretation
The strongest defensible conclusion is not that evidence gating "solves" agent safety. It is:
1. confidence-only action authorization is brittle in this controlled testbed;
2. explicit external grounding and evidence-source independence add measurable protection in the benchmark;
3. those benefits collapse when provenance/independence signals can be spoofed;
4. a serious implementation therefore needs trustworthy evidence provenance/attestation rather than merely more verifier votes.

## Research status
These are synthetic and Monte Carlo experiments. No external LLM API outputs, real customs records, production deployment, or human-subject experiments are represented here.

## Historical reproducibility qualification

The historical 1B–2E result CSVs were added to Git without their original simulation runners or complete parameter configurations. Git history for the 1B summary confirms that the result file was committed by itself. The original Experiment 1A downstream-resolution implementation is also absent. Historical numbers are therefore preserved as reported outputs, not independently reproduced results.

## New reconstruction v1

The verified execution is [GitHub Actions run 43949299526](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43949299526), and its output hashes/source provenance are pinned in [manifest-43949299526.json](../results/reconstruction_v1/manifest-43949299526.json). It completed successfully, including manuscript compilation. A separate executable reconstruction is defined in:
- `experiments/reconstruction_v1/PROTOCOL.md`
- `scripts/run_reconstruction_v1.py`
- `tests/test_reconstruction_v1.py`
- `results/reconstruction_v1/README.md`
- `experiments/reconstruction_v1/RESULTS_REVIEW.md`

It runs new 1B, 1C, 1D, 2B, 2C, 2D and 2E experiments under explicit assumptions and 30 Monte Carlo seeds per condition. It does not claim to recreate the historical results. The runner creates role-scoped synthetic attestations, preserves baseline gate decisions in dual-lineage tests, records source revision/run metadata, and hashes generated CSV outputs in its manifest.

### Preliminary interpretation

- Under the new 1B protocol, Evidence Gate's ICAR is 0.81% optimistic, 4.95% moderate and 13.51% harsh. In the moderate regime Risk Gate is 5.30%, so the observed advantage is small and costs more intervention units.
- Under 1C, the new Evidence Gate ICAR is 6.21% without attack and 14.71–33.89% across the specified metadata attacks.
- Under 1D, the chosen shifts do not increase Evidence Gate ICAR (6.52% in-distribution; 6.20% compound). The current OOD protocol is insufficient to support a robustness or degradation claim.
- Under 2B, role-scoped attestations block direct unsafe ACTs under the unsigned metadata attacks by causing escalation.
- Under 2D, compromising a single relevant root produces 10% ICAR; compromising all three produces 30%.
- Under 2E, the stylized C8 test gives 0% ICAR under no/single-authority compromise and 10% when both lineage authorities are compromised.

These results are synthetic and conditional on the new protocol. They are not replacements for the historical tables and must not be inserted into the manuscript until independent review, stronger OOD design, sensitivity analysis and claim reconciliation are complete.
