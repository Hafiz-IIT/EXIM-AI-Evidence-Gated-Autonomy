# EXIM AI — Evidence-Gated Autonomy

<p align="center">
  <strong>Can an AI system know when it has enough evidence to act?</strong><br/>
  <sub>An inspectable research program connecting document intelligence, verification failure, provenance and action-conditioned escalation.</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-research%20prototype-blue" alt="Research prototype"/>
  <img src="https://img.shields.io/badge/data-synthetic-orange" alt="Synthetic data"/>
  <img src="https://img.shields.io/badge/action-policy-ACT%20%7C%20VERIFY%20%7C%20REQUEST%20EVIDENCE%20%7C%20DEFER%20%7C%20ESCALATE-purple" alt="Action policy"/>
</p>

## The research problem

The project started from a practical EXIM/document workflow and narrowed into a general reliability question:

> **Extraction is not consistency. Consistency is not truth. Verification is not automatically independent evidence.**

A consequential AI system therefore needs to reason about **what evidence exists, where it came from, how fresh it is, whether sources are dependent, what was independently verified, and what happens if the action is wrong.**

## System idea

```
Documents / observations
          ↓
Extraction
          ↓
Cross-source consistency
          ↓
Evidence quality
  provenance · freshness
  independence · conflicts
          ↓
Action-conditioned gate
          ↓
ACT / VERIFY / REQUEST EVIDENCE / DEFER / ESCALATE
```

## What this repository actually contains

The repository includes an inspectable synthetic research environment with:

- **500 unique synthetic evidence situations**
- paired into **1,000 low/high-consequence cases**
- **10 controlled failure families**
- deterministic policy comparisons
- imperfect-verification simulations
- adversarial evidence/provenance stress tests
- out-of-distribution shifts
- Ed25519 provenance-attestation experiments
- trust-root compromise tests
- dual-lineage separation-of-duties experiments
- preregistered protocols for future real-model and human-reviewer studies

## Results are separated from future work

### Existing computational evidence

- `results/exp1/summary.csv`
- `results/exp1/exp1b_stochastic_summary.csv`
- `results/exp1/exp1c_stress_human90.csv`
- `results/exp1/exp1d_ood_summary.csv`
- `results/exp2/deterministic_attack_comparison.csv`
- `results/exp2/EXP2_RESULTS.md`
- `results/exp2/updated_claim_ledger.csv`

These are synthetic computational experiments. They should be read as evidence about the implemented simulation conditions—not as proof of performance on deployed AI systems.

## Action policy

The core policy family is:

**ACT → VERIFY → REQUEST EVIDENCE → DEFER → ESCALATE**

The interesting research question is not simply “does the model have high confidence?”

It is:

> **What evidence threshold should be required for a particular consequence?**

A low-risk informational response and a high-consequence operational action should not necessarily require the same evidentiary standard.

## EXIM origin

The project is grounded in long-running exposure to export-import and logistics workflows, including document-heavy operational processes. That domain motivated the original problem decomposition; the resulting evidence-gating framework is intentionally broader than customs or trade.

## Research boundary

This repository does **not** claim:

- production customs automation
- regulatory approval
- deployment in ICEGATE/DGFT
- a working physical cargo scanner
- human-subject validation
- real-model validation unless explicitly identified in the experiment files
- publication or peer review

The strongest defensible contribution at this stage is the **formal problem decomposition + reproducible synthetic experimentation + explicit claim ledger**.

## Related portfolio work

- [Agent Evidence Probes](https://github.com/Hafiz-IIT/agent-evidence-probes)
- [Memory Governor](https://github.com/Hafiz-IIT/memory-governor)
- [Safe RL Action Gate](https://github.com/Hafiz-IIT/safe-rl-action-gate)
- [EXIM Document Truth Bench](https://github.com/Hafiz-IIT/exim-document-truth-bench)
- [EXIM Copilot Core](https://github.com/Hafiz-IIT/exim-copilot-core)
- [Secure Document RAG Agent](https://github.com/Hafiz-IIT/secure-doc-rag-agent)
- [Cargo Scan Consistency Lab](https://github.com/Hafiz-IIT/cargo-scan-consistency-lab)
- [~haf.s__ OS Core](https://github.com/Hafiz-IIT/hafs-os-core)

## Reproducibility

Start with the experiment summaries, claim ledger and repository tests. The research materials are deliberately structured so that another reader can inspect the assumptions before interpreting the results.
