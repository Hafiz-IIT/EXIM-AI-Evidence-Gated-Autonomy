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
