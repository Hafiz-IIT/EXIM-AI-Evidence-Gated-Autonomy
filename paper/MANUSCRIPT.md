# Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence

**Syed Hafiz Ali**  
BS in Data Science and Applications (student), Indian Institute of Technology Madras  
GitHub: https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy

## Abstract

As AI systems are given greater autonomy, a central deployment question is not only whether a model can produce a plausible answer, but whether the available evidence is sufficient to authorize a consequential action. This work introduces **Evidence-Gated Autonomy (EGA)**, a synthetic benchmark and action-authorization framework that maps observable evidence states to one of five outcomes: **ACT, VERIFY, REQUEST EVIDENCE, DEFER, or ESCALATE**. The benchmark contains 500 underlying evidence situations paired across low- and high-consequence actions, producing 1,000 cases across ten controlled failure families.

In an idealized deterministic testbed, EGA produced 0/500 unsafe high-consequence ACT decisions, compared with 50/500 for tested Risk-Gate and Always-Verify baselines. This result did not survive realistic imperfections unchanged: under stochastic verification, retrieval, and escalation, the high-risk incorrect-action rate increased from 1.86% in an optimistic regime to 6.10% in a moderate regime and 13.09% in a harsh regime. Adversarial tests further showed that spoofed dependency metadata and masked external evidence could defeat the original gate. Cryptographically binding provenance claims with Ed25519 attestations prevented direct unsafe ACTs under several unsigned metadata attacks, but valid signatures over false claims remained dangerous under trust-root compromise. A dual-lineage separation-of-duties design raised the compromise threshold for fabricated evidence independence. A subsequent four-authority stress test on benchmark v0.4 found that witness-authority compromise alone produced 50 unsafe ACT decisions among 700 HIGH-risk cases; capture-plus-witness and key-administration trust-store compromise each produced 300, while compromise of the final authorization authority produced 600. These are deterministic synthetic outcomes under explicit capabilities, not real-world risk estimates. A separate authenticated witness-quorum sensitivity study with bounded false-reject recovery reached 100/100 safe-action coverage in its honest baseline, but 2-of-3 still admitted 50/700 unsafe ACTs under two-witness collusion and registry-root compromise; 3-of-3 blocked those modeled cases but not full-roster compromise and failed closed when a credential was invalid. These are deterministic synthetic outcomes, not real-world probabilities.

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

## 21. Supplementary Reconstruction: Document-Root Attestation (Benchmark v0.4)

This section reports a subsequent synthetic extension and is **not merged into the historical v0.3 benchmark tables or the original Experiment 2 results**. Benchmark v0.4 contains 700 unique underlying situations paired across LOW/HIGH actions, for 1,400 total cases and 14 fault families. The document-root threat runner evaluates its 700 HIGH-risk cases.

The document-root attestation signs canonical hashes of both raw document instances and normalized document slots, together with tenant and case identifiers, signer/key identity, issuance and expiry times, and a nonce. The verifier checks the trusted-key registry, revocation state, tenant/case scope, validity window, content digests, nonce replay state, and Ed25519 signature. The experiment uses deterministic test-only keys and process-local replay state.

The full CI run [43955044311](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43955044311) passed the regression suite, benchmark generation and integrity checks, v1/v2 reconstruction, document-root threat runner, artifact uploads, historical-table loading, and manuscript compilation. The nine document-root scenarios each contain 700 HIGH-risk cases:

| Scenario | Attestation accepted | Rejected | Downstream ACT | Unsafe ACT |
|---|---:|---:|---:|---:|
| Valid baseline | 700 | 0 | 50 | 0 |
| Raw document-instance tampering | 0 | 700 | 0 | 0 |
| Coherent rewrite without trusted private key | 0 | 700 | 0 | 0 |
| Trusted root signer compromise + coordinated upstream rewrite | 700 | 0 | 350 | 300 |
| Revoked old key | 0 | 700 | 0 | 0 |
| Rotated new key | 700 | 0 | 50 | 0 |
| Cross-tenant replay | 0 | 700 | 0 | 0 |
| First nonce use | 700 | 0 | 50 | 0 |
| Second nonce use (replay) | 0 | 700 | 0 | 0 |

In the combined compromise scenario, the attacker is assumed to possess the trusted document-root private key and coordinate changes to raw documents, normalized document slots, machine extraction, HS classification, and externally measured weight. The forged attestations then verify for all 700 cases. The existing gate authorizes 350 ACT decisions; 300 are unsafe relative to the original benchmark ground truth. This is **42.86% of all HIGH-risk cases** and **85.71% of the ACT decisions** in this specific synthetic scenario.

The 300 unsafe ACTs occur in six families: C1 extraction error, C2 cross-document conflict, C4 consistent but wrong, C6 verifier false accept, C9 cascading error, and C13 corrupted provenance (50 each). The other 50 ACT decisions occur in the clean family and are safe. Missing evidence, stale evidence, duplicate document kinds, and the other tested families remain blocked under this particular coordinated rewrite.

These figures are conditional outcomes under an intentionally strong combined-compromise assumption. They are not estimates of real-world attack probability and do not show that document-root key theft alone causes the same result. The experiment demonstrates that a signature authenticates a payload relative to a key; it does not establish semantic truth when the signing authority and corroborating upstream channels are jointly compromised.

The architectural implication is to separate independent capture attestation from extraction/normalization, external measurement, and action authorization. The capture authority should attest to source identity, acquisition channel, receipt time, and immutable raw-object digest—not certify that extracted values are true. High-consequence fields require corroboration from independently acquired sources and independently administered trust domains. Production use would additionally require KMS/HSM-backed key custody, authenticated signer enrollment, durable atomic replay state, operational revocation, audit logging, and incident response; none is implemented here. A subsequent synthetic prototype implements four role-separated attestations: capture, interpretation, independent witness, and authorization, with a separate key-administration trust-store threat control. Its deterministic compromise matrix is documented in [the v2 protocol](../experiments/evidence_trust_v2/PROTOCOL.md) and [results review](../experiments/evidence_trust_v2/RESULTS_REVIEW.md). It does not implement production key management or authenticate real source independence.

Protocol and complete family-level results: [experiments/document_root_attestation/PROTOCOL.md](../experiments/document_root_attestation/PROTOCOL.md) and [experiments/document_root_attestation/RESULTS_REVIEW.md](../experiments/document_root_attestation/RESULTS_REVIEW.md). The manuscript remains a synthetic research artifact and is not ready for arXiv submission.


## 22. Supplementary Experiment: Four-Authority Evidence-Trust Architecture (Benchmark v0.4)

This subsequent experiment is separate from the historical v0.3 benchmark tables and original Experiments 1A–2E. It evaluates all 700 HIGH-risk v0.4 cases under 15 non-empty compromise combinations of four roles—capture authority (CA), interpretation authority (IA), independent witness authority (IWA), and authorization authority (AA)—plus an honest baseline and three separate controls. The full matrix contains 19 scenarios and 13,300 case-scenario rows.

The prototype uses role-scoped Ed25519 attestations with tenant/case binding, parent digests, validity windows and replay-verification primitives. The authorization harness checks raw-document digest binding, interpretation lineage, declared source/acquisition/administrative-domain separation, witness agreement and the existing `evidence_gate_v1` policy. The independent witness is an idealized synthetic record derived from benchmark ground truth. The experiment is deterministic and does not estimate Monte Carlo uncertainty.

| Scenario | ACT | Unsafe ACT | Unsafe / all cases | Unsafe / ACT |
|---|---:|---:|---:|---:|
| Honest baseline | 50 | 0 | 0% | — |
| Capture only compromised | 0 | 0 | 0% | — |
| Interpretation only compromised | 0 | 0 | 0% | — |
| Witness only compromised | 100 | 50 | 7.14% | 50.00% |
| Capture + interpretation | 0 | 0 | 0% | — |
| Capture + witness | 350 | 300 | 42.86% | 85.71% |
| Interpretation + witness | 0 | 0 | 0% | — |
| Capture + interpretation + witness | 350 | 300 | 42.86% | 85.71% |
| Any combination including AA | 700 | 600 | 85.71% | 85.71% |
| Key-admin trust-store poisoning | 350 | 300 | 42.86% | 85.71% |
| Source forgery before capture | 0 | 0 | 0% | — |
| Disclosed shared-dependency witness | 0 | 0 | 0% | — |

The witness-only compromise result is concentrated in C4 (consistent but wrong): 50/50 cases produce unsafe ACT. The capture+witness, capture+interpretation+witness, and key-admin trust-store poisoning scenarios each produce 300 unsafe ACTs across C1, C2, C4, C6, C9 and C13 (50 per family), plus 50 safe ACTs in C0. Any scenario containing AA produces 700 ACT decisions, of which 600 are unsafe. This is an explicit modeled consequence of compromising the component that enforces final authorization.

The source-forgery-before-capture control is blocked because the independent synthetic witness retains the ground-truth value. The disclosed shared-dependency control is blocked because the witness declares the same source identifier and acquisition/administrative domains as capture. This does not prove real-world independence: the prototype checks declared labels but does not authenticate domain ownership. A compromised IWA can falsify signed witness claims and assert an apparently independent source. The key-admin control models trust-store poisoning that enrolls attacker-controlled CA, IA and IWA keys while AA remains honest; it produces the same 300 unsafe ACT outcome as the coordinated upstream-role compromise.

These results identify both the value and limits of role separation. Capture-only and interpretation-only compromise produced no unsafe ACT but blocked all ground-truth-safe cases in this benchmark. A single witness compromise produced unsafe ACT; coordinated upstream compromise recreated the v1 failure scale; AA compromise bypassed the gate entirely. The architecture therefore remains conditional on independent witness integrity, protected signer enrollment, and an authorization boundary that cannot be controlled by the attacker.

The complete protocol, threat assumptions and limitations are in [experiments/evidence_trust_v2/PROTOCOL.md](../experiments/evidence_trust_v2/PROTOCOL.md). The full family-level review is in [experiments/evidence_trust_v2/RESULTS_REVIEW.md](../experiments/evidence_trust_v2/RESULTS_REVIEW.md), and pinned output hashes are in [results/evidence_trust_v2/manifest-44025577491.json](../results/evidence_trust_v2/manifest-44025577491.json). CI run [44025577491](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44025577491) passed the full test suite, benchmark generation/verification, all experiment runners, artifact uploads, historical table loading and manuscript compilation. This is synthetic threat evidence only; production KMS/HSM custody, authenticated signer enrollment, durable replay storage, secure capture, and operational revocation are not implemented. The manuscript remains not ready for arXiv submission.

## 23. Supplementary Experiment: Authenticated Witness Quorum and Bounded Recovery (v3)

The v3 experiment evaluates 700 HIGH-risk v0.4 cases across eight threat scenarios (5,600 case-scenario rows). It introduces registry-signed witness identity credentials and case-scoped assertions, then evaluates the same assertions under 2-of-3 and strict 3-of-3 thresholds. It is an implementation and sensitivity study, not a new quorum theory. EFD and VP-CONTROL already directly study correlated evidence dependencies and quorum/verification-portfolio failure modes `[He and Yu, 2026; Zheng et al., 2026]`.

The v3 policy also permits a narrow recovery from an isolated verifier false rejection only when the witness quorum is valid and all other v1 policy guards pass. This recovers the 50 safe C7 cases in the synthetic fixture.

| Scenario | 2-of-3 ACT | 2-of-3 unsafe ACT | 3-of-3 ACT | 3-of-3 unsafe ACT |
|---|---:|---:|---:|---:|
| Honest baseline | 100 | 0 | 100 | 0 |
| One witness compromised | 100 | 0 | 100 | 0 |
| Two witnesses compromised | 150 | 50 | 100 | 0 |
| All witnesses compromised | 150 | 50 | 150 | 50 |
| Forged source identity | 100 | 0 | 0 | 0 |
| Source forgery before capture | 0 | 0 | 0 | 0 |
| Shared administrative domain | 0 | 0 | 0 | 0 |
| Registry-root compromise | 150 | 50 | 0 | 0 |

The honest baseline recovers all 100 safe cases (50 C0 plus 50 C7) with zero unsafe ACT. Under two-witness collusion, 2-of-3 produces 50 unsafe ACTs in C4 consistent-but-wrong; strict 3-of-3 rejects those cases. When all three witnesses are compromised, both thresholds produce 50 unsafe ACTs. Strict 3-of-3 also loses availability under a single invalid credential and registry-root compromise, while the shared-administration control blocks all safe cases.

All keys, identities and measurements are synthetic. The witness is derived from benchmark ground truth, so it is an idealized oracle rather than a real independent sensor. Registry signatures authenticate an issuer's credential, not the real-world truth of source identity or measurement. Distinct domain labels do not prove operational independence. The protocol and output hashes are in [experiments/evidence_trust_v3/PROTOCOL.md](../experiments/evidence_trust_v3/PROTOCOL.md); the preliminary novelty audit is in [research/NOVELTY_AUDIT.md](../research/NOVELTY_AUDIT.md). The full CI run and artifact are [44159840913](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44159840913).

## 24. Updated Related-Work and Novelty Boundary

The broad ideas of independent quorums and common-source failure are directly addressed by EFD and VP-CONTROL. TradeSense-EQA already integrates trade declarations, physical sensing, evidence chains and abstention. Commit-time authorization, execution-boundary contracts, runtime proof of execution, IoT provenance, remote attestation, capture-time authenticity, reject-option prediction and assurance-case defeaters also have substantial prior art. The current work therefore does not claim a new quorum theory, generic trade anomaly detector, generic provenance framework, or general execution-gating architecture.

The defensible contribution remains an EXIM-inspired synthetic security evaluation of how document extraction, physical evidence, claim applicability, provenance, freshness, source dependence and action authorization interact under explicit compromise assumptions. A follow-on dependency-ancestry study is required before making stronger claims about witness independence. See [the expanded prior-art audit](PRIOR_ART_AUDIT_2026.md) and [the v3 related-work review](../experiments/evidence_trust_v3/RELATED_WORK_AND_NOVELTY.md).

## References

[1] Ryan Greenblatt, Buck Shlegeris, Kshitij Sachan, and Fabien Roger. *AI Control: Improving Safety Despite Intentional Subversion*. arXiv:2312.06942, 2023.

[2] Santiago Torres-Arias, Hammad Afzali, Trishank Karthik Kuppusamy, Reza Curtmola, and Justin Cappos. *in-toto: Providing farm-to-table guarantees for bits and bytes*. 28th USENIX Security Symposium, 2019.

[3] SLSA Project. *Supply-chain Levels for Software Artifacts (SLSA): Provenance*. https://slsa.dev/

[4] Zachary Kenton et al. *On scalable oversight with weak LLMs judging strong LLMs*. arXiv:2407.04622, 2024.

[5] Yuyang Jiang et al. *Collaborative Disagreement Resolution for Scalable Oversight*. arXiv:2607.01251, 2026.

[6] Rayne Holland, Liming Zhu, and Jason Xue. *When Honesty is Not Enough in AI Debate*. arXiv:2609.29189, 2026.

[7] Kilian Hendrickx, Lorenzo Perini, Dries Van der Plas, Wannes Meert, and Jesse J. Davis. *Machine learning with a reject option: a survey*. Machine Learning 113, 3073–3110, 2024. https://doi.org/10.1007/s10994-024-06534-3

[8] Joao Sedoc, Baotong Zhang, and Dean P. Foster. *Trust but Verify: Prover-Verifier Deliberation for Selective LLM Prediction*. arXiv:2605.25133, 2026.

[9] Jun He and Deying Yu. *The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums*. arXiv:2609.02925, 2026.

[10] Zihao Zheng, Baichuan Li, Junyi Yao, and Jiayu Long. *Engineering Reliable Commit Gates for Agentic AI: Cost-Aware Verification Portfolios under Common-Mode Data Failures*. arXiv:2609.10969, 2026.

[11] Meitong Chen et al. *Artificial Intelligence-Driven Sensing of Cross-Border Trade Risks Through Declaration-to-Physical-Fact Alignment and Evidence-Grounded Question Answering*. Sensors 26(16), 5272, 2026. https://doi.org/10.3390/s26165272

[12] Bo Wu, Lin Wang, Yong Zhang, and Jiang Deng. *From Intent to Execution Grant: An Execution-Boundary Conformance Profile for High-Risk AI Actions*. arXiv:2609.11596, 2026.

[13] Jason D. Rhodes and George Kang. *Proof of Execution: Runtime Verification for Governed AI Agent Actions*. arXiv:2607.05397, 2026.

[14] Igor Santos-Grueiro. *Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents*. arXiv:2607.10487, 2026.

[15] Edward Y. Chang and Longling Geng. *Mnemosyne: Agentic Transaction Processing for Validating and Repairing AI-generated Workflows*. arXiv:2607.00269, 2026.

[16] Bofeng Pan, Natalia Stakhanova, and Suprio Ray. *Data Provenance in Security and Privacy*. ACM Computing Surveys 55(14s), 2023. https://doi.org/10.1145/3593294

[17] Omair Faraj, David Megias, and Joaquin Garcia-Alfaro. *Security Approaches for Data Provenance in the Internet of Things: A Systematic Literature Review*. ACM Computing Surveys 57(10), 2025. https://doi.org/10.1145/3718735

[18] Amir Dirin, Ian Oliver, and Teemu H. Laine. *A Security Framework for Increasing Data and Device Integrity in Internet of Things Systems*. Sensors 23(17), 7532, 2023. https://doi.org/10.3390/s23177532

[19] Eduardo Brito, Fernando Castillo, Amnir Hadachi, Ulrich Norbisrath, and Jonathan Heiss. *Decentralized Proof-of-Location for Content Provenance: Towards Capture-Time Authenticity*. arXiv:2603.27883, 2026.

[20] Ron Triepels, Hennie Daniels, and Ad Feelders. *Data-driven fraud detection in international shipping*. Expert Systems with Applications 99, 193–202, 2018. https://doi.org/10.1016/j.eswa.2018.01.007

[21] Hao Chen et al. *The use of machine learning to identify the correctness of HS Code for the customs import declarations*. IEEE DSAA, 2021. https://doi.org/10.1109/DSAA53316.2021.9564203

[22] Clifford Kahn. *Tolerating Penetrations and Insider Attacks by Requiring Independent Corroboration*. New Security Paradigms Workshop, 1998. https://www.nspw.org/papers/1998/nspw1998-kahn.pdf

[23] Stefan Buijsman and Herman Veluwenkamp. *Spotting When Algorithms Are Wrong*. Minds and Machines 33, 541–562, 2023. https://doi.org/10.1007/s11023-022-09591-0

[24] UK National Protective Security Authority. *Claims, Arguments and Evidence (CAE) Concepts*. https://www.npsa.gov.uk/system/files/documents/npsa-concepts-and-their-applicationcae-concepts1.pdf

[25] IETF. *RFC 9943: An Architecture for Trustworthy and Transparent Digital Supply Chains (SCITT Architecture)*, March 2026. https://www.rfc-editor.org/rfc/rfc9943.html

[26] Christian Janbjer. *Deterministic Intent Verification (DIV) Protocol Specification*, draft-janbjer-div-01, work in progress, 19 October 2026. https://datatracker.ietf.org/doc/html/draft-janbjer-div-01

[27] Christian Janbjer. *Deterministic Evidence & Witness Protocol (DEWP) Specification*, draft-janbjer-dewp-01, work in progress, 19 October 2026. https://datatracker.ietf.org/doc/html/draft-janbjer-dewp-01

[28] Joel Hillier. *Attestation Reconciliation Protocol*, draft-hillier-scitt-arp-06, work in progress, 23 October 2026. https://datatracker.ietf.org/doc/html/draft-hillier-scitt-arp-06

## Citation

Ali, Syed Hafiz. "Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence." Preprint, 2026.
