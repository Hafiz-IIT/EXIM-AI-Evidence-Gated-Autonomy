# Claims and Evidence Ledger

This document defines the strongest claims that can currently be made from the repository and the claims that remain unsupported. It is intended to prevent scope drift between experiments, README language, manuscripts, talks, and applications.

## Evidence levels

- **E0 — Conceptual:** design argument or proposed mechanism; no experiment.
- **E1 — Deterministic synthetic:** controlled synthetic benchmark with fixed ground truth.
- **E2 — Stochastic synthetic:** Monte Carlo simulation with imperfect verification/review assumptions.
- **E3 — Adversarial synthetic:** controlled attacks/ablation/stress tests against the benchmark.
- **E4 — External-model:** frozen benchmark evaluated using real model outputs.
- **E5 — Human-subject:** preregistered experiment with actual reviewers.
- **E6 — Real-domain/deployment:** real operational data or production deployment.

The repository currently contains evidence through **E3**. Experiment 3 is designed to reach E4. The human-oversight protocol is designed to reach E5. No E6 evidence is claimed.

## Supported claims

| Claim | Evidence | Status | Boundary |
|---|---|---|---|
| Simple confidence, document agreement, and unconditional verification can fail on controlled high-consequence cases. | Experiment 1A | Supported at E1 | Synthetic benchmark only. |
| The tested evidence gate prevented all unsafe HIGH-risk ACT decisions in deterministic Experiment 1A. | Experiment 1A | Supported at E1 | Does not imply zero real-world risk. |
| Evidence-gate performance degrades when verification, evidence retrieval, and escalation are imperfect. | Experiment 1B | Supported at E2 | Error processes are simulated. |
| External grounding, freshness, and source/dependency independence contribute measurable protection in the current benchmark. | Ablations / Exp. 1D | Supported at E1–E3 | Benchmark-specific effect sizes. |
| Correlated verifier failures can invalidate naive assumptions that multiple agreeing verifiers provide independent evidence. | Exp. 1A/1C | Supported at E1–E3 | Correlation structure is synthetic. |
| Unsigned/self-asserted provenance metadata is a weak trust foundation under active spoofing. | Exp. 1C/2 | Supported at E3 | Attack model is stylized. |
| Signed provenance can block certain tampering attacks but does not establish that a signed claim is true. | Exp. 2 | Supported at E3 + established cryptographic principle | Synthetic keys and trust model. |
| Separating verifier authority from lineage authority raises the compromise threshold in the tested synthetic design. | Exp. 2E | Supported at E3 | Not a general security proof. |
| Imperfect escalation can remain a dominant residual failure path after upstream attacks are detected. | Exp. 1B/2 | Supported at E2–E3 | Reviewer accuracy is simulated. |

## Important negative findings

1. Explicit verifier-status handling did not independently reduce deterministic incorrect-action rate once the stronger evidence checks were already present.
2. Risk conditioning mainly changed coverage/cost in the current benchmark rather than independently producing the main safety benefit.
3. REQUEST EVIDENCE improved resolution/coverage over pure deferral, but did not establish an intrinsic safety advantage under imperfect retrieval.
4. Cryptographic provenance changed the attack surface; it did not solve truth verification.
5. Adding more verifiers is not equivalent to adding independent evidence.

Negative findings must remain visible in summaries and manuscripts.

## Claims not currently supported

The project must **not** claim any of the following until new evidence exists:

- that Evidence-Gated Autonomy makes frontier AI agents safe;
- that the policy is validated on production customs/logistics workflows;
- that the reported percentages estimate real-world accident probabilities;
- that simulated 90% human-review accuracy represents actual human reviewers;
- that the provenance design is cryptographically novel;
- that signatures establish truth;
- that the approach is superior to all existing agent-control or scalable-oversight methods;
- that verifier independence can currently be established reliably from model identity alone;
- that any human-subject study has been completed;
- that Experiment 3 has been run.

## Claim-upgrade rule

A claim can only move to a higher evidence level if:

1. the protocol and primary metrics were fixed before viewing the relevant test results;
2. raw outputs and metadata are retained;
3. changed thresholds or policies are evaluated on a fresh holdout;
4. failures and null findings are reported alongside positive results;
5. the manuscript is updated to state the highest evidence level actually achieved.
