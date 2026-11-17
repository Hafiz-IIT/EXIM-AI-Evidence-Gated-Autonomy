# Evidence-Provenance v4 Results Review

**Validation run:** [GitHub Actions #44160689194](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44160689194)  
**CI result:** 29/29 steps passed, including regression tests, v4 experiment, artifact upload, all previous experiment suites, publication-table reproduction and LaTeX compilation.  
**Benchmark:** v0.4, 700 HIGH-risk cases per scenario  
**Rows:** 16 scenarios × 700 = 11,200 case-scenario rows  
**Artifact:** `ega-evidence-provenance-v4`  
**Artifact ID:** `14362294566`  
**Source commit:** `75447c40fcb0be0eb05100dc65762114269ca6aa`

## 1. Summary

| Scenario | ACT | Unsafe ACT | Safe-ACT coverage | False-block rate |
|---|---:|---:|---:|---:|
| Honest baseline | 100 | 0 | 100% | 0% |
| Source forgery before capture | 100 | 0 | 100% | 0% |
| Duplicate replay | 0 | 0 | 0% | 100% |
| Stale evidence | 0 | 0 | 0% | 100% |
| Cross-subject substitution | 0 | 0 | 0% | 100% |
| Cross-claim substitution | 0 | 0 | 0% | 100% |
| Parser lineage tampering | 0 | 0 | 0% | 100% |
| Invalid calibration | 0 | 0 | 0% | 100% |
| Shared admin/gateway | 0 | 0 | 0% | 100% |
| Credential tampering | 0 | 0 | 0% | 100% |
| Action-payload substitution | 0 | 0 | 0% | 100% |
| Single weighbridge compromise | 150 | 50 | 100% | 0% |
| Isolated tariff-registry compromise | 100 | 0 | 100% | 0% |
| Tariff compromise + independent false-accept verifiers | 150 | 50 | 100% | 0% |
| All evidence sources compromised | 150 | 50 | 100% | 0% |
| Registry-root compromise | 150 | 50 | 100% | 0% |

The benchmark contains 100 safe cases (C0 and C7). In the honest baseline, all 100 are authorized and no unsafe case is authorized. The bounded verifier-false-reject recovery remains active, but only when the legacy policy's other conditions pass.

## 2. Main findings

### 2.1 Claim scope and provenance checks fail closed

Duplicate replay, stale evidence, cross-subject substitution, cross-claim substitution, parser-lineage tampering, invalid calibration, shared administration/gateway, credential tampering and action-payload substitution each produced zero ACT decisions. Each scenario also blocked all 100 safe cases, so the false-block rate was 100%. These are intentionally severe integrity/scope attacks applied to every case in the scenario; the result demonstrates fail-closed behavior, not an acceptable operational availability level.

The v4 checks bind each assertion to the case subject, action ID, canonical action-payload digest, document digest, claim type, expected unit, source credential, evidence validity window, parser input/output lineage and (where applicable) calibration validity. Replay and monotonic-sequence state are caller-managed and shared across claim evaluations in the runner.

### 2.2 Source compromise can still produce unsafe authorization

A single compromised weighbridge source produced 50 unsafe ACT decisions in the C4 consistent-but-wrong family. The attacker-controlled measurement was aligned with the forged document/parser value, so the claim checks saw internally consistent but false evidence.

A tariff-registry compromise in isolation produced no unsafe ACT in this fixture because the existing policy's correlated-verifier guard blocked the C8 family. When the tariff registry was compromised and two verifiers were assigned distinct dependency labels while both false-accepted the wrong HS code, 50 unsafe C8 actions were authorized. This is a compound scenario: it shows that distinct verifier labels do not establish correctness or actual independence.

Compromise of all evidence sources and compromise of the registry root each produced 50 unsafe C4 ACT decisions. Signatures and source credentials cannot establish semantic truth when the source or trust root is compromised.

### 2.3 The availability trade-off is material

The metadata/scope attack scenarios all fail closed, but they also block every safe case in those scenarios. The experiment therefore reports security and availability together. It does not claim that strict rejection is a production-ready policy.

## 3. Interpretation boundary

This is a hybrid synthetic controller: the existing v1 evidence gate, v3 bounded recovery for a narrow verifier false rejection, and v4 claim-scoped provenance/action-binding checks. It is not a standalone deployed controller.

- All identities, credentials, evidence, source values, calibration fields and attacks are synthetic.
- Signatures authenticate enrolled keys and signed bytes, not the truth of source claims.
- Calibration validity and administrative-domain values are asserted test fields, not hardware-backed evidence.
- The action-payload digest binds a synthetic action descriptor; no external side effect is executed.
- Replay state is caller-managed in-memory state. No durable distributed nonce store, atomic action commit, or one-time action-grant redemption is implemented.
- A compromised source can sign false but correctly scoped evidence.
- The trust root remains an explicit trust assumption.
- The experiment does not implement production PKI, KMS/HSM custody, hardware identity, secure acquisition, or independent dependency-graph verification.
- Counts are deterministic synthetic outcomes, not real-world probabilities or production-security evidence.

## 4. Reproduction and integrity

Run:

```bash
python -m unittest discover -s tests -v
python scripts/generate_benchmark_v04.py
python scripts/verify_benchmark_v04.py
python scripts/run_evidence_provenance_v4.py
```

The CI artifact manifest records:

- `evidence_provenance_v4_cases.csv`: `3e6deba7f42a33d5df9f71b68a0d84795eda01413288f157709dae255dfed48b`
- `evidence_provenance_v4_summary.csv`: `a06655bb7fae2328d7d96450921b7a404098fbb296ce12e0f6a383626ef534d0`

## 5. Next research question

The v4 results show that claim scope, freshness, replay, lineage and action binding can be modeled and tested, but direct administrative/gateway labels and source credentials still do not establish transitive independence. The next experiment (v5) compares key-unique, direct-field-distinct 2-of-3/3-of-3, and graph-aware quorum selection using signed dependency ancestry across parent control, cloud identity, KMS, firmware/build, acquisition devices and upstream feeds. EFD and ARP already cover the general theory; v5 is an EXIM-specific empirical comparison, not a new structural-cut metric.
