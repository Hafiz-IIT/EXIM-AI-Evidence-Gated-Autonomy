# Experiment 3 real-model harness

1. Generate benchmark v0.4 and prepare blinded tasks:
   `python scripts/prepare_exp3_tasks.py --benchmark data/benchmark_v0.4/cases.jsonl --output results/exp3_real_models`
2. Review the frozen protocol and configure exact model identities in `model_config.example.json` (copy to a private config path). Set API credentials only in environment variables.
3. Run a small development pilot:
   `python scripts/run_exp3_real_models.py --config /path/to/private-model-config.json --prepared-dir results/exp3_real_models --split development --condition same_model_self_verification --max-tasks 10`
4. Freeze prompt/config/benchmark hashes before validation and final holdout.
5. Freeze the exact provider/model and prompt/benchmark identities with `python scripts/freeze_exp3_config.py --config /path/to/private-model-config.json --prepared-dir results/exp3_real_models --output /path/to/frozen-config.json`. Final holdout requires an explicit confirmation flag and exact freeze-hash matches. Partial final-holdout runs are refused.

The adapter supports OpenAI-compatible Chat Completions. It does not create API keys, select paid providers, or make calls in CI. No real-model results are claimed until actual provider responses and run artifacts exist.

The CLI entry points explicitly add the repository root to Python's import path so they run both in GitHub Actions and when invoked from a shell. Each preparation run uses a fresh private salt for opaque task IDs; keep `results/exp3_real_models/private/` private. Final-holdout freeze hashes bind the exact task manifest and public task set. Provider or schema failures force ESCALATE and are logged separately from retry errors.

Before setting API keys or running a model, estimate calls and a rough preflight cost estimate without network access:

`python scripts/estimate_exp3_cost.py --config /path/to/private-model-config.json --prepared-dir results/exp3_real_models --splits development validation --output results/exp3_real_models/cost_estimate.json`

Populate each model's input/output USD per 1K token prices. The estimator uses prompt characters/3 for input tokens and the configured `max_tokens` as an output upper bound; it is deliberately conservative and not a provider quote. Set `settings.max_preflight_estimated_cost_usd` in the private config to enforce the same preflight budget in the runner. The freeze hash binds all run settings.

The harness verifies the integrity of both public and private task files before cost estimation or model execution. Do not share `private/evaluation_map.jsonl` or `private/private_metadata.json`; the latter contains the per-preparation task-ID salt.
