# Recovered C0–C14 Experiment 3 — separate implementation track

This directory is deliberately separate from `experiments/exp3_real_models/`, which implements the later generated 700-case v0.4 harness. It preserves the recovered Notion C0–C14 protocol rather than relabeling or merging the two experiments.

## What is now staged

- `dry_run_manifest_v2.json`: versioned 28-call route table. Historical provider code Mistral is replaced by Z.ai GLM-4.7-Flash under code Z. The original v1 manifest remains unchanged.
- `routing_cases_v0.json`: recovered six disposable DR-01…DR-06 case packets from the original Notion Dry-Run Suite v0; diagnostic expected actions are separated from model-facing prompt fields.
- `primary_run_manifest_v2_draft.json`: 630-call operational draft with explicit role/family routing and fixed randomization seed. It preserves the 90/90/90/180/180 stage totals.
- `validate_manifest.py` and `validate_primary_manifest.py`: offline structural validators only.

## Important reconciliation stop

The sources define two separate, complementary dry-run tracks, not one mismatched case bank. The 28-call routing manifest uses DR-01…DR-06 to exercise same-family verification, cross-family routing, heterogeneous verifier pairs and one recovery route. The companion mechanical suite uses DRY-01…DRY-06 to test clean proposer output, evidence recovery, conflicts, stale authorization, transport retries and parser behavior. There is no source-defined row-by-row mapping between these namespaces, and none is needed: keep them separate and validate both. The original DR-01…DR-06 input packets have now been recovered from Dry-Run Suite v0. The separate DRY-01…DRY-06 suite remains the mechanical parser/retry/recovery test track.

The companion DRY suite requires its own ledger records: provider proposer/verifier/recovery calls plus adapter-level transport-failure injection and local parser tests. These are additional mechanical checks, not extra rows to silently append to the frozen 28-call routing manifest.

## Frozen protocol anchors

- Frozen protocol: https://app.notion.com/p/3de0a218bb3d8117a22cf31b037d5306
- Prompt Pack v1: https://app.notion.com/p/3de0a218bb3d81689cfdfb876d2051c7
- Execution Harness Contract v1: https://app.notion.com/p/3de0a218bb3d81898fded057b1e38aad
- Dry-Run Manifest v1: https://app.notion.com/p/3de0a218bb3d81699d46e0b0ded894f3
- Dry-Run Suite v1: https://app.notion.com/p/3de0a218bb3d81809b81eac644a88579
- Frozen Case Registry: https://app.notion.com/p/e1ff577dc3fc41a392d3bf9e77dbf905

## Zero-spend rules

No API calls are made by these files. No account-level free entitlement is assumed. Do not activate billing, add prepaid credits, enable paid overages, or configure automatic paid fallback. The provider account's actual quota and billing state must be checked locally before any smoke test. Secrets belong only in local environment variables and must never be committed or pasted into chat.

## Validation

Run from this directory:

```bash
python -m unittest -v
python dry_run_suite.py
python validate_manifest.py
python validate_primary_manifest.py
python runner.py --manifest routing --plan-only
python runner.py --manifest primary --plan-only
```

A PASS means only that the JSON route table is internally consistent. It does not mean the six dry-run scenarios are reconciled, provider accounts are Free, smoke tests passed, or any experiment has executed.


## Current implementation boundary

The offline core is now in place: prompt templates based on Prompt Pack v1, deterministic prompt hashing, strict one-pass JSON parsing, role-specific required-key checks, and a plan-only manifest interface. The six DRY checks are explicitly disposable and do not enter the scored registry.

The case registry does not contain a reversibility-description field even though the frozen Prompt Pack requires one. The public export therefore does not fabricate it, and prompt rendering hard-stops on the missing field. The transport adapter, append-only raw-response ledger, deterministic evidence-feature mapper, and plan-only runner are implemented. Historical B1–B8 policy source has now been recovered and documented in `CONTROLLER_RECOVERY.md`; the C0–C14-specific mapping remains blocked because the frozen prompts/registry do not expose all required historical inputs and do not specify every threshold/tie rule. No model calls have been made.


## Primary 630-call draft interpretation

The v2 draft makes two underspecified role assignments explicit rather than silently guessing: 3B and 3C use V1 as the single verifier; 3E assigns V1 to the next family and V2 to the remaining family in the A→B→C→A rotation. This is a proposed operational interpretation requiring a freeze before scored execution. It is not a modification of the frozen Notion v1 manifest.

## Current gates

- [x] Recover all 30 frozen C0–C14 LOW/HIGH cases.
- [x] Recover all six disposable DR-01…DR-06 routing fixtures.
- [x] Preserve the original 28-call order and add a zero-cost replacement provider slot.
- [x] Draft a 630-call manifest with explicit role/family assignments and fixed random seed.
- [x] Add offline prompt/parser/schema core and disposable mechanical checks.
- [x] Add CI coverage for both the existing 700-case v0.4 harness and this separate C0–C14 track.
- [x] Separate model-facing case packets from pair/condition metadata and recovery targets; add regression tests against prompt leakage.
- [x] Recover source-backed reversibility wording for 18/30 cases; leave 12 unresolved rather than infer reversibility from consequence.
- [x] Audit source-backed reversibility for all 30 cases; retain 12 unspecified values as null/UNKNOWN rather than infer them. A versioned amendment draft now proposes how to expose UNKNOWN without dropping cases.
- [ ] Freeze the 3B/3C/3E role interpretation in a versioned protocol amendment.
- [x] Implement direct-provider request adapters and API-free contract tests.
- [x] Implement deterministic explicit-field feature mapping and fail-closed tests.
- [x] Add a plan-only runner for 28-call and 630-call manifests; actual execution is hard-blocked.
- [x] Recover the historical B1–B8 executable policy functions and thresholds from `src/core.py`; record their exact ordered rules and source hash in `CONTROLLER_RECOVERY.md`.
- [x] Select and implement an explicit C0–C14 B1–B8 operational mapping in `controllers_v1.py`; thresholds, vote set, verifier designation, risk mapping and B8 precedence are versioned and documented in the amendment draft.
- [x] Add controller boundary, malformed-input, false-reject, UNKNOWN and precedence tests in `test_controllers_v1.py`; add the suite to CI.
- [ ] Review/freeze the selected operational defaults, Prompt Pack v2 and Statistical Analysis Plan v2 together before scored execution.
- [ ] Verify all three provider accounts are Free with no paid fallback.
- [x] Recover all six disposable DR-01…DR-06 routing payloads in `routing_cases_v0.json`.
- [x] Run the separate DRY-01…DRY-06 offline mechanical checks in CI.
- [ ] Complete provider-level end-to-end validation of the 28-call route; no provider calls have been made.
- [ ] Freeze hashes and execute the 630-call scored matrix only after every gate passes.

No external model calls have been made. No API spend or billing activation has occurred.


The adapters are deliberately not invoked by CI. They require local credentials and a separately verified account entitlement. The current code has no scored-run execution command, and the B1–B8 decision policies remain blocked pending recovery of their exact frozen rules.


Provider configuration uses canonical family labels A/B/C (Gemini/GLM/GPT-OSS). The disposable 28-call routing manifest retains its historical G/Z/O labels; the adapter normalizes G→A, Z→B and O→C without changing provider/model identity.


## Controller recovery finding

The exact historical controller functions are preserved in `src/core.py` (source blob SHA recorded in `CONTROLLER_RECOVERY.md`). The historical thresholds are 0.90 for B2/B5/B7, and 0.94/0.75 for B6. Historical B8 has an ordered rule set over source-document completeness/agreement, authorization freshness, external measurement conflict, extraction match, verifier rejection/dependency diversity and provenance integrity.

This source does not, by itself, define a valid C0–C14 adapter: the frozen real-model prompts expose different fields and omit some positive evidence attestations. The frozen Experiment 3 text also describes B3/B6 differently from the historical function names. No controller scores will be generated by pretending these mappings are equivalent. A versioned protocol amendment is required before scored execution.


## Reversibility source reconciliation

The frozen registry's Task, Evidence Packet and Recovery Target fields provide explicit reversibility statements for 18 cases. These have been added to the model-facing case packets with their source-linked basis retained in `reversibility_assessment_v1.json`. Twelve cases remain null in the prompt payload because their frozen source does not explicitly establish reversibility. The HIGH consequence label is not treated as proof of irreversibility, and LOW is not treated as proof of reversibility.

This is an additive source-reconciliation artifact; the frozen Notion registry and protocol were not edited. The primary run remains blocked until the 12 unresolved cases are clarified through a versioned protocol amendment or source recovery.


## Current scored-run blockers

- 12/30 cases still have no explicit reversibility statement in their frozen source. They remain null in model-facing inputs.
- The frozen Experiment 3 protocol does not fully specify every operational detail for B2/B3/B5/B6/B7/B8. A versioned operational mapping is now implemented in `controllers_v1.py`; the selected defaults and source-vs-proposal distinction are documented in `CONTROLLER_PROTOCOL_AMENDMENT_v1_DRAFT.md`. Review/freeze remains required before scoring.
- These are protocol/specification blockers, not software test failures. The harness remains plan-only and no model calls have been made.


## Controller protocol amendment draft

`CONTROLLER_PROTOCOL_AMENDMENT_v1_DRAFT.md` is an additive proposal, not a freeze. It separates historical source facts from proposed operational rules, specifies candidate B1–B8 behavior, proposes explicit tri-state evidence attestations for Prompt Pack v2, and retains the 12 reversibility-unknown cases as UNKNOWN. The frozen Notion protocol and Prompt Pack v1 are unchanged. Do not implement the proposed controller semantics or execute scored calls until the amendment is reviewed, approved, tested and frozen.

## Dry-run status correction

The six disposable DR-01…DR-06 routing payloads are recovered. The 28-call dry-run remains blocked for provider/account qualification and end-to-end adapter acceptance, not for missing routing payloads. The separate DRY-01…DRY-06 suite is offline mechanical testing and does not count as provider-call acceptance.


## Companion protocol drafts (not frozen)

- `CONTROLLER_PROTOCOL_AMENDMENT_v1_DRAFT.md`: proposed deterministic B1–B8 mapping and UNKNOWN behavior.
- `PROMPT_PACK_v2_DRAFT.md`: proposed tri-state evidence attestations and explicit unknown-reversibility rendering.
- `STATISTICAL_ANALYSIS_PLAN_v2_DRAFT.md`: proposed reporting of the 12 UNKNOWN cases and versioning requirements.

These drafts are coupled: they must be reviewed and frozen together. Prompt Pack v1 and Statistical Analysis Plan v1 remain authoritative until that happens. The current provider dry-run manifest predates Prompt Pack v2; if v2 is approved, generate a new versioned dry-run manifest and rerun provider acceptance with the frozen v2 prompt hashes before scored execution.


## Deterministic controller implementation

- `controllers_v1.py` implements B1–B8 as pure deterministic functions under version `E3-B1-B8-v1.0.0`.
- B2 uses proposer self-confidence with the recovered 0.90 threshold; invalid confidence defers.
- B3 uses exact normalized majority vote across proposer, V1 and V2; absent/invalid votes abstain; no 2-of-3 majority yields VERIFY.
- B5 uses the selected 0.75–0.90 confidence band (DEFER below 0.75; VERIFY from 0.75 to below 0.90; ACT at/above 0.90).
- B6 designates V1 as the authorization verifier and requires explicit supported authorization plus V1 acceptance.
- B7 uses HIGH→VERIFY; LOW uses the 0.90 proposer-confidence threshold; unknown consequence escalates.
- B8 uses ordered tri-state evidence statuses, exact verbatim packet excerpts, and the source reversibility field. It cannot convert a null source reversibility value into a positive attestation. A lone top-level verifier false-reject boolean does not override otherwise source-grounded typed evidence.
- Dedicated tests are wired into CI. These are offline policy tests only; they do not authorize model calls.
