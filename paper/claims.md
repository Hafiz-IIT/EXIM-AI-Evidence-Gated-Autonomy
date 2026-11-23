# Evidence-Gated Autonomy — Claim Ledger

**Purpose:** This file maps public-facing numerical and security claims to their benchmark version, implementation, protocol and output evidence. It is a claim-control document, not a peer-reviewed validation statement.

## Claim status vocabulary

- **Reproduced synthetic result:** Generated from committed code and a versioned protocol in a recorded CI run. It remains synthetic.
- **Historical reported result:** A value preserved in the repository, but its original runner or full parameter configuration is not recoverable from the current Git history.
- **Exploratory extension:** A later experiment under new assumptions; it must not be merged into historical manuscript tables.
- **Not evaluated:** No empirical evidence has yet been collected for the claim.

## Claim ledger

| ID | Claim or result | Evidence source | Status | Permitted interpretation |
|---|---|---|---|---|
| BENCH-03 | Benchmark v0.3 contains 500 unique synthetic evidence situations paired across LOW/HIGH consequence, giving 1,000 cases across 10 families. | scripts/generate_benchmark.py; scripts/verify_benchmark.py; data/benchmark/ | Reproduced synthetic result | Describes benchmark construction only. |
| BENCH-04 | Benchmark v0.4 contains 700 unique synthetic situations paired across LOW/HIGH consequence, giving 1,400 cases across 14 families. | scripts/generate_benchmark_v04.py; scripts/verify_benchmark_v04.py; generated manifest and CI artifact | Reproduced synthetic result | Describes benchmark construction only. |
| HIST-1A | The historical deterministic comparison reported 0/500 unsafe HIGH-risk ACT decisions for Evidence Gate versus 50/500 for Risk Gate and Always Verify. | Historical result files under results/exp1/ and results/exp2/; historical manuscript | Historical reported result | Must be labelled historical and synthetic. The original Experiment 1A downstream-resolution runner is not recovered; do not claim source-level reproduction. |
| HIST-1B | Historical stochastic results reported approximately 1.86%, 6.10% and 13.09% high-risk incorrect-action rates in optimistic, moderate and harsh regimes. | results/exp1/exp1b_stochastic_summary.csv; historical manuscript | Historical reported result | Must not be substituted with v1/v2 reconstruction values. Original runner/configuration is not recovered. |
| HIST-1C | Historical adversarial metadata/evidence transformations produced unsafe actions under dependency spoofing, external evidence masking and timestamp manipulation. | results/exp1/exp1c_stress_human90.csv; results/exp2/ | Historical reported result | Supports a synthetic failure-mode observation only; original runner/configuration is not recovered. |
| RECON-1 | Reconstruction v1 reruns selected 1B–2E experiments under a newly explicit protocol and 30 seeds per stochastic condition. | scripts/run_reconstruction_v1.py; experiments/reconstruction_v1/PROTOCOL.md; results/reconstruction_v1/; CI artifacts | Reproduced synthetic reconstruction | It is a new simulation, not a reproduction of historical CSVs. |
| RECON-2 | Reconstruction v2 applies the v1-style protocol to benchmark v0.4 and includes 25 sensitivity conditions. | scripts/run_reconstruction_v2.py; experiments/reconstruction_v2/PROTOCOL.md; results/reconstruction_v2/; CI artifacts | Reproduced synthetic reconstruction | Its Monte Carlo intervals describe simulator seed variability, not real-world uncertainty. |
| ATT-1 | The document-root attestation verifier rejected tested raw-document tampering, unsigned coherent rewrites, revoked keys, cross-tenant reuse and nonce replay on the v0.4 HIGH-risk set. | src/provenance.py; tests/test_document_root_attestation.py; scripts/run_document_root_attestation.py; experiments/document_root_attestation/ | Reproduced synthetic protocol experiment | Establishes behaviour for the implemented test cases, not production key security or truth. |
| ATT-2 | Under a deliberately coordinated compromise of the trusted document-root signer and upstream evidence channels, 300 of 700 HIGH-risk cases produced unsafe ACT (42.86% of all cases; 85.71% of ACT decisions). | experiments/document_root_attestation/RESULTS_REVIEW.md; document-root CI artifact | Reproduced synthetic adversarial result | A conditional attack outcome under explicit strong assumptions, not an incident probability or estimate of deployed-system risk. |
| TRUST-1 | A valid signature binds a payload to a key; it does not prove that the source claim is true. | src/provenance.py; document-root compromise experiment and results review | Supported design limitation | Do not describe cryptographic provenance as a truth certificate. |
| TRUST-2 | The document-root verifier checks a caller-supplied key-ID-to-signer-ID authorization mapping. | Current implementation and regression tests in src/provenance.py and tests/test_document_root_attestation.py | Implementation-level test claim | The mapping is not authenticated signer enrollment, PKI, KMS/HSM custody or an operational trust registry. |
| RETR-1 | Across 162 synthetic parameter conditions, Evidence Gate had a higher unsafe-ACT rate than Risk Gate in 145 conditions and a lower rate in 17; the paired 95% intervals were entirely positive in 141, entirely negative in 14 and crossed zero in 7. | scripts/run_retrieval_quality_sensitivity.py; experiments/retrieval_quality_sensitivity/PROTOCOL.md and RESULTS_REVIEW.md; CI artifact from workflow run 45086610287 | Reproduced exploratory synthetic sensitivity result | The result is conditional on the illustrative binary-error model, fixed 0.93 verifier accuracy and constructed v0.4 HIGH-risk cases. It is not a deployment-safety estimate. |
| REAL-1 | Real customs data, production deployment, external frontier-model evaluation and human-subject validation have not been established by the current benchmark results. | Repository research-boundary statements and experiment protocols | Not evaluated | Do not imply operational or human validation. |

## Version and interpretation rules

1. Never combine historical v0.3 CSVs with reconstruction v1/v2 outputs into one result table without clearly labelling the source and protocol.
2. Never describe reconstruction v1 or v2 as reproducing historical Experiment 1A or historical CSVs.
3. Never describe the v0.4 unkeyed content digest as an authenticated signature.
4. Never describe a valid Ed25519 signature as proof of document truth.
5. Report both unsafe ACT / all HIGH-risk cases and unsafe ACT / all ACT decisions; they answer different questions.
6. Report safe ACT coverage and false-block rate alongside unsafe-action metrics.
7. Separate deterministic benchmark conformance, stochastic simulation, prompt-level model evaluation, controller-level evaluation, human review and production evaluation.
8. Treat Monte Carlo intervals as uncertainty under the specified simulator, not as confidence intervals for deployment performance.
9. Retain negative findings and failure cases. Do not remove them because they weaken the preferred hypothesis.

## Current research blockers

- Recover the historical Experiment 1A downstream-resolution runner or explicitly retire its original numerical comparison.
- Complete independent literature and novelty review before making a novelty claim.
- Extend retrieval-quality sensitivity with correlated retrieval/verifier/human errors, empirically informed parameter ranges and intervention costs; retain its exploratory status.
- Obtain independent review of scenario labels, cost assumptions, source-dependency assumptions and attack capabilities.
- Complete real-provider evaluation separately from synthetic policy simulation.
- Reconcile every manuscript table and abstract statement against this ledger before any public preprint submission.
