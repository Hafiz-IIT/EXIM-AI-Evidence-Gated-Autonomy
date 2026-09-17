# Experiment 3 — Real-Model Evaluation

**Status:** executable scaffold and frozen evaluation contract. No real-model results are claimed in this directory until provider outputs are collected and committed under the protocol below.

## Research question

Do evidence-gated authorization policies retain their relative safety/coverage advantages when synthetic machine-error probabilities are replaced by actual model outputs, especially when verification is performed by the same model family versus independently developed model families?

## Integrity boundary

This experiment must not reuse test-set outcomes to tune controller thresholds, prompts, parsing rules, verifier rubrics, or model selection. Any post-hoc change creates a new experiment version and requires a fresh holdout.

## Required conditions

1. **Same-family self-verification** — extractor and verifier from the same model family.
2. **Cross-family verification** — extractor and verifier from independently developed model families.
3. **Two-verifier condition** — at least two verifier outputs, with model-family identity preserved rather than relabeled as independent.
4. **Model-family holdout** — at least one family excluded from any development/prompt debugging and used only for final evaluation when feasible.
5. **Format/OOD condition** — document wording/layout perturbations fixed before the final run.

## Files

- `output_schema.json` — provider-neutral record schema for saved model calls.
- `build_blinded_cases.py` — converts benchmark cases into model-facing tasks while removing ground truth and fault labels.
- `evaluate_outputs.py` — joins frozen benchmark truth with saved model outputs and computes extraction error, verifier co-failure, authorization outcomes, and coverage.
- `EXPERIMENT_FREEZE.md` — fields that must be frozen before any final test run.

## Workflow

```bash
python scripts/generate_benchmark.py
python experiments/exp3_real_models/build_blinded_cases.py
# Run model calls with an external runner/provider, saving one JSONL record per call.
python experiments/exp3_real_models/evaluate_outputs.py --outputs path/to/model_outputs.jsonl
```

## Output retention

Every external call used in the final analysis must retain:

- case ID and role;
- provider, model family, exact model/version identifier;
- prompt-template version and prompt hash;
- raw response text;
- parsed response;
- timestamp;
- latency;
- retry count;
- sampling parameters;
- monetary cost when non-zero or known.

Do not commit API keys, private credentials, private client documents, or proprietary prompts that cannot be redistributed.

## Primary endpoints

- high-risk incorrect consequential action rate (ICAR);
- false authorization rate;
- false blocking rate;
- same-family vs cross-family verifier co-failure;
- coverage/action rate;
- escalation/verification/request rates;
- extraction field error rate;
- latency and monetary cost.

## Claim boundary

Passing this experiment would still not establish production safety. It would only show how the frozen controllers behave on this benchmark when a defined set of real model families replaces the synthetic machine-error generator.