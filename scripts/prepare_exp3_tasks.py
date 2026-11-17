from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.exp3_real_models.harness import prepare_tasks, read_jsonl, assert_public_task_blinded


def main():
    parser = argparse.ArgumentParser(description="Prepare blinded Experiment 3 tasks without making model calls.")
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_v0.4/cases.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("results/exp3_real_models"))
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        tasks = read_jsonl(args.output / "public" / "tasks.jsonl")
        for task in tasks:
            assert_public_task_blinded(task)
        manifest = json.loads((args.output / "public" / "task_manifest.json").read_text(encoding="utf-8"))
        print(json.dumps({"verified_public_tasks": len(tasks), "manifest": manifest}, indent=2))
        return
    manifest = prepare_tasks(args.benchmark, args.output)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
