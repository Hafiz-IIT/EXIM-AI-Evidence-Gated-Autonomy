# Related Work Map and Novelty Boundaries

This note records the closest research families and the narrower contribution space for Evidence-Gated Autonomy (EGA). It is a research map, not a completed bibliography.

## 1. Runtime authority and action-boundary control

**AIRGuard** [Qin26b] places a runtime authority guard between an agent and side-effecting tools. It normalizes tool calls, tracks authority scope, target trust, and expected effects, and chooses enforcement actions before execution. Its central security distinction is that *evidence is not authority*: attacker-influenced content may describe an action without possessing the authority to authorize that action.

**Relation to EGA:** strong architectural overlap at the pre-action boundary. AIRGuard is primarily concerned with authority confusion and prompt-injection-mediated side effects. EGA's narrower research question is whether authorization quality changes when the gate reasons explicitly about evidence completeness, consistency, freshness, external grounding, provenance, source dependence, verifier co-failure, action consequence, and reversibility.

## 2. Information-flow control for agents

**Securing AI Agents with Information-Flow Control / FIDES** [Cos25b] uses dynamic taint tracking, confidentiality/integrity labels, quarantined inspection, and policy checks before tool execution. Its evaluation focuses on preventing indirect prompt-injection-driven unsafe flows.

**Relation to EGA:** FIDES provides a stronger formal security foundation for trusted/untrusted information flow than EGA currently provides. EGA should not claim novelty for pre-tool mediation, trust labels, or flow policies. The gap is different: FIDES largely assumes correctness of trusted labels/wrappers and does not test how action authorization should respond when evidence is incomplete, stale, mutually consistent but wrong, or supported by partially correlated verifiers.

## 3. Runtime policy enforcement

**AgentSpec** [Wan25k] defines human-readable runtime safety rules with triggers, logical checks, and enforcement actions. It can stop trajectories, request user inspection, invoke model self-examination, or substitute predefined safe actions across code, embodied-agent, and driving tasks.

**Relation to EGA:** AgentSpec establishes that deterministic runtime policy interception is already mature prior art. EGA's contribution should therefore not be framed as inventing runtime guards. Its contribution space is the empirical treatment of *what evidence structure should satisfy an authorization rule* and how those rules fail under dependence, spoofing, distribution shift, and compromised trust roots.

## 4. Formally constrained tool use

**Towards Verifiably Safe Tool Use for LLM Agents** [Dos26] derives safety requirements from system hazards and translates them into information-flow and temporal constraints enforced before tool calls. It includes blocklist, mustlist, allowlist, and confirmation tiers and demonstrates the approach through formal modeling.

**Relation to EGA:** consequence-sensitive pre-action constraints and escalation are established ideas. EGA does not claim a superior formal proof system. Instead, it asks an empirical systems question: when the authorization decision itself relies on fallible machine-produced evidence, provenance, verifiers, and external observations, which combinations meaningfully reduce unsafe action and where does the chain break?

## 5. Correlated verification

**Partially Correlated Verifier Cascades in LLM Harnesses** [Han26c] provides a theoretical account of diminishing returns under verifier correlation. It predicts concave evidence accumulation, polynomial rather than exponential reliability improvement under latent heterogeneity, and blind-spot ceilings where additional gates cannot remove systematic shared failures.

**Relation to EGA:** this directly motivates EGA's distinction between verifier count and evidence independence. The benchmark's correlated-verifier family and dependency-group checks should be presented as an empirical stress test of a problem that theory predicts should matter, not as the first observation that verifier correlation exists.

## 6. Human-AI oversight and escalation

**Human-AI Complementarity: A Goal for Amplified Oversight** [Jai25] finds that selective routing between AI and humans can outperform either alone in a fact-verification setting, but that the form of AI assistance matters. Evidence-first assistance can improve human review, while showing the AI's judgment/reasoning/confidence can induce over-reliance when the AI is wrong.

**Relation to EGA:** escalation is not automatically a safety guarantee. This supports EGA's decision to keep imperfect escalation as an explicit failure path and motivates the preregistered human-review study. The eventual human study should test whether evidence packets preserve reviewer independence rather than merely presenting the model's conclusion more persuasively.

## 7. What EGA should *not* claim as novel

EGA should not claim novelty for:

- runtime interception of tool calls;
- least-privilege authorization;
- selective prediction, abstention, or deferral as general concepts;
- human escalation;
- information-flow control;
- digital signatures or cryptographic provenance;
- separation of duties as a security design principle;
- the observation that verifier correlation exists;
- safety cases or structured assurance arguments.

## 8. Narrow contribution space

The defensible research contribution is the **combined empirical object**:

> A multi-outcome action-authorization controller that treats evidence structure and trust as first-class inputs, then stress-tests that controller under controlled extraction errors, cross-document conflicts, missing/stale evidence, mutually-consistent-but-wrong evidence, verifier false acceptance/rejection, correlated verifier failure, cascading error, provenance spoofing, trust-root compromise, and imperfect escalation.

The central empirical questions are:

1. Does evidence-structure-aware gating reduce unsafe consequential action relative to simpler confidence/agreement/risk baselines?
2. Which evidence checks actually contribute independently, and which only add cost/coverage overhead?
3. How quickly does any advantage collapse as supporting verifiers/reviewers become imperfect?
4. Does cryptographically binding provenance repair metadata-spoofing failures, and where does it merely move the trust assumption?
5. Does separating verifier and lineage authority raise the compromise threshold under an explicit threat model?
6. Do these synthetic findings survive frozen real-model evaluation?

## 9. Submission standard

The final paper should cite the prior-art families above directly and state the novelty boundary in the Introduction and Related Work. Any new paper discovered that already evaluates the same combined gate under the same failure families should trigger a narrower contribution claim rather than being ignored.

### Working cite keys

- [Qin26b] AIRGuard: Guarding Agent Actions with Runtime Authority Control.
- [Cos25b] Securing AI Agents with Information-Flow Control.
- [Wan25k] AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents.
- [Han26c] Partially Correlated Verifier Cascades in LLM Harnesses.
- [Dos26] Towards Verifiably Safe Tool Use for LLM Agents.
- [Jai25] Human-AI Complementarity: A Goal for Amplified Oversight.
