# Evidence-Trust Architecture v4 — Dependency-Root-Aware Witness Independence

**Status:** Synthetic executable experiment. This is not production PKI or proof of real-world independence.

## Research question

Can explicit dependency-root declarations distinguish genuinely disjoint witness dependencies from witnesses that merely have different keys, source IDs, acquisition labels, or administrative labels? Does requiring a conflict-free subset of matching witnesses improve resistance to common-control and common-measurement attacks without unnecessarily rejecting a quorum when an independent subset exists?

## Motivation from prior work

The v3 review identifies that independent corroboration is not new and that independence is relative to relevant interests and shared influences. The v3 design checks distinct values in a small number of identity fields, but does not detect a parent company, identity provider, key-management root, acquisition pipeline, or physical measurement source shared beneath those labels.

v4 represents those dependencies explicitly in a registry-signed credential. It does not claim the declarations are true: a registry signature authenticates the issuer's signed statement, not the real-world ownership or architecture. See RELATED_WORK_AND_NOVELTY.md.

## Credential model

Each v4 credential binds the witness ID and key ID, source ID, acquisition domain, administrative domain, tenant, validity interval, serial, public key, and five required dependency-root sets:

1. parent_control
2. identity_provider
3. key_management
4. acquisition_pipeline
5. measurement_source

Each dependency layer must be present and non-empty. Values are canonicalized as sorted unique identifiers. Missing or malformed layers fail credential verification.

## Quorum rule

The verifier first validates each registry-signed credential and case-scoped witness assertion, then groups assertions that match the expected measurement. It searches for a subset of the required threshold whose members:

- have distinct witness IDs, key IDs, source IDs, acquisition domains, and administrative domains; and
- have pairwise disjoint declared dependency-root sets in every required dependency layer.

A dissenting witness cannot lend independence to matching supporters. Conversely, a non-independent pair need not poison a larger matching group if another conflict-free subset of the required size exists. The runner compares this graph-aware policy with a field-only ablation that ignores dependency roots.

## Scenarios

The same HIGH-risk benchmark v0.4 cases are run under these scenarios:

1. Honest baseline.
2. One witness compromised.
3. Two witnesses compromised.
4. All three witnesses compromised.
5. Forged source-identity credential.
6. Source forgery before capture (transformed cases are unsafe-to-authorize; safe coverage is undefined).
7. Shared administrative domain.
8. Registry-root compromise.
9. Shared parent-control root with distinct child administrative domains.
10. Shared identity provider.
11. Shared physical measurement source.
12. Shared acquisition pipeline.
13. Two compromised witnesses sharing a parent-control root while the third witness is independently administered.

The output compares three policies on each scenario: field-only 2-of-3, dependency-aware 2-of-3, and dependency-aware 3-of-3.

## Interpretation boundaries

- Dependency-root-aware quorum can detect only common roots that are declared accurately in credentials.
- A false declaration, omitted dependency, or compromised enrollment authority can defeat the check.
- A shared identity or measurement dependency is a reason not to count those witnesses as independent for this threat model; it does not prove the observations are false.
- Two colluding witnesses with genuinely distinct declared dependency roots can still defeat a 2-of-3 policy.
- Three colluding witnesses can still defeat either threshold if all three share a fabricated measurement and the enrollment root accepts their credentials.
- Registry-root compromise remains a trust-anchor failure; dependency-root distinctness does not solve it.
- All identities, measurements, dependency roots and attacks are synthetic. Deterministic counts are not real-world probabilities or production-security evidence.

## Inspectable outputs

The runner emits three CSV files plus a manifest:

- evidence_trust_v4_cases.csv — one row per benchmark case and scenario, with all three policy decisions.
- evidence_trust_v4_summary.csv — scenario-level security and availability metrics.
- evidence_trust_v4_dependencies.csv — one row per witness and scenario, including the declared dependency-root sets, issuer ID, whether the credential verifies under that scenario's trusted root, and whether the witness is adversarial in that scenario.
- manifest.json — scenario counts, dependency layers, software context, and SHA-256 hashes for all three CSVs.

The dependency CSV is necessary to audit why a particular quorum was or was not considered independent; aggregate counts alone are insufficient.

## Metrics

For each policy and scenario, report:
- ACT count and unsafe ACT count;
- unsafe ACT rate over all cases and conditional on ACT;
- safe-action coverage and false-block rate, where the scenario has safe cases;
- verifier-false-reject recovery count.

For source forgery before capture, transformed cases are unsafe-to-authorize, so safe-action coverage and false-block rate are undefined; the key outcome is zero unsafe ACTs.

## Reproduction

```bash
python -m unittest tests.test_evidence_trust_v4 -v
python scripts/run_evidence_trust_v4.py
```
