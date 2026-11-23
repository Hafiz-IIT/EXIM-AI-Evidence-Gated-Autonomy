# Signed Action-Catalog Threats — Results Review v1

**Workflow run:** [45146699519](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/45146699519)  
**Source commit:** `6619ef07b85810b3b36c0f12e527147653903626`  
**Artifact:** [ega-signed-action-catalog-threats-v1](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/45146699519/artifacts/14804433335)  
**Benchmark:** v0.4 HIGH-risk subset  
**Cases per attack class:** 700  
**Study type:** deterministic synthetic trust-boundary conformance test

## Results

| Attack / condition | Authorization accepted | Executor binding accepted |
|---|---:|---:|
| Unmodified baseline | 700/700 | 700/700 |
| Catalog consequence metadata tampering | 0/700 | 0/700 |
| Stale catalog version | 0/700 | 0/700 |
| Action alias / identity substitution | 0/700 | 0/700 |
| Executor tool substitution after authorization | 700/700 | 0/700 |
| Catalog version changed after authorization | 700/700 | 0/700 |

The token is intentionally issued before the executor-substitution and post-authorization-version-change checks. Those rows therefore show why authorization-time validation alone is insufficient: the authorizer accepts the original action, but the executor-side binding check rejects the changed action or version.

## Interpretation

Within this deterministic harness, the HMAC manifest rejects unsigned catalog modification and version mismatch. The signed authorization envelope binds the action ID and catalog version, and the executor check rejects a different invoked action ID or a changed catalog version.

These are conformance outcomes for the implemented functions, not estimated attack success probabilities. The repeated 700-case rows reuse the same benchmark action identity and do not represent 700 independent real-world attacks.

## Limitations

- The HMAC key is a synthetic in-process test key shared by the signer and verifier. It is not managed key custody or production PKI.
- Signer identity, key provisioning, asymmetric signatures, rotation, revocation and replay prevention are not implemented.
- The expected catalog version and key are assumed to be supplied by a trusted runtime.
- The executor boundary is a pure function test. No real tool, external API or side effect is invoked.
- The experiment does not test hidden hooks, argument-dependent side effects, resource aliasing, delegation, semantic rendering, or process-level substitution below the recorded invocation fields.
- It does not establish deployment security or general superiority over existing authorization systems.

## Next experiment

Integrate the binding check at an actual executor boundary and record a canonical action digest covering tool identity, arguments, target resource, tenant, state version and relevant side-effect scope. Add expiry, nonce/replay protection, revocation and signer-identity tests. Compare the resulting threat coverage directly against existing approval-execution binding work, especially Approval Laundering.
