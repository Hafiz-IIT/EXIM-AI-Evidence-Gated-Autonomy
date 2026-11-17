# arXiv Metadata — Draft Only, Not Submission-Ready

This file is retained as a drafting aid. **Do not paste or submit it yet.** New reconstruction and v3/v4 supplementary experiment runners are now present, but the original historical 1B–2E runners and full parameter configurations remain unrecovered. New reconstruction outputs are not historical reproductions. The latest v4 changes also require a complete successful CI run, and the expanded novelty audit identifies substantial overlap with EFD, VP-CONTROL, TradeSense-EQA, execution-boundary authorization and current witness/provenance protocols. See [PRIOR_ART_AUDIT_2026.md](PRIOR_ART_AUDIT_2026.md), [NOVELTY_AUDIT.md](../research/NOVELTY_AUDIT.md), and [ARXIV_SUBMISSION_CHECKLIST.md](ARXIV_SUBMISSION_CHECKLIST.md).

## Proposed title
Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence

## Author
Syed Hafiz Ali

## Proposed affiliation
Independent Researcher; BS in Data Science and Applications, Indian Institute of Technology Madras

## Draft abstract
As AI systems are given greater autonomy, a central deployment question is not only whether a model can produce a plausible answer, but whether the available evidence is sufficient to authorize a consequential action. This work introduces Evidence-Gated Autonomy (EGA), a synthetic benchmark and action-authorization framework that maps observable evidence states to ACT, VERIFY, REQUEST EVIDENCE, DEFER, or ESCALATE. The benchmark contains 500 underlying evidence situations paired across low- and high-consequence actions, producing 1,000 cases across ten controlled failure families. In the reported idealized deterministic testbed, EGA produced 0/500 unsafe high-consequence ACT decisions, compared with 50/500 for tested Risk-Gate and Always-Verify baselines. Under reported stochastic verification, retrieval, and escalation assumptions, the high-risk incorrect-action rate increased from 1.86% in an optimistic regime to 6.10% in a moderate regime and 13.09% in a harsh regime. Adversarial tests showed that spoofed dependency metadata and masked external evidence could defeat the original gate. Cryptographically binding provenance claims with Ed25519 attestations prevented direct unsafe ACTs under several unsigned metadata attacks, but valid signatures over false claims remained dangerous under trust-root compromise. A dual-lineage separation-of-duties design raised the compromise threshold for fabricated evidence independence. All results are synthetic or simulated and do not establish production safety. Full computational reproducibility remains outstanding because the original historical experiment runners and parameter configurations are missing. The newer reconstruction and v3/v4 runners define separate, newly specified synthetic experiments; they do not retroactively reproduce the historical CSVs.

## Candidate categories (not a submission recommendation)
Possible categories after the research and novelty review include cs.AI, cs.LG, or cs.CY. Final category selection and acceptance are determined by arXiv moderation.

## Submission source boundary, if approved later
The intended source package is limited to:
- `main.tex`
- `references.bib`

Do not submit until the reproducibility and novelty blockers have been closed.
