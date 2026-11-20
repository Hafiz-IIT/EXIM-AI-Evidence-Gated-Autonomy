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
```

A PASS means only that the JSON route table is internally consistent. It does not mean the six dry-run scenarios are reconciled, provider accounts are Free, smoke tests passed, or any experiment has executed.


## Current implementation boundary

The offline core is now in place: prompt templates based on Prompt Pack v1, deterministic prompt hashing, strict one-pass JSON parsing, role-specific required-key checks, and a plan-only manifest interface. The six DRY checks are explicitly disposable and do not enter the scored registry.

The case registry does not contain a reversibility-description field even though the frozen Prompt Pack requires one. The public export therefore does not fabricate it, and prompt rendering hard-stops on the missing field. The transport adapter, append-only raw-response ledger, deterministic evidence-feature mapper, and B1–B8 controller evaluator are still outstanding. No model calls have been made.


## Primary 630-call draft interpretation

The v2 draft makes two underspecified role assignments explicit rather than silently guessing: 3B and 3C use V1 as the single verifier; 3E assigns V1 to the next family and V2 to the remaining family in the A→B→C→A rotation. This is a proposed operational interpretation requiring a freeze before scored execution. It is not a modification of the frozen Notion v1 manifest.

## Current gates

- [x] Recover all 30 frozen C0–C14 LOW/HIGH cases.
- [x] Recover all six disposable DR-01…DR-06 routing fixtures.
- [x] Preserve the original 28-call order and add a zero-cost replacement provider slot.
- [x] Draft a 630-call manifest with explicit role/family assignments and fixed random seed.
- [x] Add offline prompt/parser/schema core and disposable mechanical checks.
- [x] Add CI coverage for both the existing 700-case v0.4 harness and this separate C0–C14 track.
- [ ] Source explicit reversibility descriptions for the 30 scored cases; do not infer them.
- [ ] Freeze the 3B/3C/3E role interpretation in a versioned protocol amendment.
- [x] Implement direct-provider request adapters and API-free contract tests.
- [x] Implement deterministic explicit-field feature mapping and fail-closed tests.
- [ ] Recover the exact deterministic B1–B8 controller definitions/thresholds; do not reuse the unrelated v0.4 Evidence Gate.
- [ ] Verify all three provider accounts are Free with no paid fallback.
- [ ] Complete the 28-call provider dry run and separate DRY-01…DRY-06 mechanical suite.
- [ ] Freeze hashes and execute the 630-call scored matrix only after every gate passes.

No external model calls have been made. No API spend or billing activation has occurred.


The adapters are deliberately not invoked by CI. They require local credentials and a separately verified account entitlement. The current code has no scored-run execution command, and the B1–B8 decision policies remain blocked pending recovery of their exact frozen rules.
