# Document-Root Attestation Threat Experiment v1

**Status:** Implemented; CI run [43955044311](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43955044311) passed. Synthetic protocol experiment only. Results review: [RESULTS_REVIEW.md](RESULTS_REVIEW.md).

## Research question

Can a trusted document-root authority cryptographically bind both (a) the raw document-instance list and (b) the normalized document map to a specific tenant and case, so that an attacker cannot coherently rewrite both representations and recompute an unkeyed digest?

## Attestation construction

The Ed25519-signed payload binds:
- schema/version;
- signer identity and key identifier;
- tenant identifier and case identifier;
- SHA-256 of canonicalized raw document instances;
- SHA-256 of canonicalized normalized document slots;
- issuance and expiry timestamps;
- a unique nonce.

Verification checks the trusted key registry, revocation set, tenant/case scope, validity window, both document digests, replay state and Ed25519 signature. The nonce is consumed only after all checks succeed.

## Threat experiments

The runner evaluates these scenarios for each HIGH-risk v0.4 case:

1. Valid baseline attestation.
2. Raw document-instance tampering.
3. Coherent rewrite of raw and normalized documents without access to the trusted private key; the study harness fails closed to ESCALATE when attestation verification fails.
4. Trusted document-root signer compromise plus coherent upstream rewrite of raw documents, normalized slots, extraction and measured weight. The attacker can produce a new valid signature over the rewritten documents; the existing evidence gate is then evaluated to measure whether other checks still block unsafe ACT.
5. Revoked old signing key.
6. Key rotation to a new trusted key while the old key is revoked.
7. Cross-tenant replay.
8. First use of a nonce and second-use replay.

The CSV distinguishes **attestation acceptance** from the downstream **policy action**. The intended expected outcomes are:
- valid baseline: attestation accepted; existing evidence gate decides the action;
- raw tamper and coherent rewrite without the private key: attestation rejected and harness action is ESCALATE;
- signer compromise: forged attestation accepted, then the existing evidence gate is evaluated. Unsafe ACTs, if any, are counted against the original benchmark ground truth. This demonstrates the limits of document-root signing under trust-root compromise plus coordinated upstream manipulation;
- revoked key: reject;
- rotated new key: accept;
- cross-tenant replay: reject;
- first nonce use: accept; second use: reject.

## Results summary

Across 700 HIGH-risk v0.4 cases, the verifier rejected all tested raw tampering, unsigned coherent rewrites, revoked-key use, cross-tenant reuse and second-use nonce replays. It accepted valid baseline and rotated-key attestations. Under the combined trusted-root compromise plus coordinated upstream rewrite, the forged attestation was accepted in all 700 cases; the downstream policy issued 350 ACT decisions, 300 of which were unsafe against benchmark ground truth (42.86% of all HIGH-risk cases; 85.71% of ACT decisions). See [RESULTS_REVIEW.md](RESULTS_REVIEW.md) for the family breakdown, threat assumptions and interpretation. These rates are synthetic conditional attack outcomes, not real-world probabilities.

## Reproducibility

Run:
```bash
python -m unittest discover -s tests -v
python scripts/generate_benchmark_v04.py
python scripts/verify_benchmark_v04.py
python scripts/run_document_root_attestation.py
```

The runner uses deterministic test-only keys derived from fixed labels. This makes the experiment reproducible but is explicitly unsuitable for production. Outputs and SHA-256 hashes are written to results/document_root_attestation/.

## Security boundary and limitations

This experiment tests cryptographic binding and selected lifecycle controls. It does not implement:
- KMS/HSM-backed private-key custody;
- authenticated signer enrollment or independent identity proof;
- durable, atomic, distributed replay-state storage;
- certificate issuance, trust-chain validation or operational key rotation;
- revocation distribution/latency guarantees;
- secure document ingestion, trusted capture or proof that the document contents are truthful;
- cross-system transactional enforcement.

A valid signature proves that the holder of the corresponding private key signed the bound payload. It does not prove that the source document itself is genuine or factually correct. If the trusted document-root signing key is compromised, the attacker can sign forged evidence; the experiment makes this failure mode explicit.

The synthetic tenant-demo identifier is not a real tenant-isolation implementation. The caller must supply the expected tenant and case from an independently authenticated authorization context. Replay protection is only process-local in this experiment; production requires atomic durable storage and concurrency-safe nonce consumption.

No result should be represented as production security, real customs-system validation or cryptographic proof of document truth.
