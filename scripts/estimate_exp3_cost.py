from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.exp3_real_models.harness import estimate_condition_cost, verify_prepared_package


def main():
    parser = argparse.ArgumentParser(description="Estimate Experiment 3 API calls and a rough preflight cost without making model calls.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--prepared-dir", type=Path, default=Path("results/exp3_real_models"))
    parser.add_argument("--splits", nargs="+", default=["development", "validation"])
    parser.add_argument("--conditions", nargs="*")
    parser.add_argument("--max-budget-usd", type=float)
    parser.add_argument("--output", type=Path, default=Path("results/exp3_real_models/cost_estimate.json"))
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    _, _, public_rows, private_map = verify_prepared_package(args.prepared_dir)
    public_tasks = {row["task_id"]: row for row in public_rows}
    selected = [c for c in config["conditions"] if not args.conditions or c["condition_id"] in args.conditions]
    unknown = set(args.conditions or []) - {c["condition_id"] for c in config["conditions"]}
    if unknown:
        raise SystemExit("unknown condition IDs: " + ", ".join(sorted(unknown)))

    estimates = []
    all_priced = True
    total_cost = 0.0
    for condition in selected:
        for split in args.splits:
            if condition.get("holdout_only") and not split.startswith("final_holdout"):
                continue
            rows = [row for row in private_map if row["split"] == split]
            tasks = [public_tasks[row["task_id"]] for row in rows]
            estimate = estimate_condition_cost(tasks, condition, config)
            estimates.append({
                "condition": condition["condition_id"],
                "split": split,
                **estimate,
            })
            if estimate["cost_known"]:
                total_cost += estimate["preflight_estimated_cost_usd"]
            else:
                all_priced = False

    result = {
        "protocol": "exp3-real-models-v1",
        "status": "estimated_no_model_calls",
        "splits": args.splits,
        "conditions": [c["condition_id"] for c in selected],
        "estimate_method": "rough estimate: ceil(serialized prompt characters / 3) input tokens plus configured max_tokens output cap; provider tokenization and actual usage may differ",
        "cost_known_for_all_selected_runs": all_priced,
        "total_preflight_estimated_cost_usd": total_cost if all_priced else None,
        "max_budget_usd": args.max_budget_usd,
        "runs": estimates,
        "warning": "This is a rough planning estimate, not a guaranteed upper bound or provider quote. Actual tokenization, hidden message overhead, cached-input pricing and output usage may differ. Reconcile against provider-reported usage and billing.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if args.max_budget_usd is not None:
        if not all_priced:
            raise SystemExit("budget check requires input/output token prices for every selected model")
        if total_cost > args.max_budget_usd:
            raise SystemExit(f"preflight estimated cost USD {total_cost:.6f} exceeds preflight budget USD {args.max_budget_usd:.6f}")


if __name__ == "__main__":
    main()
