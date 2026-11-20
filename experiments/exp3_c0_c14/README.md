# Recovered C0–C14 Experiment 3 — separate implementation track

This directory is deliberately separate from `experiments/exp3_real_models/`, which implements the later generated 700-case v0.4 harness. It preserves the recovered Notion C0–C14 protocol rather than relabeling or merging the two experiments.

## What is now staged

- `dry_run_manifest_v2.json`: versioned 28-call route table. Historical provider code Mistral is replaced by Z.ai GLM-4.7-Flash under code Z. The original v1 manifest remains unchanged.
- `validate_manifest.py`: offline structural validator only. It makes no network requests and no model calls.

## Important reconciliation stop

The sources define two separate, complementary dry-run tracks, not one mismatched case bank. The 28-call routing manifest uses DR-01…DR-06 to exercise same-family verification, cross-family routing, heterogeneous verifier pairs and one recovery route. The companion mechanical suite uses DRY-01…DRY-06 to test clean proposer output, evidence recovery, conflicts, stale authorization, transport retries and parser behavior. There is no source-defined row-by-row mapping between these namespaces, and none is needed: keep them separate and validate both. The route manifest remains blocked because the source materials recovered so far do not supply the actual DR-01…DR-06 input packets, and provider account Free status is unverified.

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

Run:

```bash
python validate_manifest.py
```

A PASS means only that the JSON route table is internally consistent. It does not mean the six dry-run scenarios are reconciled, provider accounts are Free, smoke tests passed, or any experiment has executed.


## Current implementation boundary

The offline core is now in place: prompt templates based on Prompt Pack v1, deterministic prompt hashing, strict one-pass JSON parsing, role-specific required-key checks, and a plan-only manifest interface. The six DRY checks are explicitly disposable and do not enter the scored registry.

The case registry does not contain a reversibility-description field even though the frozen Prompt Pack requires one. The public export therefore does not fabricate it, and prompt rendering hard-stops on the missing field. The transport adapter, append-only raw-response ledger, deterministic evidence-feature mapper, and B1–B8 controller evaluator are still outstanding. No model calls have been made.
