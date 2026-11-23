# Related-Work Audit: Evidence-Gated Autonomy and Action Authorization

**Prepared:** 2026-11-23  
**Purpose:** Prevent unsupported novelty claims and identify where the current repository's evidence sits relative to recent work. This is a targeted initial audit, not a systematic literature review.

## Executive finding

The repository must **not** claim novelty for signed action catalogs, deterministic pre-action authorization, or approval-to-execution binding as broad ideas. Recent 2026 work already addresses those areas directly:

- **Open Agent Passport (OAP)** presents synchronous pre-action authorization, declarative policy checks and signed audit records, with a reported live adversarial testbed and latency measurements.
- **Intent-Governed Tool Authorization (IGAC)** adds request-intent certificates, session-scoped policy narrowing, tool-manifest filtering and payload/intent consistency checks.
- **Approval Laundering** directly studies whether the action approved by a human is the action ultimately dispatched. It defines six laundering classes and evaluates a keyed approval-token prototype; importantly, it reports failure classes that a field-only verifier does not catch.
- **CERT-In AI Security Auditing Guidelines v1.0 (4 November 2026)** include agent identity, approved tools, least privilege, human approval for consequential actions, execution-chain logging and tool/service identity validation.

These sources substantially overlap with the general direction of the action-consequence and signed-catalog work in this repository. The current HMAC prototype is an educational, deterministic test harness, not a novel authorization architecture.

## Additional directly overlapping work identified in the focused literature search

The following papers materially broaden the overlap beyond OAP, IGAC and Approval Laundering:

- **Evidence-carrying multimodal agents (Zhang, Zheng and Yang, Findings of EMNLP 2026).** The ECA architecture treats model text as a proposal rather than authorization, derives action-critical predicates, obtains typed certificates from constrained DOM/OCR/accessibility verifiers, and gates execution on those certificates. The paper reports verifier red-teaming and end-to-end/browser evaluations, while explicitly conditioning its guarantee on verifier, schema and gate correctness. This is a close overlap with evidence-grounded action gating.
- **Deterministic Runtime Enforcement / L-DREA (Gill-Lakhowal, IEEE Access 2026).** L-DREA separates capability generation from execution authority using signed Permit-to-Act tokens, revocation/epoch controls and a commit-before-actuate interlock. Its reported scale is much larger than this repository's synthetic benchmark. The paper's own limitations include software-resident key custody and no claim of production deployment at a regulated institution or third-party audit.
- **Trust-Aware Orchestration (Leburu, IEEE Access 2026).** This work composes tenant resolution, role-based tool authorization and schema validation as hard gates, with advisory filters and audit logging. It reports 14,885 evaluations across five models and a particularly relevant negative result: within-scope intent manipulation using an authorized role, authorized tool and schema-valid parameters succeeded at 30–70% in its adaptive case study. Structural gates therefore do not establish that an authorized action is justified by the user's intent.
- **Cryptographically Verifiable Authorization (Llambí-Morillas and Fernández-Fernández, Frontiers in Computer Science 2026).** This paper formalizes a request-bound authorization relation over principal, request, context and policy using a zero-knowledge proof-of-concept. It explicitly separates authorization-request binding from runtime execution binding and leaves the latter as an open problem; gateway compromise is outside its core threat model. This directly overlaps with the conceptual aim of the local HMAC prototype, but is substantially more formal.
- **Auditable LLM Autonomy (Theodorakopoulos and Theodoropoulou, Computers, Materials & Continua 2026).** This review presents an assurance-stack taxonomy separating evidence grounding, verification, action gating and auditability, and proposes an evaluation ladder beyond text metrics. It is a direct conceptual overlap with the repository's layer decomposition, though it is a review rather than the same synthetic experiment.
- **Securing Tool-Using AI Agents Against Injection and Authority Misuse (Kanaker et al., Computation 2026).** This simulator-based study examines injection and authority misuse, reports limitations of repeated human confirmation, and distinguishes execution receipts/read-after-write verification from pre-action gating. Its results are design guidance under simulator assumptions, not deployment incident estimates.

These works make it untenable to frame EGA as a new action-gating, signed-permit, evidence-certificate, or request-bound authorization architecture. The repository's strongest plausible direction is a controlled empirical study of how errors and compromised evidence propagate *between* assurance layers, while preserving explicit uncertainty about whether that composition gap is truly novel.

## Comparison against this repository

| Work | Main unit / mechanism | Evidence reported by source | Implication for this repository |
|---|---|---|---|
| [Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents (OAP), arXiv:2603.20953](https://arxiv.org/abs/2603.20953) | Per-tool-call pre-action authorization, declarative policy, signed audit record | Paper reports 1,000 latency measurements and a live adversarial testbed | Do not claim to introduce deterministic pre-action authorization. Compare threat models and enforcement points. |
| [Intent-Governed Tool Authorization for AI Agents, arXiv:2606.22916](https://arxiv.org/abs/2606.22916) | User-intent certificates, monotone session policy narrowing, manifest filtering, payload consistency | Proposes and maps an intent-governance layer onto an existing tool-governance substrate | Distinguish evidence sufficiency / source reliability from request-intent authorization; test composition rather than presenting either as a replacement. |
| [Approval Laundering: Systematizing Approval–Execution Binding Failures in AI Coding-Agent Harnesses, arXiv:2609.38983](https://arxiv.org/abs/2609.38983) | Approval-to-dispatch identity across scope, argument, time, tool, delegation and semantic surfaces | Reports repeated-measures harness experiments and an approval-token prototype; documents residual failures below the observable field boundary | Directly overlaps with action-ID and executor-binding claims. Our synthetic check is narrower; it does not cover side effects, hidden hooks, semantic rendering, or process-level divergence. |
| [CERT-In AI Security Auditing Guidelines v1.0](https://www.cert-in.org.in/Downloader?fileName=CIGU-2026-0004.pdf&pageid=6&type=2) | Governance and audit requirements for agentic systems | Official Indian AI security auditing guidance dated 4 November 2026 | Map repository controls to audit requirements, but do not treat guidance alignment as empirical validation. |

## What the current repository actually contributes

The defensible contribution is narrower and should remain empirical:

1. A versioned synthetic benchmark focused on evidence-gated decisions in high-consequence document workflows.
2. Explicit negative results showing that an evidence gate can underperform a simpler risk gate under the repository's particular retrieval/human-error assumptions.
3. Failure-mode experiments for provenance compromise, verifier dependence and action metadata manipulation, with claim boundaries and reproducible CI artifacts.
4. A modular testbed in which evidence sufficiency, evidence lineage, consequence classification, authorization context and execution binding can be varied independently.

Even these points are **not yet evidence of novelty**. The benchmark's scenario realism, parameter calibration, construct validity and relationship to existing benchmarks still require external review.

## Research gap to test, not assume

A plausible direction is to evaluate the **composition failure surface** across:
- evidence correctness and source dependence;
- retrieval failure and correlated verifier/human error;
- signer/catalog trust and version drift;
- authorization-to-execution binding;
- human escalation capacity, latency and operational cost.

The testable question is whether a system that passes each component's local check can still fail when the components share a compromised source, stale state, ambiguous identity, or non-atomic handoff. That question must be narrowed against the related work above before being framed as a contribution.

## Required next work

- Obtain the full text and implementation details for OAP, IGAC and Approval Laundering; compare threat models, assumptions, test harnesses and artifacts line by line.
- Add a benchmark-to-literature matrix for AgentDojo, InjecAgent, MCP tool-poisoning benchmarks and the approval/execution-binding studies.
- Define operational outcomes beyond policy return values: exact invoked tool, canonical arguments, target resource, side effects, state version, replay and revocation.
- Add correlated failure and intervention-capacity experiments, with parameter ranges justified by empirical sources or explicitly labelled as sensitivity analysis.
- Seek independent annotation and replication before any novelty or deployment-safety claim.

## Claim restriction

Do not write that this repository is the first, novel, state-of-the-art, production-secure, or empirically validated system for action authorization or approval-execution binding. Do not cite the local HMAC experiment as evidence that a real external tool call is secured.
