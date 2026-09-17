# Related-Work Audit and Novelty Boundary

## Purpose

This note records the current literature boundary for Evidence-Gated Autonomy before formal manuscript citation work. It is intentionally conservative: the goal is to prevent novelty inflation.

## What is already established

The broader literature already contains most of the architectural ingredients that an action-authorization framework might use:

- runtime assurance / safety-filter style intervention;
- deterministic action mediation;
- scoped or task-specific authorization;
- selective prediction, abstention, verification, and escalation;
- provenance and execution attestation;
- information-flow control for AI agents;
- tool-use safety and policy enforcement;
- multi-agent voting / verifier cascades;
- human escalation and supervisory review.

Therefore the project should **not** claim:

- to be the first framework separating capability from authorization;
- to invent abstention or selective verification;
- to invent provenance-aware agent control;
- to invent scoped tool authorization;
- to invent quorum-based or multi-verifier oversight;
- to prove general safety from synthetic authorization results.

## Strong recurring boundary from the literature

### Capability is not authorization

A model seeing a tool, holding credentials, or successfully calling an endpoint does not establish that the action is permitted in the present context.

### Provenance is not truth

Signed or attested records can authenticate source, execution environment, or integrity while still preserving a false statement. Trust-root freshness, signer compromise, and evidence coverage remain assumptions.

### Multiple verifiers are not automatically multiple independent reasons

Shared model families, training data, prompts, telemetry, tools, retrieval systems, or trust roots can create correlated failure. Quorum size alone is not a reliability guarantee.

### Escalation is not automatically meaningful oversight

A controller that routes difficult cases to humans inherits the quality, timing, information access, incentives, and workload limits of the review process.

## Defensible contribution claim

The strongest novelty statement currently supported is narrower:

> **A typed, risk-sensitive action-admission policy that explicitly maps evidence completeness, consistency, freshness, provenance, source dependence, external grounding, verifier behavior, action consequence, and reversibility to ACT, VERIFY, REQUEST EVIDENCE, DEFER, or ESCALATE, and evaluates how those assumptions fail under controlled correlated-verifier, provenance-spoofing, trust-root-compromise, and imperfect-escalation conditions.**

The contribution is therefore not any single mechanism. It is the **interaction structure** among evidence sufficiency, dependence, provenance, trust, consequence, and escalation in an inspectable controller plus a benchmark designed to falsify its assumptions.

## Appropriate paper-level claims

Reasonable language:

- "We operationalize action authorization as a typed evidence-admission problem."
- "We construct a synthetic benchmark that isolates correlated evidence, stale evidence, mutually consistent but wrong evidence, provenance spoofing, and cascading error."
- "We show that the tested controller's advantage depends on explicit assumptions about grounding, independence, provenance, trust roots, and escalation reliability."
- "We identify failure boundaries rather than claiming general autonomous-agent safety."
- "A real-model follow-up tests whether observed model outputs reproduce the benchmark's dependence and co-failure concerns."

Avoid:

- "first safe agent authorization framework";
- "guaranteed trustworthy autonomy";
- "cryptographic proof of truth";
- "independent verification" when only model-family diversity is known;
- "human oversight is effective" before the participant study exists.

## Literature families to cite in the manuscript

The completed literature audit surfaced especially relevant work in the following families:

1. **Agent information-flow / policy enforcement** — work on securing agent actions and constraining tool-mediated effects.
2. **Commit-time / task-scoped authorization** — work that distinguishes temporary authority from persistent execution effects and narrows action permissions.
3. **Action induction vs runtime authorization** — work separating what an LLM suggests from what the runtime should permit.
4. **Verifier co-failure and epistemic fault domains** — work showing that apparently multiple agents or verifiers can share blind spots and dependence.
5. **Provenance-aligned authorization** — work binding tool arguments, context, or execution evidence to authorization decisions.
6. **Verifiably safe tool use** — work applying policy, contracts, or formal methods to agent tool execution.
7. **Memory/action authority** — adjacent work showing how persistent state can launder old or untrusted information into apparent current permission.

## Literature-search record

The literature audit was run on 2026-09-17 in the connected Undermind research workspace under:

`/agent-governance/Evidence gated autonomy related work and novelty boundary`

The search returned a large body of relevant 2025–2026 work and concluded that a broad novelty claim would be indefensible. The manuscript should use the narrower mechanism-level contribution above.

## Manuscript action

Before submission:

- convert the highest-relevance papers into formal references;
- verify exact claims against full text where novelty depends on them;
- cite mature antecedents for abstention, runtime assurance, policy enforcement, provenance, and human oversight;
- reserve novelty only for the specific interaction/evaluation contribution actually demonstrated by this repository.
