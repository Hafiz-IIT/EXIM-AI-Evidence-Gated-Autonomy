# Evidence-Trust v3 Results Review

**Validation run:** [GitHub Actions #44168377670](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44164029203)  
**Benchmark:** v0.4, 700 HIGH-risk cases per scenario  
**Scenarios:** 8  
**Rows:** 5,600  
**Primary policy:** authenticated 2-of-3 witness quorum  
**Sensitivity:** strict 3-of-3 quorum on the same cases and signed assertions  
**Artifact:** `ega-evidence-trust-v3` (artifact ID `14365664343`)

## 1. Results

| Scenario | 2-of-3 ACT | 2-of-3 unsafe ACT | 2-of-3 safe coverage | 3-of-3 ACT | 3-of-3 unsafe ACT | 3-of-3 safe coverage |
|---|---:|---:|---:|---:|---:|---:|
| Honest baseline | 100 | 0 | 100% | 100 | 0 | 100% |
| One witness compromised | 100 | 0 | 100% | 100 | 0 | 100% |
| Two witnesses compromised | 150 | 50 | 100% | 100 | 0 | 100% |
| All witnesses compromised | 150 | 50 | 100% | 150 | 50 | 100% |
| Forged source identity credential | 100 | 0 | 100% | 0 | 0 | 0% |
| Source forgery before capture | 0 | 0 | N/A — no safe cases | 0 | 0 | N/A — no safe cases |
| Shared administrative domain | 0 | 0 | 0% | 0 | 0 | 0% |
| Registry signing-key compromise | 150 | 50 | 100% | 100 | 0 | 100% |

The benchmark has 100 safe cases in each scenario except source forgery before capture, where all 700 transformed cases are unsafe relative to the preserved physical ground truth. The 2-of-3 policy authorizes all safe cases in the scenarios where it can establish two independent valid witnesses; the shared-administration control blocks every case.

## 2. Family-level findings

The 50 unsafe ACT decisions in each of the following 2-of-3 scenarios occur only in C4, the internally consistent-but-wrong family:

- Two witnesses compromised: 50/50 C4 cases unsafe.
- All witnesses compromised: 50/50 C4 cases unsafe.
- Registry-root compromise: 50/50 C4 cases unsafe.

The 3-of-3 sensitivity blocks the two-witness and registry signing-key C4 cases because the third witness remains honest. It retains safe-case coverage in both scenarios because the third credential remains valid under the pinned registry public key. It does not block full-roster compromise: when all three witnesses are compromised and agree on the false value, 3-of-3 still produces 50 unsafe ACT decisions.

The bounded recovery path restores 50 safe C7 verifier-false-reject cases in the 2-of-3 baseline and in scenarios where a valid quorum remains available. Recovery is permitted only after a valid quorum and only when every other existing policy guard passes. It does not recover cases with invalid quorum, source forgery, or shared administrative control.

## 3. Security–availability trade-off

- **2-of-3:** tolerates one invalid/compromised witness and preserves safe coverage in the tested baseline, but two colluding witnesses can authorize the C4 false value.
- **3-of-3:** blocks the tested two-witness collusion and registry-root C4 attack, but fails closed under a forged credential, shared administrative domain, and registry-root compromise, losing all safe coverage in those scenarios.
- **Neither threshold:** prevents unsafe authorization when all three witnesses are compromised and agree.
- **Bounded recovery:** improves the baseline false-reject problem without bypassing quorum failure; it does not repair false source truth.

These are deterministic counts over a fixed synthetic benchmark, not deployment probabilities.

## 4. Claim boundary and limitations

- All keys, identities, measurements, source records and attacks are synthetic.
- The witness measurement is an idealized oracle derived from benchmark ground truth, not an independently operated physical sensor.
- Registry signatures authenticate the credential issuer, not the real-world truth of source identity or measurement.
- Distinct administrative-domain labels do not establish actual operational independence.
- The registry-root scenario assumes compromise of the existing registry signing private key while the verifier retains the original pinned public key; the attacker uses that key to enroll two attacker-controlled witnesses. This is distinct from replacing the verifier's trust anchor.
- No production PKI, KMS/HSM custody, hardware identity, secure acquisition, trusted time, durable revocation, or atomic action-commit mechanism is implemented.
- Source forgery before capture is distinct from credential forgery: honest capture can faithfully attest to forged source bytes, while independent witnesses retain physical ground truth and the controller escalates.
- Counts are deterministic synthetic outcomes, not real-world probabilities or production-security evidence.

## 5. Integrity and reproduction

Pinned manifest: [results/evidence_trust_v3/manifest-44168377670.json](../../results/evidence_trust_v3/manifest-44164029203.json).

Manifest:
- `evidence_trust_v3_cases.csv`: `3f91c67f40b276d900062008de72d9221cbf289dd5b979a82c941624730fff5e`
- `evidence_trust_v3_summary.csv`: `ff1b4ae6462b8b3a6253941564028fb94c9d0842b5d7f247a692c9bab27ab83b`

Reproduce with:

```bash
python -m unittest tests.test_evidence_trust_v3 -v
python scripts/run_evidence_trust_v3.py
```

The full workflow also regenerates benchmark v0.4, runs the reconstruction and attestation experiments, reproduces historical tables from checked-in result files, and compiles the manuscript. The historical 1B–2E numerical results remain distinct from the new reproducible reconstruction outputs.
