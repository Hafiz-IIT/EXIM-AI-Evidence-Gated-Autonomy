# arXiv Metadata — Ready to Paste

## Title
Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence

## Author
Syed Hafiz Ali

## Affiliation
Independent Researcher; BS in Data Science and Applications, Indian Institute of Technology Madras

## Abstract
As AI systems are given greater autonomy, a central deployment question is not only whether a model can produce a plausible answer, but whether the available evidence is sufficient to authorize a consequential action. This work introduces Evidence-Gated Autonomy (EGA), a synthetic benchmark and action-authorization framework that maps observable evidence states to ACT, VERIFY, REQUEST EVIDENCE, DEFER, or ESCALATE. The benchmark contains 500 underlying evidence situations paired across low- and high-consequence actions, producing 1,000 cases across ten controlled failure families. In an idealized deterministic testbed, EGA produced 0/500 unsafe high-consequence ACT decisions, compared with 50/500 for tested Risk-Gate and Always-Verify baselines. Under stochastic verification, retrieval, and escalation, the high-risk incorrect-action rate increased from 1.86% in an optimistic regime to 6.10% in a moderate regime and 13.09% in a harsh regime. Adversarial tests further showed that spoofed dependency metadata and masked external evidence could defeat the original gate. Cryptographically binding provenance claims with Ed25519 attestations prevented direct unsafe ACTs under several unsigned metadata attacks, but valid signatures over false claims remained dangerous under trust-root compromise. A dual-lineage separation-of-duties design raised the compromise threshold for fabricated evidence independence. The results support a narrow conclusion: consequential action authorization depends not merely on model confidence or verifier agreement, but on the structure, provenance, independence, and trustworthiness of the evidence chain. All current results are synthetic or simulated and do not establish production safety.

## Suggested comments field
5-page verified CI PDF (2026-10-07); synthetic benchmark and provenance stress-test study; code and reproducibility materials available at https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy

## Candidate categories
Primary candidate: cs.AI

Possible cross-list depending on final moderation/framing:
- cs.LG
- cs.CY

Category acceptance and endorsement are determined by arXiv.

## Keywords
AI safety; AI control; autonomous agents; verification; evidence provenance; scalable oversight; action authorization; correlated failure; trust roots; human escalation

## Submission source files
Upload only:
- main.tex
- references.bib

Do not upload private notes, Git history, credentials, client documents, benchmark caches, or unrelated repository files.
