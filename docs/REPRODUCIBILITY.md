# Reproducibility Contract

This repository treats reproducibility as part of the research result rather than as optional packaging.

## Current reproducible scope

The following stages are reproducible from repository code and stored summaries:

1. deterministic generation of the synthetic benchmark (`seed=42`, benchmark version `0.3`);
2. benchmark integrity checks;
3. deterministic policy evaluation and summary-table regeneration;
4. stochastic simulation summaries for imperfect verification/review regimes;
5. adversarial provenance/evidence stress tests;
6. attestation and trust-root compromise experiments.

Experiment 3 and the human-review study are not yet reproducible because they have not yet been run.

## Minimal reproduction

```bash
python -m venv .venv
# activate the virtual environment for your platform
pip install -r requirements.txt
python scripts/generate_benchmark.py
python scripts/verify_benchmark.py
python scripts/reproduce_tables.py
```

## Determinism requirements

Any script that contributes a number to the paper must record:

- code commit SHA;
- benchmark version and seed;
- configuration file or command-line arguments;
- random seed(s), where applicable;
- input hashes;
- output hashes;
- software/runtime versions where material.

## Experiment 3 reproducibility requirements

Every real-model call must write an append-only JSONL record containing at least:

- case ID and blinded benchmark split;
- role (`extractor`, `classifier`, `verifier_a`, `verifier_b`);
- provider and exact model identifier;
- model revision/version if exposed by the provider;
- system and user prompt hashes;
- decoding parameters;
- timestamp;
- request ID when available;
- raw response;
- parsed structured response;
- parse success/failure;
- latency;
- token counts and monetary cost when available;
- retry count and failure reason.

The hidden benchmark truth must not be passed to any model call.

## Freeze rule

Before the first held-out Experiment 3 result is inspected, commit:

1. split manifest;
2. prompt templates;
3. parser/schema;
4. controller versions;
5. primary metrics;
6. analysis script;
7. model-family assignment plan.

After test-set inspection, any threshold/prompt/policy modification creates a new experiment version and must be evaluated on a fresh holdout.

## Raw-data policy

Synthetic benchmark records may be regenerated instead of committed when deterministic regeneration is verified. Real-model outputs should be retained when licensing/provider terms permit. If raw outputs cannot be redistributed, publish hashes, schemas, aggregate results, and the exact collection code needed for authorized reproduction.

## Failure visibility

Parse failures, API failures, refusals, timeouts, malformed outputs, and missing values must remain in the run log. They must not be silently dropped. The analysis must report how they are handled.

## Reproduction target

A third party should be able to answer four questions from the repository alone:

1. What exact claim is being tested?
2. What exact data and model outputs produced the result?
3. What exact code transformed those inputs into the reported number?
4. Which assumptions and failure cases remain outside the evidence?
