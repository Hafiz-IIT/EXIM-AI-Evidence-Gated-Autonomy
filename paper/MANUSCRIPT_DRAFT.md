# Evidence-Gated Autonomy: When Should an AI System Be Allowed to Act?

**Author:** Syed Hafiz Ali  
**Status:** Working manuscript draft. Experiments 1A–2E completed in the public repository; Experiment 3 and the human-review study are prospective and are not reported as results.

## Abstract

As AI systems move from generating recommendations to executing consequential actions, capability alone is an incomplete basis for authorization. A model may be confident while relying on incomplete, stale, conflicting, correlated, or weakly grounded evidence. This work studies **Evidence-Gated Autonomy (EGA)**, an action-authorization layer that selects among `ACT`, `VERIFY`, `REQUEST EVIDENCE`, `DEFER`, and `ESCALATE` using evidence completeness, cross-source consistency, freshness, external grounding, provenance, source dependence, verifier behavior, and action consequence. We evaluate the approach on a deterministic synthetic benchmark of 500 underlying evidence states paired across low- and high-consequence actions, spanning ten controlled failure families. In the idealized deterministic setting, the tested Evidence Gate produced 0/500 unsafe HIGH-risk ACT decisions, compared with 50/500 for Risk Gate and Always Verify under the benchmark's downstream-action semantics. Under stochastic imperfect verification/review, the Evidence Gate's mean high-risk incorrect-action rate rose to approximately 1.9%, 6.1%, and 13.1% across optimistic, moderate, and harsh regimes, showing that the approach depends materially on the reliability of its supporting processes. Adversarial stress tests further showed that self-asserted dependency/provenance metadata is a weak trust foundation. Signed attestations blocked specific unsigned-tampering attacks, but compromised trust roots could still produce valid signatures over false claims. A separation-of-duties variant raised the compromise threshold in the tested synthetic design. The results support a narrow conclusion: reliable autonomous action depends not only on how much evidence is available, but on the structure, provenance, independence, and trust assumptions underlying that evidence. These experiments are a reproducible proof-of-concept, not real-world safety validation. A frozen external-model protocol is defined for the next empirical stage.

## 1. Introduction

AI agents increasingly combine language-model reasoning with retrieval, tool use, memory, software execution, and external APIs. This changes the safety question. A system that only proposes text can often be reviewed after generation; a system that can submit, modify, transfer, schedule, authorize, or trigger external processes creates a more direct connection between model error and real-world consequence.

A central design mistake is to treat capability evidence as authorization evidence. High model confidence does not establish that the underlying documents are complete. Agreement between multiple outputs does not establish independence. Cross-document consistency does not establish truth. A verifier can share the same failure mode as the system it checks. A provenance record can be authentic while the trusted signer is compromised. A human reviewer can be present while lacking the information, time, or authority required for meaningful intervention.

This paper asks:

> **What evidence should an AI system require before it is allowed to take the next consequential action?**

We study this question through an **Evidence-Gated Autonomy** controller that treats action authorization as a separate decision layer. Rather than returning only “continue” or “stop,” the controller can choose among five outcomes:

- **ACT** — authorize the proposed action;
- **VERIFY** — obtain an additional check;
- **REQUEST EVIDENCE** — seek missing or better evidence;
- **DEFER** — withhold autonomous action;
- **ESCALATE** — transfer the decision to a higher-authority reviewer.

The project grew from a multi-stage document and operational workflow in which extraction errors, cross-document inconsistencies, missing authorization, stale evidence, correlated verification, and downstream propagation could have different consequences depending on the action being attempted. The benchmark is synthetic and intentionally domain-inspired rather than a claim about real customs or logistics distributions.

### Contributions

This work makes four evidence-bounded contributions:

1. **A reproducible synthetic benchmark** that pairs the same underlying evidence state with low- and high-consequence actions across ten controlled failure families.
2. **A multi-outcome action-gating formulation** that separates evidence collection/verification from authorization and explicitly models evidence completeness, consistency, freshness, external grounding, dependence, and consequence.
3. **A sequence of adversarial tests** showing failure boundaries of the original gate, including provenance spoofing, correlated verifier failure, and trust-root compromise.
4. **A claim-governance and prospective external-model protocol** designed to prevent synthetic results from being overstated as deployment evidence.

The paper does **not** claim that EGA makes frontier agents safe, that its percentages estimate real-world accident rates, that the provenance mechanism is cryptographically novel, or that a human-review study has already been completed.

## 2. Problem Formulation

Let an AI-enabled workflow propose action `a` based on observable evidence `E`. A conventional pipeline often maps model output directly to action, perhaps with a confidence threshold or a fixed human-review checkpoint. EGA inserts an authorization function:

`G(a, E) -> {ACT, VERIFY, REQUEST_EVIDENCE, DEFER, ESCALATE}`

where `E` may contain:

- document presence and completeness;
- cross-document consistency;
- external measurements or observations;
- authorization state and freshness;
- model extraction/classification outputs;
- verifier outputs;
- verifier dependency groups;
- provenance and attestation information;
- action consequence and reversibility.

The central distinction is between **agreement** and **independent support**. If two verifiers share a model family, prompt, retrieval source, derived artifact, or corrupted upstream state, agreement may not represent two independent reasons for action.

Likewise, provenance provides evidence about **where a claim came from and whether it was modified**, not whether the claim is true. Trust therefore depends on a chain: evidence generation, dependency representation, attestation, trust-root integrity, gating logic, and escalation quality.

## 3. Benchmark

### 3.1 Dataset structure

Benchmark version `0.3` is generated deterministically with seed `42`. It contains 500 unique underlying evidence states. Each state is paired across two action contexts:

- a LOW-risk, highly reversible local action;
- a HIGH-risk, low-reversibility operational action.

This produces 1,000 total cases.

The benchmark contains ten failure families, 50 underlying states per family:

- `C0_clean`
- `C1_extraction_error`
- `C2_cross_document_conflict`
- `C3_missing_critical_evidence`
- `C4_consistent_but_wrong`
- `C5_stale_evidence`
- `C6_verifier_false_accept`
- `C7_verifier_false_reject`
- `C8_correlated_verifier_failure`
- `C9_cascading_error`

Cases vary in severity and observable model confidence. Hidden ground truth is used only for evaluation.

### 3.2 Why pair by action consequence?

The same evidence state may justify a reversible local save while failing to justify a consequential external action. This pairing isolates a central hypothesis: **authorization thresholds should depend on what the system is about to do, not only on how confident the model is about its prediction.**

## 4. Policies and Baselines

The repository contains several baselines:

- Always Act
- Confidence Gate
- Document Agreement
- Always Verify
- Selective Abstention
- Weak/Strong policy
- Risk Gate
- Evidence Gate v1

The original Evidence Gate authorizes HIGH-risk action only after checking for critical-document presence, authorization presence/freshness, document agreement, external conflicts, extraction consistency, verifier rejection, and at least two dependency groups among verifiers.

Later experiments add provenance-aware and separation-of-duties variants.

## 5. Experiments

### 5.1 Experiment 1A — deterministic controller evaluation

Experiment 1A evaluates all policies under idealized deterministic verification/escalation behavior.

**Result.** Evidence Gate produced **0/500** unsafe HIGH-risk ACT decisions. Risk Gate and Always Verify each produced **50/500** under the benchmark's downstream-action semantics.

This is a proof-of-concept result only. The setting idealizes supporting verification and escalation and should not be interpreted as an estimate of deployment safety.

### 5.2 Experiment 1B — imperfect verification and review

Experiment 1B replaces idealized supporting processes with stochastic imperfect verification, retrieval, and review.

Evidence Gate mean HIGH-risk incorrect-action rate:

- optimistic regime: **~1.9%**;
- moderate regime: **~6.1%**;
- harsh regime: **~13.1%**.

Under the moderate regime, Risk Gate was approximately **16.5%**.

**Interpretation.** The controller's apparent safety advantage is not intrinsic to the gate alone. It depends on the reliability of verification, evidence acquisition, and escalation.

### 5.3 Ablations and distribution shift

Ablations showed measurable protection from:

- external grounding;
- source/dependency independence;
- freshness checks.

Explicit verifier-status handling did not independently improve deterministic incorrect-action rate once stronger checks were already present. Risk conditioning mainly improved coverage/cost. REQUEST EVIDENCE improved resolution/coverage relative to pure deferral but did not establish an intrinsic safety advantage under imperfect retrieval.

Out-of-distribution and compound-shift tests degraded the richer gate materially, although it remained stronger than the tested simpler baselines in the recorded synthetic conditions.

### 5.4 Experiment 1C — adversarial evidence and provenance metadata

Adversarial manipulation exposed a major failure boundary. Changing dependency metadata or masking external evidence could cause the original gate to accept unsafe actions. Combined metadata/evidence spoofing increased incorrect HIGH-risk actions further.

The important negative result is that **the gate cannot safely rely on self-asserted metadata about evidence independence**.

### 5.5 Experiments 2A–2D — signed provenance

Experiment 2 introduces signed provenance attestations. In deterministic unsigned-spoofing tests, the original gate reached **10%** incorrect HIGH-risk actions under individual dependency, external-evidence, and timestamp attacks, and **30%** under the combined attack.

An attestation-aware gate rejected evidence whose signed claims no longer matched the current objects and prevented direct unsafe ACTs in those unsigned-tampering conditions.

However, this did not eliminate downstream risk. With a simulated 90%-accurate escalation process, the attestation-aware system retained approximately **6–7%** incorrect HIGH-risk actions under several tamper conditions because detected cases could still be mishandled after escalation.

### 5.6 Trust-root compromise

Signed provenance changes the attack surface rather than establishing truth. If a trusted verifier, sensor, or authorization signer is compromised, it can produce a valid signature over a false claim.

In the synthetic compromise experiment, compromise of a relevant trust root restored a **10%** failure family; compromise of all relevant roots restored **30%**.

### 5.7 Experiment 2E — separation of duties

A separation-of-duties variant moved dependency-lineage authority away from the verifier and required agreement from two independent lineage authorities.

In the deterministic synthetic test, this variant remained at **0%** incorrect HIGH-risk actions under:

- verifier-only compromise;
- either single lineage-authority compromise;
- verifier plus one lineage-authority compromise.

Compromise of both lineage authorities restored **10%** incorrect HIGH-risk actions. With imperfect escalation, single-authority compromise still produced approximately **7%** error due to review failures, while compromise of both lineage authorities produced approximately **15%**.

This is not a general security proof. It shows that, under the tested threat model, separating authorities increased the number of compromises required to fabricate apparent independence.

## 6. Main Findings

### 6.1 Evidence quantity is not evidence structure

Multiple agreeing model outputs do not necessarily provide multiple independent reasons for action. The experiments make dependency structure operational rather than treating “number of verifiers” as a sufficient statistic.

### 6.2 Verification is a chain of assumptions

“Verification” is often discussed as if it were a single reliable operation. Here, safety depends on several distinct assumptions:

1. the right evidence is available;
2. dependency relationships are represented correctly;
3. provenance metadata is authentic;
4. trust roots are uncompromised;
5. the gate applies the intended policy;
6. escalation/review is reliable.

A failure at any stage can dominate the end-to-end result.

### 6.3 Provenance authenticates claims, not truth

Cryptographic binding can make undetected modification harder. It cannot establish that the signer observed the world correctly or acted honestly. This distinction is essential for any agent-safety architecture that imports software-supply-chain attestation ideas into AI decision authorization.

### 6.4 Human oversight is not automatically a safety mechanism

The stochastic experiments show that escalation can simply relocate failure downstream. Meaningful human oversight requires evidence, timing, authority, visibility, and sufficient reviewer capability. The current repository contains a preregistered human-review protocol but no human-subject results.

## 7. Related Work

**This section is intentionally incomplete in this working draft.** A dedicated literature audit is in progress before submission. The final version will distinguish EGA from, and connect it to:

- selective prediction and abstention;
- runtime monitoring and safety filters;
- scalable/amplified oversight;
- human-in-the-loop and meaningful human oversight;
- AI-agent control and release gating;
- verifier and ensemble dependence;
- provenance/attestation and software supply-chain security;
- safety cases and deployment assurance;
- tool-using agent failure evaluation.

The paper will not claim novelty for digital signatures, provenance attestations, separation of duties as a general security concept, or human escalation. The research question is narrower: whether combining evidence structure, action consequence, provenance, and independence checks changes authorization behavior under controlled failures.

## 8. Experiment 3 — Frozen Prospective External-Model Evaluation

Experiment 3 is **not yet a result**. Its protocol is frozen in `docs/EXP3_FREEZE.md` and `docs/REAL_MODEL_EXPERIMENT_PROTOCOL.md`.

The study will replace simulated extraction/verifier errors with actual model outputs while keeping ground truth hidden and policies fixed. It will compare same-model self-verification and cross-family verification, evaluate model-family holdout and document-format OOD conditions, and retain refusals, parser failures, timeouts, and other inconvenient outputs rather than silently discarding them.

The primary outcome is HIGH-risk incorrect consequential action rate. Secondary outcomes include false authorization, false blocking, autonomous coverage, verification/request/escalation rates, verifier co-failure, calibration, latency, and cost.

Any prompt, threshold, parser, or policy change after test-set inspection creates a new experiment version and must be evaluated on a fresh holdout.

## 9. Limitations

The current evidence has important limitations:

- all benchmark cases are synthetic and EXIM-inspired rather than sampled from real customs distributions;
- Monte Carlo verifier/reviewer accuracy is simulated;
- cost units in the current experiments are normalized rather than economic estimates;
- cryptographic identities are synthetic test keys;
- trust-root attacks are stylized;
- the benchmark is small relative to the diversity of real agent workflows;
- no external frontier-model batch evaluation has been completed;
- no human-subject study has been completed;
- no production deployment or real client dataset has been evaluated.

The experiments therefore establish controlled counterexamples, comparative proof-of-concept behavior, and failure boundaries—not real-world safety.

## 10. Threats to Validity

### Construct validity

The benchmark operationalizes “safe to act” using known synthetic ground truth. Real-world authorization can involve legal, institutional, ethical, and contextual factors absent from this representation.

### Internal validity

Some policy advantages may depend on benchmark construction. The paired design reduces some confounding from action consequence but does not remove benchmark-specific assumptions.

### External validity

The benchmark does not establish performance on natural documents, real model distributions, long-horizon autonomous tasks, adversarial real users, or production systems.

### Security validity

The provenance threat model covers selected metadata and trust-root attacks. It is not a complete cryptographic or systems-security analysis.

## 11. Falsification Criteria

The richer evidence-gating architecture has **not earned its complexity** if a simpler baseline achieves equal or lower unsafe-action rate at comparable autonomous coverage, cost, latency, and escalation burden on frozen external-model evaluations.

Similarly, claims about verifier diversity should be weakened if cross-family verification does not reduce co-failure relative to same-model verification under controlled comparisons.

This project treats those as legitimate outcomes rather than failures of the research program.

## 12. Conclusion

The experiments support a narrower claim than “verification makes agents safe.” In controlled synthetic settings, action authorization improved when the controller reasoned about evidence completeness, freshness, external grounding, and dependency structure rather than model confidence or verifier count alone. Adversarial testing then exposed a deeper problem: metadata about evidence independence and provenance is itself part of the trust surface. Signed attestations repaired selected tampering failures but shifted attention to trust-root compromise; separation of duties raised the compromise threshold in the tested design but did not eliminate downstream review risk.

The resulting research direction is therefore not simply to add more verifiers. It is to determine **what evidence can justifiably authorize a consequential AI action, how that evidence should be structured and authenticated, and how the system should behave when the trust chain is incomplete or compromised**.

The next empirical test is the frozen external-model Experiment 3. Until that study is executed, the current contribution remains a reproducible synthetic proof-of-concept and a set of experimentally identified failure boundaries.
