# Signed Action-Catalog and Executor-Binding Threat Experiment v1

**Status:** Synthetic trust-boundary experiment. No production identity, key-management or external tool service is used.

## Research question

Does binding a proposed action to a locally supplied catalog remain protective if the catalog is modified, stale, aliased, or bypassed between authorization and execution?

## Controls under test

The experiment adds an HMAC-authenticated catalog manifest and a signed authorization envelope. The executor-side check requires the exact authorized action ID and catalog version. The same test key is used by the synthetic authorizer and executor.

## Attack cases

1. Catalog consequence metadata is modified without re-signing.
2. A stale catalog version is presented against a newer expected version.
3. A low-risk action alias is substituted for the trusted high-risk action.
4. The executor is asked to invoke a different action ID from the one authorized.
5. The catalog version changes after authorization but before execution.
6. The authorization envelope is modified after issuance.

## Metrics and interpretation

Report authorization acceptance and executor-binding acceptance by attack class. These are deterministic conformance outcomes, not probabilities, prevalence estimates, or deployment safety rates.

## Reproduction

    python -m unittest tests.test_signed_action_catalog -v
    python scripts/run_signed_action_catalog_threats.py

## Limitations

- HMAC is a test mechanism, not a production PKI or asymmetric signer identity system.
- Key custody, provisioning, rotation, revocation, multi-tenant isolation and replay prevention are not implemented.
- The experiment does not invoke a real external tool; it checks the executor boundary function.
- The trusted expected catalog version and key are assumed to arrive from a trusted runtime.
- No claim is made about production security or real-world incident reduction.
