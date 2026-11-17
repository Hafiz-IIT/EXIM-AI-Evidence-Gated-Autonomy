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

## 6. Evidence-Trust v3: Authenticated Witness Quorum and Bounded Recovery

The v3 experiment runs 700 HIGH-risk benchmark v0.4 cases under eight threat scenarios, producing 5,600 case-scenario rows. It compares a 2-of-3 witness threshold with a strict 3-of-3 sensitivity condition. The v3 runner uses registry-signed witness identity credentials, case-scoped signed assertions, and a controller path that consumes only the verified quorum measurement. Invalid quorum results force escalation rather than falling back to the original unverified measurement.

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

The v3 policy adds a bounded recovery path for isolated verifier false rejection. It recovers 50 safe C7 cases only when the quorum is valid and every other existing policy guard passes. The honest baseline therefore reaches 100/100 safe-action coverage with zero unsafe ACT. Under two-witness collusion, 2-of-3 produces 50 unsafe ACT decisions in the C4 consistent-but-wrong family; strict 3-of-3 blocks those cases. When all three witnesses are compromised, both thresholds produce 50 unsafe ACT decisions.

The 3-of-3 policy has an availability cost: it blocks all safe cases when one credential is invalid and under registry-root compromise. The shared-administration control also fails closed and blocks all safe cases. These results are not free security improvements.

All keys, identities, measurements and witness assertions are synthetic. The witness derives its value from benchmark ground truth, so it is an idealized oracle rather than an independent physical sensor. Registry signatures authenticate a credential issuer, not the real-world truth of source identity or measurements. Administrative-domain labels do not prove actual operational independence. No production PKI, KMS/HSM custody, hardware identity, trusted time, durable revocation or secure acquisition is implemented. The results are deterministic benchmark outcomes, not real-world probabilities.

The full protocol and hashes are in [experiments/evidence_trust_v3/PROTOCOL.md](../experiments/evidence_trust_v3/PROTOCOL.md), and the validated run is [44159840913](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44159840913). The v3 mechanism is treated as an implementation and sensitivity experiment, not as a novel quorum theory; EFD and VP-CONTROL directly address correlated dependencies and verification portfolios.
