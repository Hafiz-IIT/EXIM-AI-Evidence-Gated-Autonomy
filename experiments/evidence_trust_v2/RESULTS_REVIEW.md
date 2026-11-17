# Evidence-Trust Architecture v2 — Results Review

**Experiment:** Four-authority evidence-trust threat matrix  
**Benchmark:** v0.4, HIGH-risk subset (700 cases; 14 families × 50)  
**Scenarios:** 19 (15 non-empty authority-compromise combinations, honest baseline, and three separate controls)  
**Case-scenario rows:** 13,300  
**Verified CI run:** [44025577491](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44025577491)  
**Workflow source commit:** `69a25ef9970c27b1932494d29df3a7704806f727` (GitHub Actions PR merge commit)  
**Artifact:** `ega-evidence-trust-v2`  
**Status:** Deterministic synthetic threat experiment; not production security evidence.

## 1. Main results

The benchmark contains 100 HIGH-risk cases labelled safe to act and 600 labelled unsafe to act. Results below are deterministic counts over the fixed benchmark, not estimated real-world probabilities.

| Scenario | ACT | Unsafe ACT | Unsafe / all 700 | Unsafe / ACT | Safe ACT coverage | False-block rate |
|---|---:|---:|---:|---:|---:|---:|
| Honest baseline | 50 | 0 | 0% | — | 50% | 50% |
| Capture only compromised | 0 | 0 | 0% | — | 0% | 100% |
| Interpretation only compromised | 0 | 0 | 0% | — | 0% | 100% |
| Witness only compromised | 100 | 50 | 7.14% | 50.00% | 50% | 50% |
| Capture + interpretation | 0 | 0 | 0% | — | 0% | 100% |
| Capture + witness | 350 | 300 | 42.86% | 85.71% | 50% | 50% |
| Interpretation + witness | 0 | 0 | 0% | — | 0% | 100% |
| Capture + interpretation + witness | 350 | 300 | 42.86% | 85.71% | 50% | 50% |
| Any combination including AA | 700 | 600 | 85.71% | 85.71% | 100% | 0% |
| Key-admin trust-store poisoning | 350 | 300 | 42.86% | 85.71% | 50% | 50% |
| Source forgery before capture | 0 | 0 | 0% | — | 0% | 100% |
| Disclosed shared-dependency witness | 0 | 0 | 0% | — | 0% | 100% |

For scenarios with no ACT decisions, the conditional unsafe-ACT rate is undefined and is shown as —. False-block rate is calculated only among the 100 ground-truth-safe cases.

## 2. Family-level outcomes

Under **witness-only compromise**, unsafe ACT occurred in C4 (consistent but wrong): 50/50 cases. The clean family C0 produced 50 safe ACT decisions. The remaining families were blocked by the combined policy.

Under **capture + witness**, **capture + interpretation + witness**, and **key-admin trust-store poisoning**, the same six families produced unsafe ACT:

| Family | Cases | Unsafe ACT |
|---|---:|---:|
| C1 extraction error | 50 | 50 |
| C2 cross-document conflict | 50 | 50 |
| C4 consistent but wrong | 50 | 50 |
| C6 verifier false accept | 50 | 50 |
| C9 cascading error | 50 | 50 |
| C13 corrupted provenance | 50 | 50 |
| **Total** | **300** | **300** |

Each of these scenarios also authorized 50 safe ACT decisions in C0. The remaining 350 cases were escalated.

Under **AA compromise**, all 700 cases received ACT. The 600 unsafe ACT decisions covered every family except C0 clean and C7 verifier false reject; those two families accounted for the 100 safe ACT decisions. This is the expected consequence of compromising the final authority that enforces the policy.

## 3. Interpretation

### Single-authority compromise is not uniformly safe

The witness authority is a critical trust dependency. In the synthetic C4 family, the source documents and extraction are internally consistent but wrong. When IWA is compromised, it can falsify the independent measured-weight claim so that the existing evidence gate and witness-agreement check both pass. This produced 50 unsafe ACT decisions from 700 cases (7.14% overall; 50% of the 100 ACT decisions).

The capture-only and interpretation-only scenarios produced no unsafe ACT, but they also blocked all 100 safe cases in this fixed benchmark. Their zero unsafe-ACT result therefore comes with a 100% false-block rate, not free robustness.

### Multi-authority and trust-registry compromise recreate the v1 failure

Capture + witness compromise, the three upstream authority compromise, and key-admin trust-store poisoning each produced 300 unsafe ACT decisions out of 700 (42.86% overall; 85.71% of ACT decisions). This matches the scale of the v1 combined trusted-root plus coordinated-upstream rewrite result, but under the v2 role/capability model.

The key-admin control does not steal the original role private keys. It models a poisoned trust registry accepting attacker-enrolled CA, IA and IWA keys while AA remains honest. The result shows that role separation is only meaningful if signer enrollment and trust-registry administration are independently protected.

### Source and dependency controls

The source-forgery-before-capture control produced no ACT because the honest independent witness retained the benchmark ground-truth value and the existing policy detected the resulting conflict. The shared-dependency control also produced no ACT because the witness disclosed the same source identifier, acquisition domain and administrative domain as capture, failing the independence check.

These are narrow results for the declared synthetic controls. They do not prove real source authenticity or operational independence. A compromised IWA can still sign false values and claim a separate source identity because this prototype does not authenticate source ownership or administrative-domain claims against an external registry.

### Authorization authority remains a hard trust boundary

Any compromise combination containing AA produced 700 ACT decisions and 600 unsafe ACT decisions. This is not a cryptographic-verification failure: the experiment explicitly gives compromised AA the ability to sign arbitrary decisions. The architecture cannot defend against an attacker who controls the component that finally enforces authorization without an additional independent enforcement boundary.

## 4. Comparison with document-root attestation v1

The v1 combined trusted-root compromise plus coordinated upstream rewrite produced 300 unsafe ACT decisions among 700 HIGH-risk cases; 300 of 350 ACT decisions were unsafe. The v2 capture+witness, capture+interpretation+witness and key-admin trust-store poisoning scenarios each produced the same 300/700 unsafe ACT outcome, with 300/350 ACT decisions unsafe.

The v2 design therefore does not eliminate the coordinated-compromise failure. Its contribution in this experiment is to expose which distinct trust combinations can recreate it and to show that a single witness-authority compromise already creates a narrower unsafe-ACT path.

## 5. Limitations

- The benchmark and all attack transformations are synthetic and deterministic.
- The independent witness is an oracle-like record derived from `ground_truth`; no real external source or sensor was contacted.
- The prototype checks declared source identifiers, acquisition-domain labels and administrative-domain labels. It does not authenticate the truth of those labels or independently prove separate ownership and operations.
- A compromised witness authority can falsify signed witness fields. The prototype does not use a second independent witness authority or threshold corroboration.
- Key-admin compromise is modeled as trust-store poisoning for CA, IA and IWA; real enrollment, root-of-trust, administrative access and recovery workflows are not implemented.
- The experiment reuses `evidence_gate_v1` as an additional policy condition. It is not a standalone evaluation of the cryptographic layer.
- Deterministic test keys are not production keys. KMS/HSM custody, authenticated enrollment, durable atomic replay state, operational revocation, secure capture and distributed transaction enforcement are absent.
- The results are not Monte Carlo estimates and have no sampling-based confidence intervals.
- No deployed AI system, customs platform, human reviewer or production workflow was evaluated.

## 6. Reproducibility and output integrity

The successful CI run executed regression tests, benchmark generation and integrity verification, reconstruction and sensitivity runners, the v1 document-root experiment, this v2 matrix, historical table loading and manuscript compilation.

Pinned output hashes from the archived artifact:

| File | SHA-256 |
|---|---|
| `evidence_trust_v2_cases.csv` | `0fe5c636ce1d66c3159bff97932652142b48a183d8ad32067460f43c5a6d7ea4` |
| `evidence_trust_v2_summary.csv` | `d25e8441bedc713663d2ad7f1175c3cfdbefd73b69aa05250270efddde3c9677` |

Artifact ZIP SHA-256: `d4f4df2b878991371b4f5437df8acd5301ba5aa9107fc280b0322fdfb9a4e61c`.

The raw case-level and summary CSVs are archived in the `ega-evidence-trust-v2` GitHub Actions artifact for run 44025577491. This review must not be read as a production security claim or as evidence that the proposed architecture is ready for deployment.
