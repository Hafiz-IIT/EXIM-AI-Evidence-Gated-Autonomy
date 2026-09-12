# Results and Discussion — Experiments 1A–2E

## Synthetic controller evaluation
The deterministic benchmark contains 500 unique underlying evidence states paired across low- and high-consequence actions. Evidence Gate produced no unsafe high-consequence ACT decisions in Experiment 1A, while Risk Gate and Always Verify each produced 50/500. This is treated only as a proof-of-concept because verification and escalation were idealized.

When verification, evidence retrieval, and escalation were made imperfect in Experiment 1B, performance degraded as expected. Evidence Gate's mean high-risk incorrect-action rate was approximately 1.9% in the optimistic regime, 6.1% in the moderate regime, and 13.1% in the harsh regime. Under the moderate regime, Risk Gate was approximately 16.5%.

Ablations showed measurable protection from external grounding, evidence-source independence, and freshness. Explicit verifier-status handling did not independently improve the deterministic incorrect-action rate after other checks were present. Risk conditioning primarily improved coverage and cost.

## Adversarial evidence and provenance tests
Experiment 1C exposed a major failure boundary: changing dependency metadata or masking external evidence could cause the original gate to accept unsafe actions. Combined metadata/evidence spoofing materially increased incorrect high-risk actions.

Experiment 2 introduced cryptographically signed provenance attestations. In deterministic unsigned-spoofing tests, the original gate reached 10% incorrect high-risk actions on individual dependency, external-evidence, and timestamp attacks and 30% under the combined attack. An attestation-aware gate prevented direct unsafe ACTs in these conditions by rejecting evidence whose signed claims no longer matched the current objects.

This did not remove review risk. With a simulated 90%-accurate escalation process, the attestation-aware system retained roughly 6–7% incorrect high-risk actions under several tamper conditions because detected cases could still be mishandled downstream.

## Trust-root compromise
Signed provenance changed the attack surface rather than eliminating it. If a trusted verifier, sensor, or authorization signer was compromised and could generate a valid signature over a false claim, the attestation-aware gate again produced a 10% failure family; compromise of all relevant trust roots produced 30%.

A separation-of-duties variant moved dependency-lineage authority away from the verifier and required agreement from two independent lineage authorities. This variant remained at 0% deterministic incorrect high-risk actions under verifier-only compromise, either lineage-authority compromise alone, or verifier plus one lineage-authority compromise. Compromise of both lineage authorities restored 10% incorrect high-risk actions. With imperfect escalation, single-authority compromise still produced approximately 7% error due to review failures, while compromise of both lineage authorities produced approximately 15%.

## Interpretation
The experiments support a narrower claim than "verification makes agents safe." Reliability depends on a chain of assumptions: evidence availability, correct dependency representation, authentic provenance claims, uncompromised trust roots, and reliable escalation.

The key transition is from **evidence quantity** to **evidence structure and trust**. Multiple agreeing model outputs do not necessarily provide multiple independent reasons for action. Self-asserted dependency metadata is a weak trust foundation. Cryptographic binding can prevent undetected modification, yet a valid signature authenticates a signer and the integrity of a claim—not the truth of the claim.

## Limitations
All current performance results remain synthetic or Monte Carlo simulations. No external frontier-model batch evaluation, real customs dataset, production system, real cryptographic infrastructure, or human-subject study has been completed. The current evidence establishes a reproducible proof-of-concept and identifies failure modes; it does not establish real-world safety.
