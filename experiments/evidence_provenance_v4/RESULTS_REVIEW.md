# Evidence-Provenance v4 Results Review

**Validation run:** [GitHub Actions #44167896361](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44167896361)  
**Benchmark:** v0.4, 700 HIGH-risk cases per scenario  
**Scenarios:** 16  
**Rows:** 11,200  
**Artifact:** `ega-evidence-provenance-v4` (artifact ID `14367370104`)

## 1. Results

| Scenario | ACT | Unsafe ACT | Safe-ACT coverage | False-block rate |
|---|---:|---:|---:|---:|
| Honest baseline | 100 | 0 | 100% | 0% |
| Source forgery before capture | 0 | 0 | N/A — no safe cases | N/A |
| Replay attack | 0 | 0 | 0% | 100% |
| Stale evidence | 0 | 0 | 0% | 100% |
| Cross-subject substitution | 0 | 0 | 0% | 100% |
| Cross-claim substitution | 0 | 0 | 0% | 100% |
| Parser-lineage tampering | 0 | 0 | 0% | 100% |
| Invalid calibration | 0 | 0 | 0% | 100% |
| Shared admin/gateway | 0 | 0 | 0% | 100% |
| Credential tampering | 0 | 0 | 0% | 100% |
| Action substitution | 0 | 0 | 0% | 100% |
| Single weighbridge compromise | 150 | 50 | 100% | 0% |
| Single tariff-registry compromise | 100 | 0 | 100% | 0% |
| Tariff compromise + independent false accept | 150 | 50 | 100% | 0% |
| All sources compromised | 150 | 50 | 100% | 0% |
| Registry signing-key compromise | 150 | 50 | 100% | 0% |

There are 100 safe cases in each scenario except the pre-capture source-forgery scenario, where all 700 transformed cases are unsafe relative to the preserved physical ground truth. The 50 safe C7 verifier-false-reject cases are recovered in six scenarios where claim evidence and action binding remain valid, for 300 recovered safe actions across this experiment.

## 2. Attack-family findings

- **Pre-capture source forgery:** all 700 cases are transformed before capture. The capture digest is recomputed and the parser honestly extracts the forged document values, so provenance integrity is valid. The independent weighbridge, RFID counter and tariff registry retain original ground truth. All three claim checks return `claim_value_conflict`; all 700 decisions escalate and none ACT.
- **Single weighbridge compromise:** 50 unsafe ACT decisions occur in C4 consistent-but-wrong.
- **Tariff compromise with independent false accept:** 50 unsafe ACT decisions occur in C8 correlated-verifier failure.
- **All sources compromised:** 50 unsafe ACT decisions occur in C4.
- **Registry signing-key compromise:** 50 unsafe ACT decisions occur in C4. The scenario assumes the existing issuer private key is compromised while the verifier retains the original pinned public key; the attacker can enroll attacker-controlled source keys across the evidence roles. This is a combined issuer-key and source re-enrollment compromise, not a trust-anchor replacement scenario.
- **Single tariff-registry compromise:** zero unsafe ACT decisions in this benchmark; the existing correlated-verifier guard blocks the false-accept family.
- **Replay, stale evidence, cross-subject/claim substitution, parser-lineage tampering, invalid calibration, shared administration, credential tampering and action substitution:** each attack is fail-closed, but each also blocks all 100 safe cases in its scenario.

## 3. Bounded recovery behavior

The v4 controller recovers 50 safe C7 verifier-false-reject cases only when:
1. the existing evidence gate's remaining guards pass;
2. all claim-specific evidence is valid and mutually consistent;
3. source competence and calibration checks pass;
4. the evidence is bound to the correct subject and action payload; and
5. the verifier rejection is the isolated recoverable condition.

Recovery does not override replay, stale evidence, source/claim mismatch, invalid calibration, credential failure, shared administration, or action substitution. The 300 recovered safe actions are deterministic benchmark counts, not an estimated real-world recovery rate.

## 4. Claim boundary and limitations

- All identities, source credentials, evidence values, and attacks are synthetic.
- Signatures authenticate enrolled keys and signed bytes, not semantic truth.
- Calibration, administrative-domain and gateway status are asserted test fields, not hardware-backed evidence.
- The registry signing-key scenario assumes compromise of the existing issuer private key and attacker-controlled source re-enrollment across all evidence roles; the original public key remains pinned.
- The benchmark does not implement production PKI, KMS/HSM custody, secure hardware identity, durable revocation, trusted time, or an atomic distributed action-commit protocol.
- Deterministic counts are not real-world probabilities or production-security evidence.

## 5. Integrity and reproduction

Pinned manifest: [results/evidence_provenance_v4/manifest-44167896361.json](../../results/evidence_provenance_v4/manifest-44167896361.json).

Output hashes:
- `evidence_provenance_v4_cases.csv`: `94e9ddba2319cf1c066cea54490c1fa3e9991357d92d065b5b1ce612029443d8`
- `evidence_provenance_v4_summary.csv`: `2b6c2bf9fd94aa0d320184f0578eddcf4c9fa5922817b3f94250a4bcb4aa633a`

Reproduce with:

```bash
python -m unittest tests.test_evidence_provenance_v4 -v
python scripts/run_evidence_provenance_v4.py
```

The full workflow also runs benchmark integrity checks, reconstruction and sensitivity experiments, v3 and v5 studies, publication-table reproduction, and manuscript compilation.
