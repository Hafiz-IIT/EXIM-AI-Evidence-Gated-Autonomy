# Evidence-Trust Architecture v3 — Independent Witness Quorum

**Status:** Implemented as a synthetic executable experiment and subject to CI validation. This is not production PKI or evidence of real-world source independence.

## Research question

Can a threshold of multiple witnesses reduce the unsafe-authorization exposure observed when a single witness authority is compromised in v2, and what does cryptographic source-identity enrollment actually establish?

## Changes from v2

- Three witness identities are enrolled by a pinned synthetic registry root.
- Each registry-signed credential binds witness ID, key ID, public-key bytes, source ID, acquisition domain, administrative domain, tenant, serial, and validity window.
- Each witness signs a case-scoped measurement assertion bound to its credential digest and evidence parent.
- Authorization requires two matching assertions from at least two distinct witness IDs, key IDs, source IDs, acquisition domains, and administrative domains. Independence is evaluated on the matching supporters themselves; a dissenting third witness cannot lend independence to a colluding pair.
- The configured roster must contain exactly three distinct witness IDs; up to one invalid credential can be tolerated only if two remaining valid, independent witnesses form the matching quorum. Repeated entries or a missing roster member cannot increase the number of independent supporters.
- A credential cannot be edited to claim a different source or key without invalidating the registry signature.

## Prespecified threat scenarios

1. Honest three-witness baseline.
2. One witness compromised.
3. Two witnesses compromised.
4. All three witnesses compromised.
5. Forged source-identity credential (credential-body tampering without a valid registry signature).
6. Source forgery before capture, separately from signer/credential compromise.
7. Disclosed shared administrative domain.
8. Registry-root compromise, treated as a trust-anchor failure rather than a routine witness failure.

The deterministic HIGH-risk benchmark v0.4 subset is reused. Outputs are a separate v3 result set and do not overwrite v2 artifacts or historical results.

## Interpretation

A 2-of-3 quorum is expected to tolerate one compromised witness only when the other two provide valid, independent, matching evidence. Two compromised witnesses can control a 2-of-3 quorum. A forged credential should fail under an uncompromised pinned registry key. Source forgery before capture is a distinct threat: the identity credential may still be valid, so detection depends on the independent witness disagreeing with the forged document interpretation. Shared administrative-domain labels should fail the declared independence check. The controller's independent-measurement input is populated only from a successfully verified quorum; it must not fall back to the benchmark's untouched measurement when quorum verification fails.

A registry signature proves that the pinned issuer signed a credential binding a key to identity claims. It does **not** prove that the source physically exists, that the acquisition channel is honest, or that the claimed administrative domains are genuinely independent. Those require external identity proofing, governance, audits, and operational controls.

## Quorum verification invariants

The verifier enforces the configured witness roster size and distinct witness IDs. It then groups only assertions that match the controller's expected measurement and checks witness ID, key ID, source ID, acquisition domain, and administrative domain independence within each matching group. A dissenting or non-matching witness cannot contribute an independence claim to the supporters. Invalid credentials can be excluded, but the remaining matching supporters must still satisfy the threshold and all independence checks.

## Claim boundary

All keys, identities, measurements and source records are synthetic. Deterministic benchmark counts are not real-world probabilities. The implementation does not provide production CA governance, KMS/HSM custody, hardware-backed device identity, secure enrollment, trusted time, durable distributed revocation, or proof of operational independence. Results must not be described as production security validation.

## Reproduction

```bash
python -m unittest tests.test_evidence_trust_v3 -v
python scripts/run_evidence_trust_v3.py
```
