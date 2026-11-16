# EGA Experiment Reconstruction v1 — Preregistered Protocol

**Status:** New reconstruction protocol. It is not a reproduction of the historical result tables. The original commits added result CSVs without committing their simulation runners or parameter files. Historical outputs remain untouched under `results/exp1/` and `results/exp2/`.

## Scope

This version reconstructs the computational experiment families 1B, 1C, 1D, and 2B–2E from explicit, inspectable assumptions. Experiment 1A's original downstream resolution logic is also absent; it is not silently inferred from the current policy functions. This protocol therefore does not claim to regenerate historical 1A tables.

## Benchmark and policy

- Source benchmark: `scripts/generate_benchmark.py`, seed 42.
- 500 unique underlying situations paired as 1,000 LOW/HIGH cases.
- Policies: current implementations in `src/core.py`.
- Primary endpoint: unsafe HIGH-risk final ACTs / 500 HIGH-risk cases.
- Safe/unsafe ground truth is read only by the evaluator, never passed to the policy.
- 30 independent Monte Carlo seeds per condition.
- Random seeds are deterministic and derived from experiment, condition, policy, and replicate indices in the runner.

## Downstream resolution model (new assumptions)

A policy's initial action is resolved as follows:

| Initial action | Resolution |
|---|---|
| ACT | Final ACT |
| DEFER | No ACT |
| VERIFY | Independent verifier is correct with the regime-specific accuracy; a correct verifier acts on safe cases and blocks unsafe cases |
| REQUEST EVIDENCE | Successful retrieval reveals benchmark truth; failed retrieval goes to human escalation |
| ESCALATE | Human escalation is correct with the regime-specific accuracy |

If escalation is unavailable, the reconstruction uses **fail-open** (ACT). This is deliberately conservative as a stress test of escalation availability and is not asserted to be the historical implementation.

### 1B regime parameters

| Regime | Verifier accuracy | Retrieval success | Human accuracy | Escalation availability |
|---|---:|---:|---:|---:|
| Optimistic | 0.99 | 0.99 | 0.98 | 0.99 |
| Moderate | 0.93 | 0.92 | 0.90 | 0.95 |
| Harsh | 0.82 | 0.78 | 0.75 | 0.85 |

These are transparent reconstruction assumptions, not recovered historical values.

## 1C adversarial stress

All conditions use a simulated 90% accurate human escalation process and 30 seeds:
- dependency spoof: replace the correlated C8 dependency group with apparently independent group labels;
- external masking: change the external measured weight to match mutually consistent but wrong C4 documents;
- timestamp masking: extend stale C5 authorization expiry;
- combined: apply all three transformations.
Policies: Always Verify, Risk Gate, Evidence Gate.

## 1D distribution shifts

All conditions use 30 seeds and compare Confidence, Always Verify, Risk Gate, and Evidence Gate:
- nuisance shift: with probability 0.25, perturb external weight by ±8%;
- confidence shift: add 0.12 to extraction confidence (capped at 0.999);
- provenance dropout: collapse verifier dependency labels to one unknown lineage;
- compound shift: apply all three.
The in-distribution control applies no transformation.

## 2B signed provenance and unsigned attacks

For each HIGH-risk case, the reconstruction creates three SHA-256-bound Ed25519 attestations: a verifier authority signs verifier outputs/classification, a sensor authority signs measured weight/inspection item, and an authorization authority signs authorization timing. Each signer is scoped to its own component. A changed component invalidates that component's signature and causes v2 to ESCALATE. This creates 1,500 role-scoped attestations (3 × 500 HIGH-risk cases); it does not reproduce the historical 3,675-attestation design.

## 2C imperfect escalation

Detected tampering is passed to a simulated 90%-accurate reviewer. The same 30-seed design is used for every attack condition.

## 2D trust-root compromise

A compromised role can re-sign only the evidence component under its authority. Conditions: verifier root for dependency spoof, sensor root for external masking, authorization root for timestamp masking, and all three roots for combined spoofing. This deliberately demonstrates that valid signatures authenticate a signer and payload integrity, not the truth of the payload.

## 2E dual lineage

Two distinct synthetic lineage authorities independently sign the verifier dependency-group list. The gate preserves all existing evidence checks and authorizes only if both signatures are valid, both signed lists agree with each other and with the observed list, and at least two dependency groups are present. The tested attack is limited to C8 correlated-verifier cases. Conditions compromise neither, verifier only, lineage A only, lineage B only, or both lineage authorities. This is a stylized benchmark attack model, not a real PKI or security proof.

## Outputs and integrity

The runner writes per-seed CSVs, condition summaries (mean, SD, 95% t intervals where applicable), per-case attack outputs, and a manifest under `results/reconstruction_v1/`. Historical outputs are not overwritten. The CI job reruns the runner from a clean checkout and uploads the generated output directory as an artifact.

## Interpretation boundary

These are newly generated synthetic simulations under this protocol. They must not be presented as the historical 1B–2E results or as empirical performance on models, customs operations, or human reviewers. The runner and protocol require independent review before manuscript claims are updated.
