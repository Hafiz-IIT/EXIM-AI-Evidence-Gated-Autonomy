# Claims and Evidence Ledger

This file separates what the repository directly supports from hypotheses, bounded interpretations, and work not yet completed.

## Supported by current repository evidence

### C1 — Extraction confidence alone is insufficient for consequential authorization

**Support:** synthetic failure families include high-confidence machine outputs that can conflict with documents, external measurements, or benchmark truth. Simpler confidence-only baselines perform worse than the tested evidence-aware controller on the benchmark.

**Boundary:** this is a benchmark result, not a claim that every production model is miscalibrated in the same way.

### C2 — Agreement does not imply truth

**Support:** the consistent-but-wrong and correlated-verifier-failure families create mutually agreeing evidence that is nevertheless wrong relative to hidden benchmark truth.

**Boundary:** the benchmark demonstrates possibility and controller sensitivity, not prevalence in deployed systems.

### C3 — Evidence-source independence matters

**Support:** ablations and correlated-failure conditions show that treating dependent verifiers as independent can permit unsafe authorization.

**Boundary:** current dependency groups are benchmark metadata; real-world dependence is substantially harder to identify.

### C4 — Freshness and external grounding provide independent protective value in the synthetic benchmark

**Support:** ablations and adversarial stress tests show degradation when these checks are removed or spoofed.

**Boundary:** the exact effect size depends on benchmark construction.

### C5 — Cryptographic provenance authenticates integrity/signer claims, not truth

**Support:** Experiment 2 shows that signed false claims remain dangerous when trusted roots are compromised.

**Boundary:** the cryptographic setup uses deterministic test keys and is not a production PKI deployment.

### C6 — Separation of duties can raise the compromise threshold in the synthetic provenance setting

**Support:** the dual-lineage Experiment 2 variant prevents specific single-authority compromise paths that defeat weaker provenance designs.

**Boundary:** it does not prove institutional independence, operational security, or protection against collusion in real deployments.

### C7 — Verification and escalation are themselves failure-bearing stages

**Support:** stochastic simulations degrade materially when review/retrieval/escalation are imperfect.

**Boundary:** human behavior is simulated in current results. No participant study has been run.

## Supported negative findings

### N1 — Explicit verifier-status handling did not add independent deterministic protection after other checks were present

Treat as a benchmark-specific negative result.

### N2 — Risk conditioning primarily changed coverage/cost in the current benchmark

Do not claim a universal safety advantage from consequence labels alone.

### N3 — REQUEST EVIDENCE improved resolution/coverage but did not establish intrinsic safety benefit in the current stochastic setup

Do not overstate request behavior as automatically safer than deferral.

## Hypotheses requiring Experiment 3

### H1 — Cross-family verification has lower co-failure than same-family self-verification

**Status:** untested with real external model families in this repository.

### H2 — Evidence Gate v1 retains a lower high-risk incorrect-action rate than simpler baselines when machine outputs come from real models

**Status:** untested.

### H3 — Document-format distribution shift materially changes extraction and verifier co-failure patterns

**Status:** untested.

### H4 — Model-family identity is a useful but incomplete proxy for verifier independence

**Status:** hypothesis. Experiment 3 should preserve family identity but must not equate different families with guaranteed independence.

## Work explicitly not completed

- no production EXIM deployment;
- no real customs/client document evaluation;
- no external frontier-model batch experiment;
- no human-subject oversight study;
- no production cryptographic trust infrastructure;
- no claim that zero observed benchmark failures proves safety;
- no evidence that the proposed controller prevents catastrophic AI outcomes in the real world.

## Publication language rule

Use language such as:

- “in this synthetic benchmark”;
- “under the tested attack model”;
- “the results suggest”;
- “the experiment identifies a failure boundary”;
- “requires validation with real-model outputs / human reviewers.”

Avoid language such as:

- “solves agent safety”;
- “guarantees safe autonomy”;
- “proves independent verification”;
- “validated in real-world EXIM operations”;
- “human oversight is effective” before the participant study exists.
