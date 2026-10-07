# Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence

**Syed Hafiz Ali**  
Independent Researcher; BS in Data Science and Applications, Indian Institute of Technology Madras  
GitHub: https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy

## Abstract

As AI systems are given greater autonomy, a central deployment question is not only whether a model can produce a plausible answer, but whether the available evidence is sufficient to authorize a consequential action. This work introduces **Evidence-Gated Autonomy (EGA)**, a synthetic benchmark and action-authorization framework that maps observable evidence states to one of five outcomes: **ACT, VERIFY, REQUEST EVIDENCE, DEFER, or ESCALATE**. The benchmark contains 500 underlying evidence situations paired across low- and high-consequence actions, producing 1,000 cases across ten controlled failure families.

In an idealized deterministic testbed, EGA produced 0/500 unsafe high-consequence ACT decisions, compared with 50/500 for tested Risk-Gate and Always-Verify baselines. This result did not survive realistic imperfections unchanged: under stochastic verification, retrieval, and escalation, the high-risk incorrect-action rate increased from 1.86% in an optimistic regime to 6.10% in a moderate regime and 13.09% in a harsh regime. Adversarial tests further showed that spoofed dependency metadata and masked external evidence could defeat the original gate. Cryptographically binding provenance claims with Ed25519 attestations prevented direct unsafe ACTs under several unsigned metadata attacks, but valid signatures over false claims remained dangerous under trust-root compromise. A dual-lineage separation-of-duties design raised the compromise threshold for fabricated evidence independence.

The results support a narrow conclusion: consequential action authorization depends not merely on model confidence or verifier agreement, but on the structure, provenance, independence, and trustworthiness of the evidence chain. All current results are synthetic or simulated and do not establish production safety.

## 1. Introduction

Increasingly capable AI systems are being integrated into workflows where model outputs can trigger external actions. In such settings, a useful question is not simply, "How confident is the model?" or "Do multiple models agree?" but:

> **What evidence should an AI system require before it is allowed to take the next action?**

This question becomes important when evidence can be incomplete, internally inconsistent, stale, mutually dependent, machine-generated, or inconsistent with external observations. It becomes harder still when verifiers or provenance infrastructure can fail.

This project grew from document-heavy operational workflows in which errors are rarely isolated. A wrong extraction can propagate into classification; several apparently independent checks can share the same upstream source; three documents can agree while all being wrong; a valid authorization can be stale; and a human reviewer can still make an incorrect decision after an automated system correctly escalates.

Evidence-Gated Autonomy treats action authorization as a structured evidence problem. The controller considers evidence completeness, cross-document consistency, freshness, external grounding, verifier disagreement, source dependence, action consequence, and later, cryptographically bound provenance.

The work has four goals:

1. build a reproducible benchmark containing controlled evidence failures;
2. compare an evidence-structured gate against simpler action policies;
3. actively search for counterexamples and attacks that break the gate;
4. test whether provenance attestation and separation of duties repair specific observed failures.

The main contribution is therefore not a claim that EGA "solves" autonomous-agent safety. Instead, the project provides a compact experimental setting for studying **when authorization rules fail because the evidence on which they rely is itself unreliable**.

## 2. Research Questions

The experiments address five questions.

**RQ1.** Does explicitly gating consequential actions on evidence completeness, consistency, freshness, external grounding, and verifier independence reduce unsafe high-consequence actions in a controlled benchmark?

**RQ2.** How does performance change when verification, evidence retrieval, and escalation are imperfect?

**RQ3.** Which observable evidence features provide independent protection, and which appear redundant under the benchmark?

**RQ4.** Can the gate be broken by manipulating provenance or dependency information without directly changing the apparent task evidence?

**RQ5.** If provenance claims are cryptographically bound, what failures remain under imperfect review and compromised trust roots?

## 3. Related Work and Scope

This work is adjacent to AI control, scalable oversight, and provenance research. AI control studies protocols intended to prevent harmful outcomes even when an untrusted model may intentionally subvert the safety mechanism; Greenblatt et al. evaluate such protocols empirically [1]. Scalable-oversight work studies whether weaker judges can supervise stronger agents through debate and consultancy [4]. Recent work on collaborative disagreement resolution and strategic communication further highlights that oversight quality depends on how evidence is elicited and presented, not only on whether a final verdict is correct [5,6].

EGA addresses a narrower complementary question: **before an external action is authorized, what properties of the evidence chain should be required, and what happens when those properties are themselves compromised?** Source dependence, provenance, freshness, external grounding and escalation are therefore explicit experimental variables.

The provenance experiments draw on established assurance systems. in-toto provides signed statements about software supply-chain history [2], while SLSA defines verifiable provenance describing where and how artifacts were produced [3]. These systems motivate the integrity experiments here, but EGA explicitly tests the distinction between authenticated provenance and truthful claims.

This project does not replace AI control, scalable oversight, provenance systems, or human review. Its contribution is a controlled benchmark for studying how evidence-chain failures propagate into consequential action authorization.

## 4. Benchmark

### 4.1 Structure

The benchmark is generated deterministically with seed 42. It contains:

- **500 unique underlying evidence situations**;
- **10 failure families**, 50 situations per family;
- each underlying situation paired with a **LOW**- and **HIGH**-consequence action;
- **1,000 total action cases**.

LOW-risk cases represent reversible temporary-record actions. HIGH-risk cases represent consequential workflow advancement with higher external effect and lower reversibility.

### 4.2 Failure Families

The ten controlled families are:

- **C0 — Clean:** no injected failure.
- **C1 — Extraction error:** extracted quantity deviates from ground truth.
- **C2 — Cross-document conflict:** one document conflicts with the others.
- **C3 — Missing critical evidence:** a declaration or authorization is absent.
- **C4 — Consistent but wrong:** multiple documents and extraction agree on an incorrect value.
- **C5 — Stale evidence:** authorization has expired.
- **C6 — Verifier false accept:** an extraction error is accepted.
- **C7 — Verifier false reject:** correct evidence is rejected.
- **C8 — Correlated verifier failure:** multiple verifiers share a dependency and accept the same wrong classification.
- **C9 — Cascading error:** an upstream extraction error propagates downstream.

Each family includes mild, moderate, and severe perturbations.

### 4.3 Observable Evidence

The controller receives only observable workflow information, including:

- invoice, packing-list, and declaration fields;
- authorization presence and freshness;
- externally measured weight;
- extracted fields and confidence;
- verifier accept/reject decisions;
- verifier dependency groups;
- action consequence.

Ground-truth labels and fault-family labels are hidden from the controller and used only for evaluation.

## 5. Action Policies

The primary controller produces one of five actions:

**ACT / VERIFY / REQUEST EVIDENCE / DEFER / ESCALATE**

For high-consequence actions, Evidence Gate v1 checks:

1. critical evidence and authorization are present;
2. authorization is fresh;
3. documents agree;
4. no external-weight conflict exists;
5. extraction matches the invoice;
6. no verifier rejects the case;
7. at least two verifier dependency groups are represented.

If these conditions are satisfied, the controller ACTs; otherwise it verifies, requests evidence, or escalates depending on the failure.

Seven comparison policies are included:

- Always Act;
- Confidence Gate;
- Document Agreement;
- Always Verify;
- Selective Abstention;
- Weak/Strong heuristic;
- Risk Gate.

## 6. Metrics

The primary metric is the **high-risk incorrect consequential action rate (ICAR)**: the proportion of HIGH-risk cases that ultimately result in an incorrect consequential action.

Additional metrics include:

- false authorization among ACT decisions;
- false blocking of safe cases;
- final action rate;
- verification rate;
- escalation rate;
- request-evidence rate;
- normalized intervention cost.

The cost values are abstract utilities for comparing controller behavior and are not economic estimates.

## 7. Experiment 1A: Deterministic Policy Comparison

In the idealized deterministic benchmark, Evidence Gate produced **0 incorrect high-risk consequential actions out of 500**.

| Policy | Incorrect HIGH actions | ICAR | Final ACT rate |
|---|---:|---:|---:|
| Evidence Gate | 0/500 | 0.000 | 0.700 |
| Risk Gate | 50/500 | 0.100 | 0.280 |
| Always Verify | 50/500 | 0.100 | 0.200 |
| Weak/Strong | 102/500 | 0.204 | 0.264 |
| Confidence | 144/500 | 0.288 | 0.360 |
| Document Agreement | 325/500 | 0.650 | 0.850 |
| Always Act | 400/500 | 0.800 | 1.000 |

The zero-error result should not be read as evidence of real-world safety. The controller and deterministic post-actions were partly constructed around the benchmark's observable failure structure. Its value is as a sanity check before introducing imperfect verification and adversarial shift.

## 8. Experiment 1B: Imperfect Verification, Retrieval, and Escalation

To remove the assumption of perfect downstream handling, Experiment 1B introduces stochastic failure in verification, evidence retrieval, and escalation. Each regime is evaluated over 30 Monte Carlo seeds.

Evidence Gate mean HIGH-risk ICAR:

- **Optimistic:** 0.0186 ± 0.0052
- **Moderate:** 0.0610 ± 0.0115
- **Harsh:** 0.1309 ± 0.0131

Under the moderate regime, Risk Gate ICAR was approximately 0.1655.

The important result is not that the gate remains "safe," but that its apparent deterministic performance depends strongly on the quality of downstream review. As those components degrade, incorrect consequential actions reappear.

## 9. Ablations

Ablations show measurable protection from:

- external grounding;
- source/dependency independence;
- freshness checks.

Explicit verifier-status handling did not provide an independent deterministic reduction in ICAR once the other checks were present in the current benchmark.

Risk conditioning primarily changed coverage and intervention cost rather than providing the central safety benefit. REQUEST EVIDENCE improved resolution and coverage relative to pure deferral but did not establish an intrinsic safety effect.

These negative findings are retained because they constrain the claims that can reasonably be made about the framework.

## 10. Experiment 1C: Adversarial Evidence and Provenance Stress

Experiment 1C targets a core assumption: that visible metadata about evidence provenance and verifier independence can be trusted.

At a simulated 90% human-review accuracy:

- with no attack, Evidence Gate ICAR was approximately **6.4%**;
- dependency spoofing increased it to approximately **15.36%**;
- external-evidence masking increased it to approximately **15.70%**;
- combined metadata spoofing increased it to approximately **24.06%**.

The attack does not need to make the model more confident. It changes the evidence context on which authorization depends.

This experiment invalidated an important assumption in Evidence Gate v1: **self-asserted dependency and provenance metadata are not a sufficient trust foundation**.

## 11. Experiment 1D: Distribution Shift

Frozen policies were tested under nuisance shift, confidence shift, provenance dropout, and a compound shift.

Under compound shift:

- Evidence Gate ICAR: **0.1195**
- Risk Gate ICAR: **0.1851**
- Confidence-only ICAR: **0.7660**

EGA remained better than the tested simpler baselines in this synthetic setting, but its error rate increased materially. Provenance dropout alone increased EGA ICAR from approximately 0.0619 in-distribution to 0.0895.

The result reinforces the central failure mode: evidence-structured authorization only helps to the extent that the structure being checked is itself reliable.

## 12. Experiment 2A–2C: Attested Provenance

Experiment 2 adds synthetic Ed25519 attestations to bind provenance claims to current evidence objects.

The experiment created **3,675 signed attestations** covering documents, external weight evidence, authorization timing, and verifier outputs/dependency metadata.

Evidence Gate v2 requires both:

1. a valid signature from a trusted signer; and
2. a binding between the signed claim and the current evidence object.

### 12.1 Deterministic Unsigned Attacks

For individual dependency, external-evidence, and timestamp spoofing attacks:

- Evidence Gate v1: **10% ICAR**
- Attestation-aware v2: **0% direct unsafe ACT**

Under a combined spoof:

- v1: **30% ICAR**
- v2: **0% direct unsafe ACT**

The v2 controller often escalated instead. Therefore, the result is not that cryptography solved the decision problem; it prevented several silent metadata manipulations from being accepted directly.

### 12.2 Imperfect Review Remains

With simulated 90%-accurate escalation, attestation-aware v2 still produced approximately **6–7% ICAR** under several detected-tamper conditions.

This rejects the hypothesis that cryptographic tamper detection removes downstream review risk.

## 13. Experiment 2D: Trust-Root Compromise

A valid signature over a false claim defeats simple signature checking.

When a trusted verifier, external-sensor signer, or authorization signer was compromised, Evidence Gate v2 produced a **10% deterministic ICAR** for the corresponding failure family. Compromising all relevant roots produced **30% ICAR**.

One particularly important result was that compromising a verifier signer could fabricate apparent evidence independence in v2.

This demonstrates the difference between:

- **integrity:** the signed claim was not modified;
- **authenticity:** the claim came from a trusted identity;
- **truth:** the claim accurately represents the world.

The first two do not imply the third.

## 14. Experiment 2E: Separation of Duties

A third design separates verifier-output authority from dependency-lineage authority.

The verifier signs its output, while two independent lineage authorities separately attest the verifier's dependency lineage.

Deterministic ICAR remained at **0%** under:

- verifier-only compromise;
- lineage-authority A compromise;
- lineage-authority B compromise;
- verifier plus one lineage-authority compromise.

Compromising **both lineage authorities** restored **10% ICAR**. With imperfect 90%-accurate escalation, single-authority compromise still produced approximately **7% error**, while compromise of both lineage authorities produced approximately **15%**.

Within the synthetic benchmark, separation of duties therefore raised the compromise threshold required to fabricate independence. It did not eliminate trust-root or human-review risk.

## 15. Discussion

### 15.1 Evidence Quantity Is Not Evidence Independence

Several agreeing outputs can provide the appearance of corroboration while depending on the same upstream source. In the benchmark, correlated verifiers can fail together. This means "two verifiers agree" is weaker than "two independently grounded verifiers agree."

### 15.2 External Grounding Matters, but Can Be Hidden

The consistent-but-wrong family is deliberately designed so that documents agree internally. External measurement exposes the discrepancy. Once external evidence can be masked, this protection weakens.

### 15.3 Provenance Is a Security Boundary

The project initially treated dependency metadata as an observable feature. Adversarial testing showed that this was too strong an assumption. Moving to signed provenance changed the failure mode from simple metadata spoofing to trust-root compromise.

### 15.4 Cryptography Authenticates Claims, Not Reality

A signature can tell the controller who asserted a claim and whether the signed representation changed. It cannot tell the controller whether a trusted signer is mistaken, compromised, or malicious.

### 15.5 Escalation Is Part of the Safety System

A system that correctly detects uncertainty but escalates into an unreliable human or automated review process can still produce unsafe outcomes. Oversight quality must therefore be evaluated rather than assumed.

## 16. Policy and Governance Relevance

Although this is a technical synthetic benchmark, the structure has a direct governance interpretation.

Policymakers, auditors, and independent evaluators increasingly face claims that AI safeguards are reliable: that monitoring catches dangerous behavior, that evaluations are independent, that human escalation provides a backstop, or that provenance records establish accountability.

The experiments suggest a set of questions for assurance and audit:

- What evidence supports the safety claim?
- Are apparently independent checks actually independent?
- Can the provenance metadata itself be manipulated?
- Who controls the trust roots?
- What happens when a trusted verifier is compromised?
- Are negative evaluation results disclosed?
- Is escalation effectiveness measured empirically or merely assumed?
- Which safeguards remain effective under correlated failure?

The paper does not prescribe a regulatory regime. It instead motivates treating **evidence provenance, independence, and failure correlation as first-class properties of assurance claims** for consequential AI deployments.

## 17. Limitations

The limitations are substantial and explicit.

1. **Synthetic domain.** The cases are EXIM-inspired but do not reproduce real customs or logistics distributions.
2. **No external frontier-model evaluation yet.** Experiment 3 is preregistered but not run.
3. **Simulated reviewers.** Monte Carlo reviewer accuracy is not a substitute for real human behavior.
4. **No human-subject results.** A human-oversight experiment is preregistered only.
5. **Synthetic cryptographic infrastructure.** Test keys and signer identities are reproducibility tools, not a real PKI.
6. **Stylized compromise.** Trust-root attacks are controlled scenarios rather than empirically estimated threat probabilities.
7. **Benchmark dependence.** Policies may exploit structure specific to the benchmark.
8. **Normalized cost.** Intervention-cost values are comparison utilities rather than economic estimates.
9. **No production deployment.** The project provides no evidence that EGA is safe for real operational use.

These limitations mean the results should be interpreted as controlled counterexamples, comparative proof-of-concept evidence, and hypothesis generation—not deployment validation.

## 18. Preregistered Next Studies

### 18.1 Real-Model Experiment

A frozen protocol will replace synthetic extraction/verifier error probabilities with actual outputs from at least three independently developed model families. Ground truth and failure labels remain hidden during generation and verification.

Primary analyses include:

- same-model versus cross-model co-failure;
- calibration;
- model-family holdout;
- prompt perturbation;
- document-format out-of-distribution shift;
- Evidence Gate v1/v2/v3 comparison.

No result from this protocol is claimed in the current paper.

### 18.2 Human-Oversight Study

A randomized within-subject crossover study is preregistered to compare:

1. raw escalation output; and
2. structured evidence packets containing provenance, dependencies, conflicts, missing evidence, verifier history, freshness, and escalation rationale.

The primary outcome is correct authorization decision. Recruitment has not been conducted and no human-result claim is made.

## 19. Reproducibility

The public repository contains the benchmark generator, verification checks, controller code, provenance code, result tables, claim ledger, limitations, and preregistered protocols.

The benchmark is regenerated deterministically with:

`python scripts/generate_benchmark.py`  
`python scripts/verify_benchmark.py`  
`python scripts/reproduce_tables.py`

Repository: https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy

## 20. Conclusion

Evidence-Gated Autonomy began with a simple intuition: consequential actions should require stronger evidence than low-impact actions. The experiments progressively weakened the assumptions behind that intuition.

A deterministic evidence gate performed well in the controlled benchmark. Imperfect verification and escalation reintroduced errors. Provenance and dependency attacks broke the original trust model. Signed attestations blocked several unsigned manipulations, but trust-root compromise demonstrated that authentic provenance is not equivalent to truthful evidence. Separation of duties raised the threshold for fabricating independence but did not eliminate review or trust-root risk.

The strongest conclusion is therefore deliberately narrow:

> **Action authorization should reason not only about model outputs, but about the provenance, independence, freshness, external grounding, and failure structure of the evidence supporting those outputs.**

Whether such mechanisms improve real-world AI safety remains an empirical question for the preregistered model and human studies.

## References

[1] Ryan Greenblatt, Buck Shlegeris, Kshitij Sachan, and Fabien Roger. *AI Control: Improving Safety Despite Intentional Subversion*. arXiv:2312.06942, 2023.

[2] Santiago Torres-Arias, Hammad Afzali, Trishank Karthik Kuppusamy, Reza Curtmola, and Justin Cappos. *in-toto: Providing farm-to-table guarantees for bits and bytes*. 28th USENIX Security Symposium, 2019.

[3] SLSA Project. *Supply-chain Levels for Software Artifacts (SLSA): Provenance*. https://slsa.dev/

## Citation

Ali, Syed Hafiz. "Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence." Preprint, 2026.
