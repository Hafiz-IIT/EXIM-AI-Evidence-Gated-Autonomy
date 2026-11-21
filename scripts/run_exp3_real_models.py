from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


import argparse
import json
from pathlib import Path

from experiments.exp3_real_models.harness import run_condition


def main():
    parser = argparse.ArgumentParser(description="Run one frozen Experiment 3 model condition.")
    parser.add_argument("--config", type=Path, required=True, help="Private JSON config; API keys must remain in environment variables.")
    parser.add_argument("--prepared-dir", type=Path, default=Path("results/exp3_real_models"))
    parser.add_argument("--split", choices=["development", "validation", "final_holdout_id", "final_holdout_ood"], required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("results/exp3_real_models/runs"))
    parser.add_argument("--max-tasks", type=int)
    parser.add_argument("--confirm-final-holdout", action="store_true")
    args = parser.parse_args()
    if args.split.startswith("final_holdout"):
        if not args.confirm_final_holdout:
            parser.error("final holdout requires --confirm-final-holdout")
        if args.max_tasks is not None:
            parser.error("partial final-holdout runs are prohibited")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    condition = next((x for x in config["conditions"] if x["condition_id"] == args.condition), None)
    if condition is None:
        parser.error(f"unknown condition: {args.condition}")
    result = run_condition(
        config=config, condition=condition, split=args.split,
        prepared_dir=args.prepared_dir,
        output_dir=args.output_dir / args.split / args.condition,
        max_tasks=args.max_tasks,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
