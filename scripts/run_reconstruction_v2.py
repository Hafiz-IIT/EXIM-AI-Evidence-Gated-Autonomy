"""Run v0.4 reconstruction plus one-factor and interaction sensitivity sweeps."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import random
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.run_reconstruction_v1 as base
base.BENCH = ROOT / "data" / "benchmark_v0.4"
base.OUT = ROOT / "results" / "reconstruction_v2"
OUT = base.OUT
SENSITIVITY_LEVELS = {
    "verifier_accuracy": [0.75, 0.85, 0.93, 0.99],
    "retrieval_success": [0.70, 0.85, 0.92, 0.99],
    "human_accuracy": [0.70, 0.80, 0.90, 0.98],
    "escalation_available": [0.70, 0.85, 0.95, 1.00],
}
BASELINE = {
    "verifier_accuracy": 0.93,
    "retrieval_success": 0.92,
    "human_accuracy": 0.90,
    "escalation_available": 0.95,
}
POLICY_NAMES = ("B4_AlwaysVerify", "B7_RiskGate", "B8_EvidenceGate")


def run_sensitivity(cases):
    policies = {name: base.POLICIES[name] for name in POLICY_NAMES}
    raw = []
    condition_index = 0
    for parameter, levels in SENSITIVITY_LEVELS.items():
        for level in levels:
            params = dict(BASELINE)
            params[parameter] = level
            condition = f"one_factor_{parameter}_{level:.2f}"
            for policy_index, (policy_name, policy) in enumerate(policies.items()):
                for seed in range(base.N_SEEDS):
                    run_seed = 80000 + condition_index * 1000 + seed
                    metrics = base.evaluate_policy(cases, policy, params, run_seed)
                    raw.append({
                        "experiment": "sensitivity_one_factor",
                        "condition": condition,
                        "varied_parameter": parameter,
                        "varied_value": level,
                        "human_accuracy": params["human_accuracy"],
                        "escalation_available": params["escalation_available"],
                        "policy": policy_name,
                        "seed": seed,
                        **metrics,
                    })
            condition_index += 1

    # Two-factor interaction: human review accuracy × escalation availability.
    for human in (0.70, 0.85, 0.98):
        for available in (0.70, 0.85, 1.00):
            params = dict(BASELINE)
            params["human_accuracy"] = human
            params["escalation_available"] = available
            condition = f"interaction_human_{human:.2f}_availability_{available:.2f}"
            for policy_name, policy in policies.items():
                for seed in range(base.N_SEEDS):
                    run_seed = 100000 + condition_index * 1000 + seed
                    metrics = base.evaluate_policy(cases, policy, params, run_seed)
                    raw.append({
                        "experiment": "sensitivity_interaction",
                        "condition": condition,
                        "varied_parameter": "human_accuracy_x_escalation_available",
                        "varied_value": None,
                        "human_accuracy": human,
                        "escalation_available": available,
                        "policy": policy_name,
                        "seed": seed,
                        **metrics,
                    })
            condition_index += 1

    base.write_csv(OUT / "sensitivity_seed_results.csv", raw)
    group_fields = ["experiment", "condition", "varied_parameter", "varied_value", "policy"]
    summary = base.summarize_seed_runs(raw, group_fields)
    base.write_csv(OUT / "sensitivity_summary.csv", summary)
    return len(raw), len(summary)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cases = base.read_jsonl(base.BENCH / "cases.jsonl")
    if len(cases) != 1400:
        raise SystemExit(f"Expected 1,400 v0.4 cases, found {len(cases)}")

    # Re-run the complete transparent experiment suite on v0.4, in a separate output directory.
    base.exp1b(cases)
    base.exp1c(cases)
    base.exp1d(cases)
    base.exp2(cases)
    raw_count, summary_count = run_sensitivity(cases)

    files = sorted(OUT.glob("*.csv"))
    manifest = {
        "protocol": "EGA reconstruction v2 on benchmark v0.4",
        "historical_reproduction": False,
        "benchmark_version": "0.4",
        "benchmark_records": len(cases),
        "monte_carlo_seeds_per_condition": base.N_SEEDS,
        "sensitivity_seed_rows": raw_count,
        "sensitivity_summary_rows": summary_count,
        "one_factor_parameters": SENSITIVITY_LEVELS,
        "interaction_parameters": ["human_accuracy", "escalation_available"],
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "generated_files": [p.name for p in files],
        "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "signature_records_created": base.ATTESTATIONS_CREATED,
        "note": "New synthetic reconstruction on benchmark v0.4; not a reproduction of historical experiment outputs.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
