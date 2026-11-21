# arXiv / Preprint Release Checklist

## Current decision

**NOT READY FOR SUBMISSION**

The repository now contains executable reconstruction runners and later synthetic extensions, but the original frozen source for historical Experiments 1B–2E was not recovered. The new reconstruction v1/v2 outputs are explicitly separate studies under newly declared assumptions; they must not be described as exact reproductions of the historical CSVs. Evidence-Trust v3, Evidence-Provenance v4, Dependency-Graph v5 and the Experiment 3 harness are also separate versioned extensions. No external model/API evaluation has been run.

## Paper identity
**Title:** Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence  
**Author:** Syed Hafiz Ali  
**Current manuscript:** `paper/main.tex`

## Claims that may be stated with explicit synthetic boundaries
- Historical benchmark v0.3: 500 underlying synthetic evidence states paired into 1,000 LOW/HIGH-consequence cases. Its historical 1A–2E result tables remain reported historical outputs where original runners/configurations were not recovered.
- Benchmark v0.4: 700 underlying synthetic situations paired into 1,400 LOW/HIGH cases across 14 fault families, including missing invoice, missing packing list, duplicate document kind and corrupted provenance.
- Reconstruction v1 and v2: executable, newly versioned synthetic reconstruction studies with explicit assumptions, fixed seeds, result manifests and output hashes. They are not exact reproductions of historical 1B–2E numbers.
- Document-root attestation, Evidence-Trust v3, Evidence-Provenance v4 and Dependency-Graph v5: separate synthetic extensions with their own protocols, threat matrices and artifacts.
- Experiment 3: blinded real-model harness and cost preflight are implemented, but no provider calls or real-model results are claimed.
- All current results are synthetic or simulated and are not production-safety evidence.

The manuscript must distinguish historical reported results, reconstructed results and later versioned extensions in every table and claim.

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

- [x] Commit new executable reconstruction v1/v2 runners for the declared stochastic, adversarial, OOD, attestation and trust-root conditions; preserve them as reconstructions, not historical reproductions.
- [x] Expand benchmark v0.4 to include missing invoice, missing packing-list, duplicate document-kind and corrupted-provenance families.
- [x] Add separate document-root, Evidence-Trust v3, Evidence-Provenance v4 and Dependency-Graph v5 synthetic extensions with manifests and CI artifacts.
- [ ] Recover the exact historical 1B–2E source/configuration or permanently label those original numbers as historical reported outputs only.
- [ ] Reconcile every manuscript table, abstract claim, checklist entry and claims ledger against the correct versioned result source.
- [ ] Strengthen OOD design, sensitivity analysis and per-family false-accept/false-block analysis.
- [ ] Complete and independently review the real-model Experiment 3 development, validation and frozen holdout runs.
- [ ] Complete a fresh literature/novelty search immediately before manuscript freeze.
- [ ] Complete independent mathematical, security and manuscript review.

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
- [x] Model-family holdout configuration is isolated to final-holdout conditions; a dedicated freeze helper pins model, prompt and benchmark hashes.
- [x] Blinded task preparation, deterministic pair-level split, separate private evaluation map and prompt hashes.
- [x] Development/validation/final-holdout and document-layout OOD conditions specified.
- [x] CI verifies model-facing tasks contain no oracle labels and uploads only the public task package.
- [ ] Actual provider/model identities and API credentials configured.
- [ ] Development pilot and validation run completed.
- [ ] Frozen final-holdout run completed with raw responses, costs, latency and uncertainty intervals.
- [ ] Provenance-aware v2/v3 model evaluation remains blocked on issue #3.

No real-model Experiment 3 result is claimed until the unchecked execution items are completed.

The Experiment 3 cost preflight is an approximate planning heuristic, not a guaranteed upper bound or hard spend cap. Final usage and cost must be reconciled against provider-reported token usage and billing.

## Release decision

Do not upload the current manuscript as a research preprint until every blocker above is closed. A successful LaTeX build or benchmark-generation workflow is not a substitute for rerunning the experiments.
