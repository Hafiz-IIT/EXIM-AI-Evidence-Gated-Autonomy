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


## Supplementary four-authority Evidence-Trust v2 experiment (benchmark v0.4)

This subsequent synthetic experiment is separate from the historical v0.3 benchmark and Experiments 1A--2E. It evaluates 700 HIGH-risk v0.4 cases under all 15 non-empty compromise combinations of capture, interpretation, independent witness and authorization authorities, plus an honest baseline and three controls (19 scenarios; 13,300 case-scenario rows).

The honest baseline produced 50 ACT decisions, all safe, with 50% safe-ACT coverage and a 50% false-block rate. The latter reflects the benchmark's safe-but-false-reject cases. Single capture or interpretation compromise produced no unsafe ACT but blocked all safe cases. Single witness-authority compromise produced 50 unsafe ACT decisions (7.14% of all HIGH-risk cases; 50% of ACT decisions), all in C4 consistent-but-wrong. Capture+witness, capture+interpretation+witness, and key-admin trust-store poisoning each produced 300 unsafe ACT decisions (42.86% of all HIGH-risk cases; 85.71% of ACT decisions), in C1, C2, C4, C6, C9 and C13 (50 per family). Any compromise combination containing AA produced 700 ACT decisions, 600 unsafe (85.71% of all HIGH-risk cases).

The source-forgery-before-capture control and disclosed shared-dependency-witness control produced no ACT decisions. The latter is rejected because the witness discloses the same source identifier and acquisition/administrative-domain labels as capture. These checks do not authenticate the labels: a compromised witness can sign false values and claim a separate source identity. The independent witness itself is simulated from benchmark ground truth; no real external source was used.

The result therefore does not show that role separation eliminates trust-root risk. It shows that some isolated compromises are contained at the cost of coverage, while compromise of the witness authority, trust registry or final authorization boundary can still produce unsafe action. The complete scenario table, family-level breakdown, threat assumptions, output hashes and limitations are in [the v2 results review](../experiments/evidence_trust_v2/RESULTS_REVIEW.md). The successful CI execution is [run 44025577491](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44025577491).


## Supplementary dependency-aware witness ancestry experiment (v5)

The v5 experiment compares four policies on the same 16 scenarios and 700 HIGH-risk cases per scenario: K2 key-unique 2-of-3, F2 direct-field-distinct 2-of-3, F3 direct-field-distinct 3-of-3, and G2 graph-aware 2-of-3. The four-policy experiment contains 44,800 case-policy-scenario rows.

| Policy | Unsafe ACT across 11,200 cases | Safe-ACT coverage | Graph-validation rejections |
|---|---:|---:|---:|
| K2 key-unique | 700 | 100% | 0 |
| F2 field-distinct | 650 | 100% | 0 |
| F3 field-distinct | 50 | 93.75% | 0 |
| G2 graph-aware | 150 | 87.5% | 1,800 |

G2 blocks the modeled C4 false quorum in seven declared hidden-shared-dependency scenarios where K2 and F2 each authorize 50 unsafe actions despite distinct direct labels. It rejects incomplete ancestry when the incomplete witness is needed. The trade-off is availability: malformed or unresolved graph structure and invalid graph signatures fail closed across all 700 cases in each affected scenario, including safe cases. F3 blocks two-witness collusion but still permits 50 unsafe actions under full-roster compromise. G2 is also fooled by registry-root compromise when the compromised registry signs a graph that omits a true common parent.

This is an EXIM-inspired empirical comparison, not a new quorum theory, structural-cut metric, or dependency-aware quorum algorithm. EFD/DAQC and ARP already cover the general concepts; the defensible result is the benchmark-specific comparison and its security/availability trade-offs. All graph data and attacks are synthetic; a signed graph authenticates registry assertions, not real-world completeness or truth. See the v5 protocol, results review, and pinned manifest.
