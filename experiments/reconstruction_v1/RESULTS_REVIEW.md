# Reconstruction v1 — Preliminary Results Review

**Source run:** [GitHub Actions run 43949299526](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43949104719)  
**Protocol:** [PROTOCOL.md](PROTOCOL.md)  
**Runner:** [run_reconstruction_v1.py](../../scripts/run_reconstruction_v1.py)  
**Status:** Synthetic reconstruction; not historical reproduction; not yet manuscript-approved. The run manifest is pinned at [manifest-43949299526.json](../../results/reconstruction_v1/manifest-43949299526.json).

The values below are from the generated reconstruction artifact. The protocol and raw per-seed CSVs must be consulted before secondary analysis. These numbers must not replace the historical result tables without a separate review decision.

## 1B — Stochastic verification/retrieval/escalation

Evidence Gate mean HIGH-risk ICAR:
- Optimistic: **0.81%** (SD 0.43%; 95% t interval 0.65–0.97%).
- Moderate: **4.95%** (SD 1.10%; 95% t interval 4.54–5.36%).
- Harsh: **13.51%** (SD 1.58%; 95% t interval 12.92–14.10%).

In the moderate regime, Risk Gate was **5.30%** (SD 0.99%; 95% t interval 4.93–5.67%). The difference is small under this reconstruction, while Evidence Gate's mean initial intervention cost is 1.30 versus 1.00 for Risk Gate. This does **not** establish a meaningful advantage for EGA under the specified assumptions.

## 1C — Adversarial metadata stress

Evidence Gate ICAR:
- No attack: **6.21%**.
- Dependency spoof: **14.71%**.
- External-evidence masking: **15.43%**.
- Timestamp masking: **15.93%**.
- Combined metadata spoof: **33.89%**.

This reconstruction reproduces the qualitative counterexample: the current gate can be induced to authorize unsafe cases when the metadata it trusts is altered. The result remains conditional on the synthetic C4/C5/C8 attack constructions.

## 1D — Distribution shift

Evidence Gate ICAR:
- In-distribution: **6.52%**.
- Nuisance shift: **6.22%**.
- Confidence shift: **6.47%**.
- Provenance dropout: **5.98%**.
- Compound shift: **6.20%**.

The current shifts did not increase Evidence Gate ICAR. The nuisance perturbation often triggers additional external-conflict handling, and provenance dropout forces a single dependency group, which prompts escalation. These transformations therefore do not provide a strong test of degraded evidence quality. The correct conclusion is that this v1 OOD protocol is insufficient to establish either robustness or meaningful degradation. A stronger, preregistered shift design is required.

Confidence-only ICAR rises from **28.8%** in-distribution to **48.0%** under the confidence/compound shift, illustrating that this specific confidence perturbation affects the confidence baseline.

## 2B — Unsigned metadata attacks and scoped attestations

Under the deterministic synthetic attacks:
- Evidence Gate v1: **10% ICAR** for each individual dependency, external-evidence, and timestamp attack; **30%** for the combined attack.
- Evidence Gate v2 with three role-scoped attestations per HIGH-risk case: **0 direct unsafe ACTs** in these unsigned-tamper conditions; tampered components are escalated.

This is an integrity/tamper-detection result under deterministic synthetic keys, not a production security claim.

## 2C — Imperfect review after detection

With 90%-accurate simulated escalation:
- No attack: **2.01% ICAR**.
- Dependency spoof: **8.11%**.
- External masking: **1.87%**.
- Timestamp masking: **7.87%**.
- Combined spoof: **7.92%**.

Tamper detection does not eliminate downstream review error. The large difference across attack families also warrants per-case inspection before making broader claims.

## 2D — Trust-root compromise

- Verifier root compromised: **10% ICAR**.
- Sensor root compromised: **10%**.
- Authorization root compromised: **10%**.
- All three roots compromised: **30%**.

The implementation now scopes each signer to its own component. A compromised root can re-sign only the component under its authority in this experiment.

## 2E — Dual lineage

- No compromise: **0% ICAR**.
- Verifier-only compromise: **0%**.
- Lineage A only: **0%**.
- Lineage B only: **0%**.
- Both lineage authorities: **10%**.

This is a stylized test of the C8 correlated-verifier family. It is not a security proof, and the independence assumptions of the two lineage authorities require stronger adversarial analysis.

## Required follow-up before manuscript use

1. Independently review the action-resolution model and cost function.
2. Expand the OOD protocol with stronger shifts, train/test separation and shift-specific rationale.
3. Add missing-invoice, missing-packing-list, duplicate-document and malformed-provenance benchmark families.
4. Add sensitivity analyses for all stochastic parameters, not only the three selected regimes.
5. Inspect raw per-case outputs for the 1C and 2C attack families.
6. Reconcile the new results with historical tables without fitting parameters to match old numbers.
7. Recover or retire the historical Experiment 1A downstream-resolution claims.
8. Perform a fresh literature and novelty review.

**No numerical claims in the manuscript should be replaced with these values until the above review is completed.**
