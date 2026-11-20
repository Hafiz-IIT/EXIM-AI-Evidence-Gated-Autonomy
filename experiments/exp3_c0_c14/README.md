# Recovered C0–C14 Experiment 3 — separate implementation track

This directory is deliberately separate from `experiments/exp3_real_models/`, which implements the later generated 700-case v0.4 harness. It preserves the recovered Notion C0–C14 protocol rather than relabeling or merging the two experiments.

## What is now staged

- `dry_run_manifest_v2.json`: versioned 28-call route table. Historical provider code Mistral is replaced by Z.ai GLM-4.7-Flash under code Z. The original v1 manifest remains unchanged.
- `validate_manifest.py`: offline structural validator only. It makes no network requests and no model calls.

## Important reconciliation stop

The original route manifest names its disposable cases DR-01…DR-06. The companion Dry-Run Suite v1 names six mechanical scenarios DRY-01…DRY-06. The suite assigns recovery to DRY-02 and parser-format testing to DRY-06, while the 28-call route ends with a DR-06 recovery call. No source mapping between these identifier systems is specified. The harness must not guess this mapping. Therefore the replacement manifest is marked `BLOCKED_NOT_EXECUTABLE`.

The companion suite also requires transport-failure injection and local malformed-JSON tests beyond the 28 provider-call route. These need their own explicit test records and cannot be represented as successful provider calls by implication.

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
