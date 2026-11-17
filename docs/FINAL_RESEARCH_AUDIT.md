# Evidence-Gated Autonomy — Experiment 1A–1D Final Research Audit

## 1A — deterministic synthetic benchmark
500 unique underlying evidence situations, paired into 1,000 LOW/HIGH action cases.
Evidence Gate: 0/500 HIGH-risk unsafe ACT decisions in the deterministic environment.
This result is intentionally treated as a sanity/proof-of-concept result only.

## 1B — imperfect stochastic verification/retrieval/escalation
30 Monte Carlo seeds per regime.
Evidence Gate mean HIGH-risk ICAR:
- optimistic: 0.0186 ± 0.0052
- moderate: 0.0610 ± 0.0115
- harsh: 0.1309 ± 0.0131

Moderate Risk Gate ICAR: 0.1655.

## 1C — adversarial evidence/provenance stress
The method's main discovered vulnerability is reliance on trustworthy evidence metadata.
Dependency spoofing and external-evidence masking materially increase ICAR; combined metadata/evidence spoofing reaches ~24% in the current stress design.

## 1D — OOD / compound shift
Frozen policies evaluated under nuisance shift, overconfidence, provenance dropout, and compound shift.
Compound shift:
- Evidence Gate: 0.1195
- Risk Gate: 0.1851
- Confidence-only: 0.7660

## Interpretation
The strongest defensible conclusion is not that evidence gating "solves" agent safety. It is:
1. confidence-only action authorization is brittle in this controlled testbed;
2. explicit external grounding and evidence-source independence add measurable protection in the benchmark;
3. those benefits collapse when provenance/independence signals can be spoofed;
4. a serious implementation therefore needs trustworthy evidence provenance/attestation rather than merely more verifier votes.

## Research status
These are synthetic and Monte Carlo experiments. No external LLM API outputs, real customs records, production deployment, or human-subject experiments are represented here.

## Historical reproducibility qualification

The historical 1B–2E result CSVs were added to Git without their original simulation runners or complete parameter configurations. Git history for the 1B summary confirms that the result file was committed by itself. The original Experiment 1A downstream-resolution implementation is also absent. Historical numbers are therefore preserved as reported outputs, not independently reproduced results.

## New reconstruction v1

The verified execution is [GitHub Actions run 43949299526](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43949299526), and its output hashes/source provenance are pinned in [manifest-43949299526.json](../results/reconstruction_v1/manifest-43949299526.json). It completed successfully, including manuscript compilation. A separate executable reconstruction is defined in:
- `experiments/reconstruction_v1/PROTOCOL.md`
- `scripts/run_reconstruction_v1.py`
- `tests/test_reconstruction_v1.py`
- `results/reconstruction_v1/README.md`
- `experiments/reconstruction_v1/RESULTS_REVIEW.md`

It runs new 1B, 1C, 1D, 2B, 2C, 2D and 2E experiments under explicit assumptions and 30 Monte Carlo seeds per condition. It does not claim to recreate the historical results. The runner creates role-scoped synthetic attestations, preserves baseline gate decisions in dual-lineage tests, records source revision/run metadata, and hashes generated CSV outputs in its manifest.

### Preliminary interpretation

- Under the new 1B protocol, Evidence Gate's ICAR is 0.81% optimistic, 4.95% moderate and 13.51% harsh. In the moderate regime Risk Gate is 5.30%, so the observed advantage is small and costs more intervention units.
- Under 1C, the new Evidence Gate ICAR is 6.21% without attack and 14.71–33.89% across the specified metadata attacks.
- Under 1D, the chosen shifts do not increase Evidence Gate ICAR (6.52% in-distribution; 6.20% compound). The current OOD protocol is insufficient to support a robustness or degradation claim.
- Under 2B, role-scoped attestations block direct unsafe ACTs under the unsigned metadata attacks by causing escalation.
- Under 2D, compromising a single relevant root produces 10% ICAR; compromising all three produces 30%.
- Under 2E, the stylized C8 test gives 0% ICAR under no/single-authority compromise and 10% when both lineage authorities are compromised.

These results are synthetic and conditional on the new protocol. They are not replacements for the historical tables and must not be inserted into the manuscript until independent review, stronger OOD design, sensitivity analysis and claim reconciliation are complete.

## Benchmark v0.4 and reconstruction v2

### Benchmark changes

Benchmark v0.4 is generated separately from v0.3 and preserves the historical dataset:
- 700 unique underlying situations, paired into 1,400 LOW/HIGH cases.
- 14 fault families, 100 paired-risk cases per family.
- New families: missing invoice, missing packing list, duplicate document kind, corrupted provenance.
- The verifier checks pair integrity, family counts, fault placement and SHA-256 checksums for generated JSONL files.
- Policy tests verify that missing invoice/packing list request evidence and duplicate document kinds/corrupted digests escalate.

**Security boundary:** the document-set digest is unkeyed. A regression test coherently rewrites document, extraction and external-weight values, recomputes the digest and confirms the current gate still returns ACT. It therefore detects mismatch/corruption, not malicious source rewriting or authenticity. A trusted document-root signature is still required.

### Reconstruction v2 execution

The full v2 run [43952541323](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43952541323) passed regression tests (including the coherent-rewrite limitation test), v0.3/v0.4 benchmark generation and integrity checks, v1/v2 reconstruction, historical-table loading, artifact uploads, execution-status publication and LaTeX compilation. Its manifest is pinned at [manifest-43952541323.json](../results/reconstruction_v2/manifest-43952541323.json). It records:
- 1,400 benchmark records / 700 HIGH-risk cases;
- 30 Monte Carlo seeds per stochastic condition;
- 25 sensitivity conditions and 2,250 per-seed sensitivity rows;
- 75 sensitivity summary groups;
- 30,100 synthetic signature records across the 2B–2E reconstruction;
- SHA-256 hashes for all 16 CSV outputs;
- source commit `aa0c67e234f880c8cb10b50036d1d9c51f027b60`, Python 3.11.18.

The coherent-rewrite regression test passed in the same full CI run. It does not change the experiment runner or generated numerical outputs.

### Main v0.4 results

- **1B moderate regime:** Evidence Gate ICAR 5.03%; Risk Gate 5.72%. The paired EGA-minus-Risk-Gate difference is −0.70 percentage points (95% t interval −1.25 to −0.14 pp). The optimistic interval includes zero; the harsh difference is −1.35 pp (−1.97 to −0.74 pp).
- Evidence Gate mean intervention cost is 1.4286 versus 1.0000 for Risk Gate under the current cost model (+0.4286 units per HIGH-risk case).
- **1C:** Evidence Gate ICAR rises from 5.99% without attack to 12.12–12.95% under the individual metadata attacks and 25.72% under combined spoofing.
- **1D:** Evidence Gate ICAR is 6.28% in-distribution and 5.94% under the current compound shift. The current OOD transformations do not establish robustness or degradation.
- **2B:** the signed variant records zero unsafe ACTs for the tested unsigned metadata attacks by escalating when covered component digests fail.
- **2C:** under 90%-accurate simulated human review, ICAR ranges from 2.65% to 8.74% across the tested attack conditions.
- **2D:** one relevant trust-root compromise yields 7.14% ICAR; all three covered roots compromised yields 21.43%.
- **2E:** both lineage authorities compromised yields 7.14% ICAR in the stylized C8 test; no/single-authority compromise yields zero.

### Sensitivity findings

Paired differences are Evidence Gate minus Risk Gate ICAR, in percentage points, with 30 seeds per condition:
- Verifier accuracy 0.75: −11.37 pp; 0.85: −5.40 pp; 0.93: −0.62 pp; 0.99: **+2.80 pp**.
- Human accuracy 0.70: **+5.16 pp**; 0.80: **+2.04 pp**; 0.90: −0.92 pp; 0.98: −3.47 pp.
- Retrieval success 0.70–0.99: −0.28 to −1.23 pp.
- Escalation availability 0.70–1.00: −0.79 to −1.02 pp.
- In the human-accuracy × availability interaction, low reviewer accuracy (0.70) leaves Evidence Gate 4.90–5.30 pp worse than Risk Gate; at reviewer accuracy 0.98 it is 3.43–3.54 pp better.

**Interpretation:** the policy's relative advantage depends strongly on downstream verifier/reviewer quality. At very high verifier accuracy, Always Verify/Risk Gate can outperform a gate that directly authorizes selected cases. Low human-review accuracy can reverse the benefit of escalation. The current cost model also makes Evidence Gate more intervention-intensive.

### Remaining research blockers

1. Analyze independent and combined trust-domain compromises in the new document-root attestation protocol; its first synthetic results are now available.
2. Improve OOD shifts and expand sensitivity beyond one-factor and selected two-factor sweeps.
3. Inspect false accepts/false blocks by family and severity beyond the first document-root family breakdown.
4. Recover or retire the historical 1A downstream-resolution comparison.
5. Reconcile manuscript claims against the new results without fitting parameters to historical values.
6. Complete an independent literature/novelty and methods review.

The v0.4 outputs are new synthetic evidence, not historical reproductions, production security evidence, real customs performance, real-model evaluation or human-subject validation. The manuscript remains **not ready for arXiv submission**.


## Document-root attestation threat experiment v1 (CI-verified)

The dedicated document-root signer prototype binds raw document instances and normalized document slots using Ed25519, with tenant/case binding, expiry, key revocation, key rotation and nonce replay checks. Protocol: [experiments/document_root_attestation/PROTOCOL.md](../experiments/document_root_attestation/PROTOCOL.md). Results review: [experiments/document_root_attestation/RESULTS_REVIEW.md](../experiments/document_root_attestation/RESULTS_REVIEW.md).

The full CI run [43955044311](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43955044311) passed tests, benchmark generation/verification, v1/v2 reconstruction, document-root threat runner, artifact uploads, historical-table loading and manuscript compilation. The document-root artifact contains 6,300 case-scenario rows across nine scenarios and 700 HIGH-risk v0.4 cases.

Under baseline, raw tampering, unsigned coherent rewrite, revoked-key, rotated-key, cross-tenant and nonce-replay tests, the expected attestation outcomes occurred for all 700 cases in each scenario. Under the combined trusted-root compromise plus coordinated upstream rewrite, 700/700 forged attestations verified; the downstream policy authorized ACT in 350 cases, 300 unsafe against benchmark ground truth (42.86% of all HIGH-risk cases; 85.71% of ACT decisions). The 300 unsafe ACTs occurred in C1, C2, C4, C6, C9 and C13, 50 per family.

**Interpretation boundary:** this is a deliberately strong synthetic combined-compromise scenario, not an estimate of deployment risk and not evidence that private-key theft alone produces the same outcome. It demonstrates that a signature proves a trusted key signed a bound payload, not that the payload is semantically true. The prototype uses deterministic test keys and process-local replay state; it does not implement production KMS/HSM custody, independent signer enrollment, secure capture, distributed replay storage or operational key management. The manuscript must retain these qualifications.


## Four-authority Evidence-Trust v2 threat experiment

### Implementation and validation

- Role-separated Ed25519 attestations: `src/evidence_trust_v2.py`
- Threat-matrix runner: `scripts/run_evidence_trust_v2.py`
- Regression tests: `tests/test_evidence_trust_v2.py`
- Protocol: [experiments/evidence_trust_v2/PROTOCOL.md](../experiments/evidence_trust_v2/PROTOCOL.md)
- Results review: [experiments/evidence_trust_v2/RESULTS_REVIEW.md](../experiments/evidence_trust_v2/RESULTS_REVIEW.md)
- Pinned outputs: [results/evidence_trust_v2/manifest-44025577491.json](../results/evidence_trust_v2/manifest-44025577491.json)
- Successful full CI run: [44025577491](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44025577491)

The runner evaluates all 15 non-empty compromise combinations of CA, IA, IWA and AA, plus an honest baseline, source forgery before capture, disclosed shared-source witness, and key-admin trust-store poisoning. It generates 13,300 case-scenario rows over 19 scenarios, each containing 700 HIGH-risk v0.4 cases. The successful run passed the full regression suite, both benchmark generators/verifiers, reconstruction and sensitivity runners, v1 document-root runner, v2 threat matrix, historical-table loading, artifact uploads and LaTeX compilation.

### Main findings

- Honest baseline: 0 unsafe ACT; 50 ACT, all safe; safe-ACT coverage 50%, false-block rate 50%.
- IWA-only compromise: 50 unsafe ACT (7.14% of all HIGH-risk cases; 50% of ACT decisions), all in C4 consistent-but-wrong.
- CA+IWA, CA+IA+IWA, and key-admin trust-store poisoning: 300 unsafe ACT each (42.86% overall; 85.71% of ACT decisions), across C1, C2, C4, C6, C9 and C13 (50 each).
- Any compromise combination containing AA: 700 ACT, 600 unsafe (85.71% overall).
- Source forgery before capture and disclosed shared-dependency witness: no ACT in this synthetic model.

### Audit interpretation and remaining limitations

The experiment demonstrates that role separation can contain some isolated capture/interpretation compromises, but the witness authority remains a critical trust dependency. A disclosed common source is rejected by comparing declared source/acquisition/administrative-domain labels; those labels are not externally authenticated. The ground-truth-derived witness is an idealized oracle, not a real independent measurement. Key-admin compromise is modeled as trust-store poisoning for CA/IA/IWA while AA remains honest. AA compromise is modeled as arbitrary authorization. These are deterministic synthetic outcomes, not deployment-risk estimates.

The implementation does not include production KMS/HSM custody, authenticated signer enrollment, externally anchored trust registry, durable atomic replay storage, operational revocation, secure capture, or independent administrative-domain verification. The manuscript must retain these limitations and remain **not ready for arXiv submission** pending independent review, source-level reconciliation and further empirical work.
