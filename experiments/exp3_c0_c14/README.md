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
- [ ] Source explicit reversibility descriptions for the 30 scored cases; do not infer them.
- [ ] Freeze the 3B/3C/3E role interpretation in a versioned protocol amendment.
- [x] Implement direct-provider request adapters and API-free contract tests.
- [x] Implement deterministic explicit-field feature mapping and fail-closed tests.
- [x] Add a plan-only runner for 28-call and 630-call manifests; actual execution is hard-blocked.
- [x] Recover the historical B1–B8 executable policy functions and thresholds from `src/core.py`; record their exact ordered rules and source hash in `CONTROLLER_RECOVERY.md`.
- [ ] Freeze a versioned C0–C14-specific mapping for B1–B8. Historical B3/B6/B8 inputs are not semantically interchangeable with the frozen real-model prompt outputs; missing freshness/provenance/reversibility fields must not be guessed.
- [ ] Verify all three provider accounts are Free with no paid fallback.
- [ ] Complete the 28-call provider dry run and separate DRY-01…DRY-06 mechanical suite.
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
