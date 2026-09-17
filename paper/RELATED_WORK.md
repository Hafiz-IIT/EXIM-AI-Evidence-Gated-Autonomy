# Related Work and Novelty Boundary

This section is written as a reviewer-facing comparison rather than a list of adjacent keywords. The purpose is to make explicit which mechanisms are prior art and what narrower contribution Evidence-Gated Autonomy (EGA) is actually testing.

## 1. Information-flow control and deterministic policy enforcement

Costa et al. (2025), *Securing AI Agents with Information-Flow Control*, present Fides, a planner that propagates confidentiality/integrity labels and deterministically enforces policies over consequential actions. Fides is important prior art for the idea that an agent should not be trusted to police its own reasoning and that a separate runtime layer can constrain action based on provenance/integrity labels.

**What EGA must not claim:** EGA does not invent runtime interposition, trusted/untrusted provenance labels, or the idea that consequential actions can be denied when influenced by untrusted data.

**Distinction:** Fides principally asks whether information is permitted to flow into a consequential sink under an information-flow policy. Its trusted configuration is part of the threat model. It does not primarily evaluate whether available evidence is complete, internally consistent, fresh, externally grounded, mutually dependent, or sufficient for a particular reversible/irreversible action. Its enforcement path is effectively allow/abort, whereas EGA studies a five-way action-admission policy: ACT, VERIFY, REQUEST EVIDENCE, DEFER, or ESCALATE.

Reference: Manuel Costa et al., *Securing AI Agents with Information-Flow Control*, arXiv:2505.23643, 2025. DOI: 10.48550/arXiv.2505.23643.

## 2. Formal runtime policy enforcement

Palumbo et al. (2026), *Formal Policy Enforcement for Real-World Agentic Systems*, present FORGE, a reference-monitor architecture that evaluates Datalog policies over execution context and causal history. FORGE makes a strong case that policy enforcement should be external to agent reasoning and can be deterministic when the observability contract holds.

**What EGA must not claim:** EGA does not invent formal runtime admission, reference monitors, causal-history-aware policy enforcement, or decoupling enforcement from the agent.

**Distinction:** FORGE's primary policy object is compliance with declared organizational/security constraints: approvals, identities, data-flow restrictions, and domain rules. EGA's primary policy object is *evidence sufficiency under uncertainty*: whether evidence is complete, consistent, fresh, independently sourced, grounded, and trustworthy enough to justify a particular action. FORGE is primarily binary Allow/Deny; EGA explicitly studies intermediate outcomes and the reliability of the review/escalation stages themselves.

Reference: Nils Palumbo et al., *Formal Policy Enforcement for Real-World Agentic Systems*, arXiv:2602.16708, 2026.

## 3. Commit-time authorization and stale authority

Santos-Grueiro (2026), *Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents*, shows that authority that was valid earlier in an agent trajectory may no longer authorize a durable effect at commit time. CommitGuard checks freshness, causal priority, effect binding, and commit eligibility at the durability boundary.

**What EGA must not claim:** EGA does not invent the idea that authorization can become stale, that endpoint/task success is distinct from authorized execution, or that durable effects require a final authorization boundary.

**Distinction:** Commit-time authorization is centered on whether the original authority witness still authorizes the concrete durable effect. EGA treats freshness as one member of a broader evidence-admission vector and additionally stress-tests cross-document inconsistency, mutually consistent-but-wrong evidence, verifier co-failure, external grounding, provenance spoofing, trust-root compromise, and imperfect escalation. EGA also makes consequence/reversibility explicit in the action object rather than treating every durable effect through the same evidence policy.

Reference: Igor Santos-Grueiro, *Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents*, arXiv:2607.10487, 2026. DOI: 10.48550/arXiv.2607.10487.

## 4. Argument-level provenance and capability contracts

Fan et al. (2026), *The Granularity Mismatch in Agent Security: Argument-Level Provenance Solves Enforcement and Isolates the LLM Reasoning Bottleneck*, present PACT. PACT assigns semantic roles to tool arguments, tracks provenance across replanning, and checks role-specific trust contracts before execution.

**What EGA must not claim:** EGA does not invent provenance-aware runtime authorization, role-specific trust constraints, or the idea that untrusted data should not bind authority-bearing arguments.

**Distinction:** PACT is a structural authority-binding defense: it asks *who/what source is allowed to determine an argument*. It does not generally decide whether a set of permitted-origin claims is logically consistent, current, externally true, independently corroborated, or sufficient for a high-consequence action. Its trusted computing base is assumed rather than attacked. EGA's provenance experiments specifically explore the difference between authentic provenance and semantic truth, including signed false claims under compromised trust roots.

Reference: Linfeng Fan et al., *The Granularity Mismatch in Agent Security: Argument-Level Provenance Solves Enforcement and Isolates the LLM Reasoning Bottleneck*, arXiv:2605.11039, 2026. DOI: 10.48550/arXiv.2605.11039.

## 5. Action induction versus execution authorization

Guo et al. (2026), *When Tool Outputs Become Commands: Separating Action Induction from Runtime Authorization in Tool-Augmented LLM Agents*, present SARA. SARA distinguishes information that induces an action from information that normatively authorizes execution, preserves action-origin provenance, and prevents historical recurrence from laundering origin into authority.

**What EGA must not claim:** EGA cannot claim priority for separating model/tool suggestion from runtime authorization, or for the broader observation that a successful tool call does not by itself imply user-authorized execution.

**Distinction:** SARA's central threat is observation-driven action induction and provenance laundering across tool trajectories. Its authorization tests goal support, execution-chain support, and argument support. EGA's central object is a typed evidence state, including evidence completeness, cross-source consistency, freshness, external grounding, verifier dependence, provenance integrity, consequence, and reversibility. The EGA benchmark is therefore better described as an *evidence-sufficiency stress test* rather than an action-origin security framework.

Reference: Xiao-Kun Guo et al., *When Tool Outputs Become Commands: Separating Action Induction from Runtime Authorization in Tool-Augmented LLM Agents*, arXiv:2608.27146, 2026.

## 6. Correlated verifiers and epistemic fault domains

He and Yu (2026), *The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums*, formalize shared causal ancestry using Epistemic Fault Domains and a Structural Epistemic Cut. Their work makes explicit that adding nominally different reviewers does not create epistemic redundancy when they share upstream roots.

Han (2026), *Partially Correlated Verifier Cascades in LLM Harnesses*, develops a mathematical theory of correlated serial verification. It shows that independence-based exponential reliability improvement can collapse to polynomial improvement or a hard blind-spot ceiling under correlation.

Chen (2026), *When Does Combining Language Models Help?*, empirically studies 67 models and shows that routing/voting/mixture gains are bounded by an all-models-wrong co-failure rate that pairwise correlations cannot identify.

**What EGA must not claim:** EGA does not invent verifier dependence, correlated verification failure, co-failure ceilings, or the observation that different model families are not proof of independence.

**Distinction:** EGA uses dependence as one component in a broader action-authorization benchmark. Its distinct empirical question is not the mathematics of correlation alone, but how dependence interacts with stale/missing/conflicting evidence, external grounding, provenance spoofing, compromised trust roots, action consequence/reversibility, and imperfect escalation. Model-family identity in Experiment 3 is therefore retained only as a transparent diversity label, never as a proof of epistemic independence.

References:
- Jun He and De-Ying Yu, *The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums*, arXiv:2609.02925, 2026.
- Jian-guo Han, *Partially Correlated Verifier Cascades in LLM Harnesses: Concave Log-Odds, Polynomial Reliability, and Blind-Spot Ceilings*, arXiv:2607.13918, 2026. DOI: 10.48550/arXiv.2607.13918.
- J. Chen, *When Does Combining Language Models Help? A Co-Failure Ceiling on Routing, Voting, and Mixture-of-Agents Across 67 Frontier Models*, arXiv:2606.27288, 2026. DOI: 10.48550/arXiv.2606.27288.

## 7. The narrow contribution left for EGA

After accounting for these prior systems, the defensible contribution is not a claim that EGA invented runtime authorization, provenance, abstention, freshness checks, or correlated-verifier reasoning.

The contribution is the following *interaction-level research object*:

> **A typed, risk-sensitive action-admission policy that maps evidence completeness, consistency, freshness, provenance, source dependence, external grounding, verifier behavior, action consequence, and reversibility to ACT, VERIFY, REQUEST EVIDENCE, DEFER, or ESCALATE, together with a benchmark designed to falsify the assumptions behind that policy under controlled extraction error, mutually consistent-but-wrong evidence, correlated verification, provenance spoofing, trust-root compromise, distribution shift, and imperfect escalation.**

The synthetic experiments currently support only this bounded claim. Experiment 3 is intended to test whether the same failure structure appears when machine outputs are supplied by real model families rather than a synthetic error generator.

## 8. Reviewer-facing novelty test

A novelty claim should survive the following questions:

1. **Would the contribution disappear if Fides/PACT/FORGE were cited?** If yes, the claim is too broad.
2. **Would the contribution disappear if correlated-verifier theory were cited?** If yes, the claim is too broad.
3. **Does the claimed contribution require the interaction of at least several evidence dimensions rather than a single prior-art mechanism?** If no, narrow it.
4. **Is the claim supported by a completed experiment in this repository?** If no, label it hypothesis/future work.
5. **Would the claim remain true if Experiment 3 performs poorly?** The benchmark/failure-analysis contribution may remain; a real-model performance claim would not.

This is the standard the final manuscript should use.