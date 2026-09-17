# Reproducibility Guide

## Scope

This repository contains a deterministic synthetic benchmark plus stochastic/adversarial experiments. Experiment 3 adds a provider-neutral contract for real-model outputs but does not include real-model results until such runs are completed.

## Minimum environment

- Python 3.10+
- dependencies from `requirements.txt`
- repository root as working directory

## Deterministic benchmark regeneration

```bash
python scripts/generate_benchmark.py
python scripts/verify_benchmark.py
```

Expected manifest for benchmark v0.3:

- seed: 42
- unique underlying states: 500
- paired cases: 1000
- unique fingerprints: 500

Any mismatch should be treated as a reproduction failure until explained.

## Existing result reproduction

```bash
python scripts/reproduce_tables.py
```

The script should reproduce the repository's published summary tables from committed result artifacts. If a figure/table cannot be regenerated from code plus committed artifacts, that table should be labeled archival rather than reproducible.

## Experiment 3 preparation

```bash
python experiments/exp3_real_models/build_blinded_cases.py
```

The generated model-facing JSONL must not contain:

- `ground_truth`;
- `fault`;
- `safe_to_act`.

Before external calls, create a run manifest containing:

```text
experiment_version
benchmark_commit_sha
prompt_version
prompt_hash
parser_version
provider
model_family
model_id
role
verifier_slot
temperature
seed
max_retries
run_start_utc
run_end_utc
```

## Experiment 3 output preservation

Save one JSON object per model call using `experiments/exp3_real_models/output_schema.json`.

Never retain only parsed fields. Preserve the raw model response used to derive them.

Parsing failures must remain in the dataset and be reported; do not silently drop them.

## Experiment 3 evaluation

```bash
python experiments/exp3_real_models/evaluate_outputs.py \
  --outputs path/to/model_outputs.jsonl
```

The evaluator writes case-level results and an aggregate summary under `results/exp3/` by default.

## Independence labeling

Model-family identity is preserved as a dependency grouping signal. This is intentionally conservative:

- same family != independent;
- different family != guaranteed independent;
- shared training data, tools, retrieval systems, prompts, or infrastructure may still create dependence.

Any stronger independence claim requires a separate operational definition and experiment.

## Zero-failure reporting

A zero observed failure count is not a zero failure probability. Report denominators and an uncertainty interval or upper confidence bound.

## Versioning rule

If prompts, parsers, controller thresholds, benchmark construction, model choices, or evaluation metrics change after final holdout inspection, increment the experiment version and use an untouched holdout where possible.

## Artifact checklist for a publishable run

A publishable run should contain all of the following:

- benchmark commit SHA;
- blinded-case hash/manifest;
- prompt templates and hashes;
- model/version identities;
- raw responses;
- parsed outputs;
- retry/error logs;
- case-level evaluation table;
- aggregate metrics;
- code commit SHA;
- analysis script version;
- documented exclusions, if any;
- cost and latency summary;
- negative results and failed conditions.
