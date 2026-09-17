# Evidence-Gated Autonomy: Authorization Under Uncertain, Dependent, and Potentially Compromised Evidence

**Draft status:** manuscript scaffold grounded in Experiments 1A–2E. Experiment 3 real-model results are not yet included and must not be inferred from this draft.

## Abstract

As AI systems become more agentic, a capability question—whether a model can complete a task—becomes distinct from an authorization question—whether the available evidence is sufficient to permit a consequential action. We study a simple evidence-gated controller that can ACT, VERIFY, REQUEST EVIDENCE, DEFER, or ESCALATE based on evidence completeness, consistency, freshness, provenance, source dependence, external grounding, verifier behavior, and action consequence. We evaluate the controller in a synthetic benchmark containing 500 underlying evidence states paired across low- and high-consequence actions and ten controlled failure families. In the deterministic benchmark, the evidence gate produced 0/500 unsafe high-consequence ACT decisions, while selected simpler baselines failed on correlated or externally inconsistent conditions. Under stochastic verification and escalation, performance degraded materially, demonstrating that review stages are themselves failure-bearing. Adversarial provenance experiments further showed that self-asserted dependency metadata is a weak trust foundation: signed attestations blocked unsigned tampering, but valid signatures over false claims remained dangerous under trust-root compromise. A separation-of-duties variant raised the compromise threshold in the synthetic setting but did not eliminate downstream review risk. These results do not establish real-world safety. They instead identify a narrower systems problem: authorization reliability depends not only on how much evidence agrees, but on how evidence is grounded, how sources depend on one another, and which trust roots can vouch for the claims used by an action gate. A frozen real-model protocol is provided for follow-up evaluation.

## 1. Introduction

Agentic AI systems increasingly operate across multi-stage workflows in which model outputs can trigger external effects. In such settings, task success and action authorization are not equivalent. A system may be capable of producing an apparently coherent plan or extraction while relying on stale, incomplete, mutually dependent, or compromised evidence.

This work asks:

> **What evidence should an AI system require before it is allowed to take the next action?**

The motivating distinction is between **capability** and **authorization**. Capability evaluation asks whether a system can produce a useful answer or complete a task. Authorization asks whether the current evidence is sufficiently trustworthy for the system to take a specific action with a particular consequence and reversibility profile.

We study an evidence-gated policy with five possible outcomes:

`ACT / VERIFY / REQUEST EVIDENCE / DEFER / ESCALATE`

Rather than treating verification as a single binary check, the controller reasons over several evidence properties: completeness, cross-document consistency, freshness, external grounding, provenance, source dependence, verifier state, and action consequence.

The project makes four bounded contributions:

1. a reproducible synthetic benchmark separating extraction error, agreement failure, stale evidence, correlated verifier failure, and cascades;
2. a controller comparison showing where evidence-aware gating differs from confidence-only, agreement-only, always-verify, and risk-only baselines;
3. adversarial provenance experiments demonstrating that authentic metadata and truthful evidence are different properties, especially under compromised trust roots;
4. a frozen protocol and executable scaffold for replacing simulated machine errors with real external model outputs without changing the benchmark truth.

The work is a proof-of-concept, not a production safety validation.

## 2. Problem Formulation

Let an action `a` have a consequence profile including risk level, external effect, and reversibility. Let the system observe an evidence state `E` containing documents, machine extractions, verifier outputs, external measurements, authorization records, provenance claims, and dependency metadata.

We study a controller:

`G(E, a) -> {ACT, VERIFY, REQUEST_EVIDENCE, DEFER, ESCALATE}`

The controller's purpose is not to prove that the world state is true. Its purpose is to decide whether the currently observed evidence is sufficient to authorize the next action under a defined benchmark.

The central failure modes are:

- incomplete evidence;
- mutually inconsistent evidence;
- mutually consistent but false evidence;
- stale authorization;
- extraction error;
- false verifier acceptance;
- false verifier rejection;
- correlated verifier failure;
- evidence/provenance spoofing;
- cascading downstream error.

## 3. Benchmark

### 3.1 Structure

The benchmark contains 500 unique underlying evidence states across ten controlled families (C0–C9). Each underlying state is paired into a LOW-consequence and HIGH-consequence action, producing 1,000 cases total.

The paired design holds the evidence state fixed while changing consequence and reversibility. This permits direct examination of whether the controller treats identical evidence differently when the downstream action is more consequential.

### 3.2 Failure families

- **C0 Clean:** evidence is complete and mutually consistent with hidden truth.
- **C1 Extraction Error:** machine extraction differs from benchmark truth.
- **C2 Cross-Document Conflict:** one document conflicts with the others.
- **C3 Missing Critical Evidence:** declaration or authorization is missing.
- **C4 Consistent but Wrong:** documentary and machine evidence agrees but conflicts with hidden truth/external grounding.
- **C5 Stale Evidence:** authorization is expired.
- **C6 Verifier False Accept:** the extraction is wrong while verifiers accept.
- **C7 Verifier False Reject:** evidence is safe while verifiers reject.
- **C8 Correlated Verifier Failure:** multiple verifiers share a dependency group and support the same wrong evidence.
- **C9 Cascading Error:** an upstream error propagates into a downstream derived field.

### 3.3 Hidden truth

Benchmark truth and fault labels are retained for evaluation but are not assumed to be available to the controller. The Experiment 3 scaffold additionally strips `ground_truth`, `fault`, and `safe_to_act` from all model-facing cases.

## 4. Controllers and Baselines

The benchmark compares the evidence-aware controller against simpler policies including:

- Always Act;
- confidence threshold;
- document agreement;
- Always Verify;
- selective abstention;
- weak/strong routing;
- risk gate.

The evidence gate checks high-consequence actions for missing or stale evidence, cross-document disagreement, external conflicts, extraction mismatch, verifier rejection, and insufficient verifier dependency diversity before authorizing ACT.

This controller is intentionally simple and interpretable. The goal is not to claim optimality, but to make failure mechanisms inspectable.

## 5. Metrics

Primary metrics include:

- high-risk incorrect consequential action rate (ICAR);
- false authorization rate;
- false block rate;
- action coverage;
- verification / request / escalation rates;
- co-failure rate;
- cascade/action reach;
- latency and cost in stochastic or real-model conditions.

For zero observed failures, denominators and uncertainty bounds should be reported rather than interpreting the observed rate as a guarantee.

## 6. Results

### 6.1 Deterministic controller evaluation

In Experiment 1A, the Evidence Gate produced **0/500** unsafe HIGH-risk ACT decisions in the deterministic benchmark. Risk Gate and Always Verify each produced **50/500** in the tested setup.

The zero count is a benchmark observation only. It does not imply zero real-world failure probability.

### 6.2 Imperfect verification and escalation

Experiment 1B introduced stochastic imperfection in verification, evidence retrieval, and review. Evidence Gate's mean high-risk incorrect-action rate increased to approximately:

- **1.9%** in the optimistic regime;
- **6.1%** in the moderate regime;
- **13.1%** in the harsh regime.

Under the moderate regime, Risk Gate was approximately **16.5%**.

The important result is not merely the ranking. The experiment shows that a controller that routes uncertain cases into verification or escalation inherits the reliability of those downstream stages.

### 6.3 Ablations

Ablations show measurable protection in the benchmark from:

- external grounding;
- evidence-source independence;
- freshness checks.

Explicit verifier-status handling did not independently reduce deterministic incorrect-action rate after the other checks were present. Risk conditioning primarily altered coverage and cost in the current benchmark.

### 6.4 Adversarial evidence and provenance

Experiment 1C showed that changing dependency metadata or masking external evidence can cause the original gate to authorize unsafe actions. Under combined metadata/evidence attacks, failure rose materially.

Experiment 2 added signed provenance attestations. Under unsigned spoofing, the original gate reached 10% incorrect high-risk actions on individual dependency, external-evidence, and timestamp attacks and 30% under the combined attack. An attestation-aware variant prevented direct unsafe ACT decisions in these unsigned-tampering conditions by rejecting evidence whose signed claims no longer matched the current objects.

### 6.5 Trust-root compromise

Signing evidence does not establish truth. If a trusted signer can generate a valid signature over a false claim, the trust mechanism can faithfully authenticate a lie.

Under synthetic trust-root compromise, the attestation-aware gate again failed on defined families. A dual-lineage separation-of-duties variant raised the threshold: verifier-only compromise, one lineage-authority compromise, or verifier plus one lineage-authority compromise did not reproduce the deterministic independence fabrication tested earlier. Compromise of both lineage authorities restored the failure.

With imperfect escalation, single-authority compromise still produced error due to review failures. Separation of duties therefore changed the attack threshold; it did not remove all downstream risk.

## 7. Negative Results

Three negative results are important to preserve:

1. Explicit verifier-status handling added no independent deterministic protection once other checks were present.
2. Risk conditioning mainly improved coverage/cost in the current benchmark rather than producing an independent universal safety effect.
3. REQUEST EVIDENCE improved resolution/coverage over pure deferral but did not establish an intrinsic safety advantage in the stochastic setup.

These findings constrain the design rather than weakening the paper.

## 8. Interpretation

The experiments support a narrower statement than "verification makes agents safe."

Reliability depends on a chain of assumptions:

1. required evidence exists;
2. evidence refers to the current state rather than a stale one;
3. independent-looking evidence is not secretly dependent;
4. provenance claims are authentic;
5. trusted signers are not compromised;
6. escalation/review works when the controller refuses to act.

This shifts the relevant object from **evidence quantity** to **evidence structure and trust**.

Multiple agreeing model outputs are not automatically multiple reasons for action. Cryptographic integrity is not semantic truth. Human escalation is not automatically meaningful oversight.

## 9. Relationship to Existing Research

This work sits at the intersection of several established areas:

- selective prediction and abstention;
- runtime assurance and safety filtering;
- AI control and oversight;
- verifier-based evaluation;
- provenance and attestation;
- human-in-the-loop decision systems;
- safety cases and deployment governance.

The novelty claim should therefore remain narrow. The contribution is **not** the invention of abstention, verification, cryptographic signing, or human escalation. The specific research object is the interaction among evidence sufficiency, source dependence, provenance integrity, trust-root compromise, action consequence, and escalation in an inspectable authorization controller.

A current literature audit is being maintained separately and should be converted into formal citations before submission.

## 10. Experiment 3 — Real-Model Follow-Up

The next experiment replaces synthetic machine-error probabilities with saved outputs from real model families while preserving frozen hidden benchmark truth.

Required comparisons include:

- same-family self-verification;
- cross-family verification;
- multiple verifier families;
- model-family holdout;
- prompt perturbation;
- document-format/OOD shift.

The repository contains an executable provider-neutral schema, blinded-case builder, and evaluator. No real-model results are claimed until raw calls are collected under the frozen protocol.

A current implementation gap is explicitly documented: the reusable `src/` package exposes Evidence Gate v1 but not the later v2/v3 provenance-aware gates as callable controller functions. Those variants must be reconstructed and regression-tested against Experiment 2 results before they are included in Experiment 3.

## 11. Threats to Validity

### Construct validity

The benchmark operationalizes evidence quality using synthetic documents, explicit dependency groups, and known hidden truth. Real systems may have ambiguity that cannot be represented by these fields.

### External validity

No current result demonstrates performance on live customs operations, production agents, real client documents, or safety-critical infrastructure.

### Dependence modeling

Dependency groups are explicit in the synthetic benchmark. Real verifier dependence can arise through shared pretraining data, tooling, retrieval systems, prompts, infrastructure, or correlated incentives and may be difficult to observe.

### Human oversight

Current review behavior is simulated. The preregistered human-oversight study has not been run.

### Provenance

Experiment 2 uses a synthetic Ed25519 test setup and deterministic keys for reproducibility. This is not a production PKI or institutional trust system.

### Model evaluation

No external model-family batch has yet been executed. Experiment 3 is protocol/scaffold only until raw model outputs exist.

## 12. Conclusion

Evidence-gated authorization reframes a common agent-safety problem: the question is not only whether an AI system can produce a plausible action, but whether the current evidence warrants allowing that action to occur.

The synthetic experiments show that evidence-aware gating can outperform simpler rules under the tested conditions, but also expose where that advantage breaks: correlated verification, spoofed provenance, compromised trust roots, and imperfect escalation.

The resulting research direction is therefore not "add more verifiers." It is to understand which evidence relationships are sufficiently trustworthy to support consequential authorization, how those relationships fail under attack and distribution shift, and when an autonomous system should refuse to act.