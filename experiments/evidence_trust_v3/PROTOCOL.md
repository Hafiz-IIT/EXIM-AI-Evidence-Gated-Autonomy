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

The deterministic HIGH-risk benchmark v0.4 subset is reused. Outputs are a separate v3 result set and do not overwrite v2 artifacts or historical results. In the pre-capture source-forgery scenario, the document set is changed relative to the unchanged physical ground truth and the transformed case is relabeled unsafe-to-authorize. Safe-action coverage and false-block rate are therefore undefined for that scenario; the relevant metric is whether the policy issues any unsafe ACT.

## Interpretation

A 2-of-3 quorum is expected to tolerate one compromised witness only when the other two provide valid, independent, matching evidence. Two compromised witnesses can control a 2-of-3 quorum. A forged credential should fail under an uncompromised pinned registry key. Source forgery before capture is a distinct threat: the identity credential may still be valid, so detection depends on the independent witness disagreeing with the forged document interpretation. Shared administrative-domain labels should fail the declared independence check. The controller's independent-measurement input is populated only from a successfully verified quorum; it must not fall back to the benchmark's untouched measurement when quorum verification fails.

A registry signature proves that the pinned issuer signed a credential binding a key to identity claims. It does **not** prove that the source physically exists, that the acquisition channel is honest, or that the claimed administrative domains are genuinely independent. Those require external identity proofing, governance, audits, and operational controls.

## Quorum verification invariants

The verifier enforces the configured witness roster size and distinct witness IDs. It then groups only assertions that match the controller's expected measurement and checks witness ID, key ID, source ID, acquisition domain, and administrative domain independence within each matching group. A dissenting or non-matching witness cannot contribute an independence claim to the supporters. Invalid credentials can be excluded, but the remaining matching supporters must still satisfy the threshold and all independence checks.

## Bounded recovery from verifier false rejection

The v3 controller may recover an isolated machine-verifier false rejection only after a valid 2-of-3 witness quorum confirms the interpreted measurement. Recovery is allowed only when every earlier v1 guard passes: complete documents, present and fresh authorization, cross-document agreement, no external measurement conflict, extraction matching the invoice, valid provenance, no duplicate document kind, and at least two independent machine-verifier dependency groups. The only overridden condition is one or more machine verifiers rejecting despite those other checks passing. This is not a general override for verifier disagreement and cannot bypass missing evidence, stale authorization, provenance failures, document conflicts, extraction mismatch, or a failed witness quorum.

The recovery policy is tested against all eight v3 threat scenarios. Results report the number of recoveries separately. Because the benchmark's C7 family is deliberately labeled as a false-reject case, any improved coverage there is a benchmark-specific result, not evidence that real-world verifier rejections are generally safe to override.

## Threshold sensitivity: 2-of-3 versus 3-of-3

The runner evaluates the same signed assertions twice: the primary 2-of-3 policy and a strict 3-of-3 sensitivity policy. Both use the same bounded verifier-false-reject recovery rule and the same synthetic cases. The comparison isolates the effect of requiring unanimity among the three enrolled witnesses. A 3-of-3 quorum is expected to block a two-witness collusion when the third honest witness disagrees, but it also loses availability when any credential is invalid or the trust anchor is compromised. Three compromised witnesses can still authorize a jointly fabricated measurement. These are benchmark-specific deterministic comparisons, not universal threshold recommendations.

## Pre-registered acceptance profile

The deterministic runner includes assertions for the following expected ACT / unsafe-ACT counts (out of 700 cases per scenario). These are executable regression expectations, not empirical probability estimates.

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

The 100 honest ACTs comprise 50 clean cases plus 50 deliberately constructed safe cases with isolated verifier false rejection (C7), recovered only after a valid witness quorum and all other policy guards pass. The 50 unsafe ACTs in two-witness collusion, full-roster compromise and registry-root compromise arise in C4 consistent-but-wrong. Strict 3-of-3 blocks the two-witness and registry-root scenarios in this fixture, but cannot defend against compromise of all three enrolled witnesses. It also loses availability when one credential is invalid, as shown by the forged-source-identity control. CI must fail if these deterministic acceptance profiles drift.

## Claim boundary

All keys, identities, measurements and source records are synthetic. Deterministic benchmark counts are not real-world probabilities. The implementation does not provide production CA governance, KMS/HSM custody, hardware-backed device identity, secure enrollment, trusted time, durable distributed revocation, or proof of operational independence. Results must not be described as production security validation.

## Reproduction

```bash
python -m unittest tests.test_evidence_trust_v3 -v
python scripts/run_evidence_trust_v3.py
```
