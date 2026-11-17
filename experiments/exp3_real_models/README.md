# Experiment 3 real-model harness

1. Generate benchmark v0.4 and prepare blinded tasks:
   `python scripts/prepare_exp3_tasks.py --benchmark data/benchmark_v0.4/cases.jsonl --output results/exp3_real_models`
2. Review the frozen protocol and configure exact model identities in `model_config.example.json` (copy to a private config path). Set API credentials only in environment variables.
3. Run a small development pilot:
   `python scripts/run_exp3_real_models.py --config /path/to/private-model-config.json --prepared-dir results/exp3_real_models --split development --condition same_model_self_verification --max-tasks 10`
4. Freeze prompt/config/benchmark hashes before validation and final holdout.
5. Final holdout requires an explicit confirmation flag and exact freeze-hash matches. Partial final-holdout runs are refused.

The adapter supports OpenAI-compatible Chat Completions. It does not create API keys, select paid providers, or make calls in CI. No real-model results are claimed until actual provider responses and run artifacts exist.
