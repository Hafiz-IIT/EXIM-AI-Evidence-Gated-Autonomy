# Experiment 3 — Frozen Real-Model Evaluation Protocol

## Status

Harness and blinded task preparation implemented. **No external model/API experiment has been run or claimed.** The current real-model study uses Evidence Gate v1 only. A separately labeled reconstruction of the archived v2/v3 behavior now reproduces the recovered deterministic artifacts, but it is not treated as the historical source or silently substituted into this model study.

## Frozen design

- Benchmark: generated v0.4, 700 HIGH-risk cases across 14 synthetic failure families.
- Split unit: underlying pair ID, so paired LOW/HIGH records cannot cross splits.
- Split: deterministic SHA-256 ordering within each family; 30/50 pairs development, 10/50 validation, 10/50 final holdout.
- Model-facing data: only rendered source documents, visible external observations, authorization timing and action consequence. No family, severity, fault, oracle truth, safe_to_act, pair ID or original case ID is sent. Task IDs use a fresh per-preparation secret salt; the salt and case mapping stay in the private directory, while the public manifest contains only the salt hash.
- Layout conditions: canonical development, table validation, canonical final-holdout ID, and a distinct held-out OOD rendering of the same final-holdout cases.
- Model roles: extractor, verifier A, verifier B.
- Conditions: same-model self-verification, same-family multi-model verification where available, cross-family verification, and a model-family holdout condition using a family reserved exclusively for final holdout. Each verifier's configured model ID and family label is preserved.
- Controller: Evidence Gate v1 only until exact historical v2/v3 source is recovered. The v1 gate receives model-generated extraction and verifier results; source documents and external observations remain benchmark-visible.
- Model family IDs are diversity labels, not proof of independent training, ownership, data, tools or infrastructure.

## Provider adapter

The runner supports OpenAI-compatible Chat Completions endpoints. The freeze helper rejects placeholder model IDs, requires the holdout model family to be unique among configured families, and prevents a holdout-only model from appearing in development/validation conditions. The optional cost estimator uses prompt-character/4 input-token approximations and max_tokens output bounds; set per-model token prices and a max_estimated_cost_usd budget to block a run before any API calls if its conservative estimate exceeds the budget. Each model is configured with an exact provider, base URL, model/version string, family ID, and the name of an environment variable containing its API key. Secrets are never stored in the config or run manifest. Run `scripts/estimate_exp3_cost.py` before provider calls; the runner repeats the configured budget check before making calls. Non-compatible providers require an explicit adapter; no provider is silently assumed.

## Required model-facing schemas

Extractor:
- quantity, gross_weight, hs, confidence, missing_fields, uncertainties.

Verifier:
- accept, confidence, reason_codes.

Invalid or unparseable responses fail closed: extraction fields become null and verifier accept becomes false, and any provider or schema failure forces ESCALATE. Raw responses, prompt hashes, model identity, usage, latency, retry history, provider failures and available cost metadata are saved. Provider failures are recorded separately from transient retry errors.

## Execution stages

1. Generate and integrity-check benchmark v0.4.
2. Run blinded task preparation and verify no forbidden oracle/identity fields appear in public tasks.
3. Development pilot only: inspect schema/operational failures, not final-holdout outcomes.
4. Freeze prompts, provider/model/version identities, conditions, settings, benchmark hash, task-manifest hash, public-task hash, salted task-ID hash, split assignment, and retry policy.
5. Run validation; any prompt or controller change after validation requires a new protocol version and fresh holdout.
6. Run the complete final-holdout ID and OOD sets once with the frozen configuration. Partial final-holdout runs are prohibited. A non-empty final-holdout output directory cannot be reused, preventing accidental reruns of the same frozen holdout.
7. Persist raw responses before evaluation; evaluate against the private map only after responses are saved.

## Required artifacts

- run_manifest.json;
- task_manifest.json and public tasks hash;
- exact provider/model/version identities;
- prompt versions and SHA-256 hashes;
- raw_responses.jsonl;
- case_results.csv and summary.json;
- retry_errors.jsonl and provider_errors.jsonl;
- latency, token usage and cost where returned;
- exclusions and parser failures.

## Metrics

HIGH-risk incorrect consequential action rate (unsafe ACT / all HIGH-risk cases), false authorization, false-block rate among safe cases, coverage, escalation rate, extraction exact-match, verifier co-failure conditional on wrong extraction, model-family co-failure, latency and estimated cost. Zero observed unsafe actions must be reported with an uncertainty interval; it is not proof of safety.

## Holdout guard

Final-holdout execution requires:
- explicit CLI confirmation;
- freeze.status=frozen and a non-empty frozen_at timestamp;
- matching benchmark, prompt, task-manifest, public-task, salted task-ID and model/condition configuration hashes;
- no max-tasks truncation.

## Limitations

All benchmark cases and source documents are synthetic. This study evaluates model outputs on a controlled testbed; it does not validate real customs workflows, production security, or the independence of model families. The OOD rendering is a synthetic wording/layout shift, not a real scanned-document distribution.

Before estimating or running any model, the harness verifies the hashes of the public task file, task manifest, private evaluation map and private task-ID salt, and checks that public/private task IDs form an exact one-to-one mapping. The final-holdout freeze also binds the private evaluation-map hash.
