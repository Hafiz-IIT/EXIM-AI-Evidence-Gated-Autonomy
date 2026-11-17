# Document-Root Attestation — Results Review

**Protocol:** v1  
**Benchmark:** v0.4, HIGH-risk subset (700 cases; 14 families × 50 cases)  
**Verified CI run:** [43955044311](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43955044311)  
**Source commit:** `8e2dc845efefb856818ca61011395f8887249b38`  
**Archived artifact:** `ega-document-root-attestation-v1` (GitHub Actions artifact, run 43955044311)  
**Status:** Synthetic protocol/threat experiment; not production security evidence.

## 1. Results

The runner evaluates nine scenarios for each of the 700 HIGH-risk benchmark cases. The 6,300 case-scenario rows and summary CSVs are archived in the CI artifact. The output hashes and execution metadata are recorded in `manifest-43955044311.json`.

| Scenario | Attestation accepted | Rejected | Downstream ACT | Unsafe ACT |
|---|---:|---:|---:|---:|
| Valid baseline | 700/700 | 0 | 50 | 0 |
| Raw document-instance tampering | 0/700 | 700 | 0 | 0 |
| Coherent rewrite without trusted private key | 0/700 | 700 | 0 | 0 |
| Trusted root signer compromise + coordinated upstream rewrite | 700/700 | 0 | 350 | **300** |
| Revoked old key | 0/700 | 700 | 0 | 0 |
| Rotated new key | 700/700 | 0 | 50 | 0 |
| Cross-tenant replay | 0/700 | 700 | 0 | 0 |
| First nonce use | 700/700 | 0 | 50 | 0 |
| Second nonce use (replay) | 0/700 | 700 | 0 | 0 |

The baseline and lifecycle-control scenarios show that the implemented verifier rejects the tested mismatches, revoked-key use, cross-tenant reuse and repeated nonce use. A new trusted key is accepted after rotation in this simplified keyring model.

## 2. Compromised-root outcome

In the combined compromise scenario, the attacker is assumed to:
1. possess the trusted document-root private key;
2. coherently rewrite raw document instances and normalized document slots;
3. coordinate changes to machine extraction, HS classification and externally measured weight;
4. sign the rewritten document representations with the compromised key.

The resulting attestation verifies. The existing evidence gate then authorizes ACT in 350/700 cases. Of those, 300 are unsafe relative to the benchmark's original ground-truth label:

- **Unsafe ACT / all HIGH-risk cases:** 300/700 = **42.86%**.
- **Unsafe ACT / policy-authorized ACT cases:** 300/350 = **85.71%**.
- The other 50 ACT decisions are in the clean family and are safe.

This is not an estimate of real-world incident probability. It is a deterministic synthetic stress-test result under an explicitly strong, coordinated compromise assumption.

## 3. Family-level breakdown under combined compromise

| v0.4 family | Cases | ACT | Unsafe ACT |
|---|---:|---:|---:|
| C0 clean | 50 | 50 | 0 |
| C1 extraction error | 50 | 50 | 50 |
| C2 cross-document conflict | 50 | 50 | 50 |
| C3 missing critical evidence | 50 | 0 | 0 |
| C4 consistent but wrong | 50 | 50 | 50 |
| C5 stale evidence | 50 | 0 | 0 |
| C6 verifier false accept | 50 | 50 | 50 |
| C7 verifier false reject | 50 | 0 | 0 |
| C8 correlated verifier failure | 50 | 0 | 0 |
| C9 cascading error | 50 | 50 | 50 |
| C10 missing invoice | 50 | 0 | 0 |
| C11 missing packing list | 50 | 0 | 0 |
| C12 duplicate document kind | 50 | 0 | 0 |
| C13 corrupted provenance | 50 | 50 | 50 |
| **Total** | **700** | **350** | **300** |

The six families that pass the compromised gate are C1, C2, C4, C6, C9 and C13. The other families are blocked by checks that remain effective under this particular rewrite. This family pattern is specific to the current benchmark and attack transformation.

## 4. Interpretation

The experiment supports a narrow but important conclusion:

**A signature over document bytes/normalized fields can establish integrity relative to a trusted signing key; it cannot establish semantic truth when the signing authority and the channels used for corroboration are jointly compromised.**

The signature design blocks unauthorized edits and selected lifecycle attacks when the trust root is intact. It does not make a compromised trust root safe, nor does it establish that the documents were truthful at capture time.

The 42.86% figure must not be described as the expected failure rate of a deployed system. The experiment intentionally assumes coordinated control over the signing key and upstream evidence channels. It is a conditional attack-success rate on this synthetic benchmark.

## 5. Architecture implications

The next design should not simply add more signatures to the same trust domain. It should separate the provenance of *capture* from the production of *semantic interpretations* and the authorization decision:

1. **Independent capture authority:** a narrowly scoped ingestion/capture service should attest to source identity, acquisition channel, receipt time and immutable raw-object digest. It should not certify that extracted values are true.
2. **Separate interpretation lineage:** OCR, normalization, classification and model extraction should have their own versioned lineage and attestations, distinct from the raw-capture authority.
3. **Independent corroboration:** high-consequence fields should be checked against independently acquired sources (for example, a separately administered measurement or authoritative external record), not a second representation derived from the same compromised input.
4. **Trust-domain separation:** capture, extraction, external sensing and action authorization should not share a single signing authority or administrative control plane. Threshold/multi-party authorization may reduce single-key blast radius, but only if the parties are operationally independent.
5. **Fail-closed authorization:** invalid, missing, stale or replayed evidence proofs must prevent ACT and produce a review/evidence-request outcome. The authorization engine must verify proofs against a trust registry obtained independently of the evidence payload.
6. **Operational controls:** production would require KMS/HSM-backed keys, authenticated signer enrollment, key rotation and revocation procedures, durable atomic replay state, audit logs and incident response. None is implemented by this synthetic experiment.

A follow-up experiment should separately vary (a) capture signer compromise, (b) extraction signer compromise, (c) external sensor compromise, (d) authorization signer compromise, and (e) pairs/triples of these compromises. It should include attacks where the attacker can alter only one channel, and cases where supposedly independent channels share a hidden upstream dependency. The proposed separation-of-duties design and preregistered threat matrix are documented in [ARCHITECTURE_V2.md](ARCHITECTURE_V2.md); this is a design proposal, not an implemented control.

## 6. Limitations

- Deterministic test keys are derived from fixed labels; they are not production secrets.
- The synthetic tenant identifier and in-memory nonce set do not implement real tenant isolation or distributed replay protection.
- The test does not establish secure capture, source identity, truthfulness of source documents, operational key custody, or real-world attack prevalence.
- The coordinated-compromise transformation modifies several channels together; its assumptions are deliberately stronger than a document-signing-key-only compromise.
- The benchmark is synthetic and its family composition is controlled.
- No production customs, logistics, government, or enterprise system was evaluated.

## 7. Reproducibility

The full workflow passed on 16 November 2026:
- regression tests;
- v0.3/v0.4 benchmark generation and integrity checks;
- v1 and v2 reconstruction;
- document-root attestation runner;
- artifact uploads;
- historical table loading;
- manuscript compilation.

Run link: https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43955044311

The manifest records source commit, Python version, run ID and SHA-256 hashes for both CSV outputs. This experiment is a new synthetic threat study and does not replace historical manuscript results.
