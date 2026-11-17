from __future__ import annotations

import argparse
import json
from pathlib import Path

from legacy.experiment2_reconstruction.controller import reconstruct_experiment2


def main():
    parser = argparse.ArgumentParser(description="Reconstruct archived Experiment 2B/2D/2E outputs from original benchmark data.")
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark/cases.jsonl"))
    parser.add_argument("--original-results", type=Path, default=Path("results/exp2"))
    parser.add_argument("--output", type=Path, default=Path("results/exp2_reconstruction"))
    args = parser.parse_args()
    manifest = reconstruct_experiment2(args.benchmark, args.original_results, args.output)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
