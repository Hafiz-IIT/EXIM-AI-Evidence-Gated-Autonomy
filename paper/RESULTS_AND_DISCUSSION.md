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


<!-- Current-head reproducibility trigger: manuscript workflow also validates documentation-triggered revisions. -->


## Reproducibility qualification

The historical 1B–2E result CSVs do not have their original experiment runners or complete parameter configurations in the repository history. The new `reconstruction_v1` outputs are generated from an explicit new protocol and are not historical reproductions. Experiment 1A's original downstream-resolution implementation is also missing. The historical numerical claims therefore remain pending source-level reconciliation.


## Supplementary document-root attestation experiment (benchmark v0.4)

This is a subsequent synthetic extension and is not merged into the historical v0.3 benchmark or original Experiment 2 tables. On 700 HIGH-risk v0.4 cases, the document-root verifier rejected raw document-instance tampering, coherent rewrites without the trusted private key, revoked-key use, cross-tenant reuse, and second-use nonce replay in all 700 cases per scenario. Valid baseline and rotated-key attestations were accepted in all 700 cases per scenario.

The combined compromise scenario assumes both possession of the trusted document-root private key and coordinated modification of raw document instances, normalized document slots, machine extraction, HS classification, and external measured weight. All 700 forged attestations verified. The downstream gate authorized ACT in 350 cases, of which 300 were unsafe against benchmark ground truth: 42.86% of all HIGH-risk cases and 85.71% of ACT decisions in this synthetic scenario. The 300 unsafe ACTs occurred in C1, C2, C4, C6, C9 and C13 (50 per family); the other 50 ACTs were safe cases in C0.

This is a conditional result under an intentionally strong combined-compromise assumption, not an estimate of real-world probability and not evidence that signer-key theft alone causes the same outcome. It shows that signatures bind payloads to keys but do not establish semantic truth when signing authority and corroborating channels are jointly compromised. The design implication is to separate capture attestation from extraction/normalization, external sensing and action authorization, and to require corroboration from independently acquired sources. See [the protocol](../experiments/document_root_attestation/PROTOCOL.md) and [the complete results review](../experiments/document_root_attestation/RESULTS_REVIEW.md).
