# arXiv / Preprint Release Checklist

## Current decision

**NOT READY FOR SUBMISSION**

The repository now contains explicit runners for new reconstruction experiments (v1/v2), the v3 authenticated witness-quorum study, and a v4 claim-scoped evidence-provenance prototype. The v3 manuscript update and its full CI run (44164029203) passed. However, the original historical experiment runners and complete parameter configurations for Experiments 1B–2E are still absent from Git history. The new reconstruction runs are new simulations under explicit protocols, not historical reproductions. The v4 experiment stage has generated an initial artifact, but the latest code changes (claim units, credential validity bounds, shared replay state, and stale-vs-replay separation) still require a complete successful workflow. The paper is therefore not submission-ready.

## Paper identity
**Title:** Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence  
**Author:** Syed Hafiz Ali  
**Current manuscript:** `paper/main.tex`

## Claims that may be stated with explicit synthetic boundaries
- 500 underlying synthetic evidence states paired into 1,000 LOW/HIGH-consequence cases.
- Reported deterministic Evidence Gate result: 0/500 unsafe HIGH-risk ACT decisions in the documented setup.
- Reported Risk Gate and Always Verify deterministic result: 50/500 each.
- Reported stochastic Evidence Gate ICAR: 1.86% optimistic, 6.10% moderate, 13.09% harsh.
- Reported provenance attacks demonstrate failures under compromised metadata/trust assumptions.
- Reported 3,675 synthetic Ed25519 attestations.
- The reported results are synthetic and not production-safety evidence.

These are currently claims cross-checked against stored result files, not independently regenerated from complete committed experiment source.

The v3 supplementary experiment is separately reproducible from its committed protocol and runner: the honest baseline recovered 100/100 safe cases with zero unsafe ACT; 2-of-3 admitted 50/700 unsafe ACT under two-witness collusion and registry-root compromise; strict 3-of-3 blocked those modeled cases but not full-roster compromise and failed closed under one invalid credential. These v3 counts are validated by full CI run 44164029203. Do not conflate this supplementary result with the unrecovered historical 1B–2E simulations. No v4 result should be stated until its latest full workflow and artifact have passed review.

## Claims forbidden
- "solves AI safety"
- "guarantees safety"
- "production-ready"
- "real-world validated"
- "frontier-model evaluation completed"
- "works on real customs data"
- "human oversight was validated"
- "cryptography proves evidence truth"

## Required blockers

- [ ] Recover the original historical 1B–2E experiment source and parameters, or remove/relabel the historical numerical claims so they are not presented as independently reproduced.
- [x] Commit new reconstruction runners for 1B/1C/1D and 2B–2E under explicit v1/v2 protocols; keep them clearly distinguished from historical reproductions.
- [x] Commit and validate the v3 witness-quorum runner, regression tests, results review, and manuscript section (full CI run 44164029203).
- [ ] Complete a full successful CI run for the latest v4 claim-scoped provenance code; the latest action-payload, unit, credential-window, replay-state and stale-evidence changes must be validated together.
- [ ] Complete the dependency-ancestry follow-up comparing key-only, direct-field-distinct 2-of-3/3-of-3 and graph-aware evidence independence, with shared-parent, cloud-IDP, KMS, firmware and upstream-feed attacks.
- [ ] Rerun all current results from a clean checkout and compare output hashes for benchmark v0.4 and each v2/v3/v4 experiment artifact.
- [ ] Reconcile manuscript tables, claims ledger, protocol versions, results reviews and manifests with the final regenerated artifacts.
- [ ] Complete a full-text novelty review against EFD, VP-CONTROL, TradeSense-EQA, commit-time authorization, SCITT, DIV/DEWP/ARP, IoT provenance, defeaters and reject-option research.
- [ ] Complete final mathematical, security, and manuscript review.

## Checks already completed

- [x] LaTeX source compiles in GitHub Actions for the v3 manuscript revision (run 44164029203).
- [x] Existing result CSVs are checked into version control.
- [x] A regression test now verifies that missing invoice, packing list, or declaration requests evidence.
- [x] Benchmark generation and pair-integrity checks run in CI.
- [x] Manuscript and claim boundary explicitly state that results are synthetic.
- [x] Related-work section now includes EFD, VP-CONTROL, TradeSense-EQA, execution-boundary authorization and provenance-security work.
- [x] Preliminary novelty audit records additional SCITT, DIV, DEWP and ARP prior art.

## Release decision

Do not upload the current manuscript as a research preprint until every blocker above is closed. A successful LaTeX build or benchmark-generation workflow is not a substitute for rerunning the experiments.
