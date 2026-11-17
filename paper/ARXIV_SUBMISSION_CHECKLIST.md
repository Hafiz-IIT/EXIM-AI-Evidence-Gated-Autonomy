# arXiv / Preprint Release Checklist

## Current decision

**NOT READY FOR SUBMISSION**

The project has reported synthetic results and a compiled manuscript, but the full experiment runners for Experiments 1B–2E are not present in the repository. The current reproduction command regenerates the benchmark and loads existing CSVs; it does not rerun the simulations that produced those CSVs.

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

- [ ] Commit executable experiment runners for stochastic verification/retrieval/escalation (1B).
- [ ] Commit executable runners for adversarial metadata/evidence stress (1C).
- [ ] Commit executable runners for OOD/compound-shift evaluation (1D).
- [ ] Commit executable runners for attestation attacks, trust-root compromise, and dual-lineage experiments (2A–2E).
- [ ] Expand benchmark coverage for missing invoice and missing packing-list evidence.
- [ ] Rerun all results from a clean checkout and compare output hashes.
- [ ] Reconcile manuscript tables, claims ledger, and manifests with regenerated results.
- [ ] Complete a fresh literature/novelty review.
- [ ] Complete final mathematical, security, and manuscript review.

## Checks already completed

- [x] LaTeX source compiles in GitHub Actions.
- [x] Existing result CSVs are checked into version control.
- [x] A regression test now verifies that missing invoice, packing list, or declaration requests evidence.
- [x] Benchmark generation and pair-integrity checks run in CI.
- [x] Manuscript and claim boundary explicitly state that results are synthetic.

## Additional synthetic extensions completed

- [x] Evidence-Trust v3 authenticated witness-quorum runner, threat matrix, bounded-recovery checks and artifact-backed results review.
- [x] Evidence-Provenance v4 claim-scoped evidence/action-binding runner, tests, threat matrix and artifact-backed results review.
- [x] Dependency-Graph v5 four-policy comparison across 16 scenarios, 44,800 rows, integrity manifest, results review and full CI.
- [x] Latest v5 full workflow [44169136135](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44169136135) passed all 30 job steps, including manuscript compilation.

These later synthetic extensions do not recover the original frozen Experiment 2 source or missing dual_lineage_compromise.csv, and do not substitute for the real-model Experiment 3 evaluation. They must not be presented as historical reproduction of Experiments 2A–2E.

## Experiment 3 execution readiness

- [x] Provider-neutral OpenAI-compatible harness implemented for Evidence Gate v1.
- [x] Blinded task preparation, deterministic pair-level split, separate private evaluation map and prompt hashes.
- [x] Development/validation/final-holdout and document-layout OOD conditions specified.
- [x] CI verifies model-facing tasks contain no oracle labels and uploads only the public task package.
- [ ] Actual provider/model identities and API credentials configured.
- [ ] Development pilot and validation run completed.
- [ ] Frozen final-holdout run completed with raw responses, costs, latency and uncertainty intervals.
- [ ] Provenance-aware v2/v3 model evaluation remains blocked on issue #3.

No real-model Experiment 3 result is claimed until the unchecked execution items are completed.

## Release decision

Do not upload the current manuscript as a research preprint until every blocker above is closed. A successful LaTeX build or benchmark-generation workflow is not a substitute for rerunning the experiments.
