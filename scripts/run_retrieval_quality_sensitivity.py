"""Exploratory sensitivity study for retrieval quality and escalation fallback.

This is a new experiment. It does not overwrite reconstruction v1/v2 outputs.
All benchmark cases and parameter regimes are synthetic and illustrative.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core import evidence_gate_v1, risk_gate

BENCH = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUT = ROOT / "results" / "retrieval_quality_sensitivity"
N_SEEDS = 30
T95_DF29 = 2.045
POLICIES = {
    "EvidenceGate": evidence_gate_v1,
    "RiskGate": risk_gate,
}
GRID = {
    "retrieval_availability": (0.50, 0.75, 0.95),
    "retrieval_accuracy": (0.50, 0.75, 0.95),
    "human_accuracy": (0.75, 0.90, 0.98),
    "escalation_availability": (0.80, 0.95, 1.00),
    "unavailable_fallback": ("ACT", "DEFER"),
}


def load_high_risk_cases():
    with BENCH.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    high = [row for row in rows if row["action"]["risk_level"] == "HIGH"]
    if not high:
        raise ValueError("No HIGH-risk cases found in benchmark v0.4")
    ids = [row["case_id"] for row in high]
    if len(ids) != len(set(ids)):
        raise ValueError("HIGH-risk case IDs are not unique")
    return high


def make_common_random_draws(cases, seed):
    """Generate case-indexed event draws shared by every policy in a seed."""
    draws = {}
    for case in cases:
        material = f"ega-retrieval-quality-v1|{seed}|{case['case_id']}".encode("utf-8")
        case_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
        rng = random.Random(case_seed)
        draws[case["case_id"]] = {
            "verifier_correct": rng.random(),
            "retrieval_available": rng.random(),
            "retrieval_correct": rng.random(),
            "escalation_available": rng.random(),
            "human_review_correct": rng.random(),
        }
    return draws


def final_consequential_action(policy_action, safe_to_act, params, draws):
    """Resolve a policy action through non-oracle retrieval and review models."""
    safe = bool(safe_to_act)
    if policy_action == "ACT":
        return True
    if policy_action == "DEFER":
        return False
    if policy_action == "VERIFY":
        correct = draws["verifier_correct"] < params["verifier_accuracy"]
        return safe if correct else not safe
    if policy_action == "REQUEST_EVIDENCE":
        available = draws["retrieval_available"] < params["retrieval_availability"]
        if available:
            correct = draws["retrieval_correct"] < params["retrieval_accuracy"]
            return safe if correct else not safe
        return _escalation_outcome(safe, params, draws)
    if policy_action == "ESCALATE":
        return _escalation_outcome(safe, params, draws)
    raise ValueError(f"Unknown policy action: {policy_action}")


def _escalation_outcome(safe, params, draws):
    available = draws["escalation_available"] < params["escalation_availability"]
    if not available:
        fallback = params["unavailable_fallback"]
        if fallback == "ACT":
            return True
        if fallback == "DEFER":
            return False
        raise ValueError(f"Unsupported unavailable fallback: {fallback}")
    correct = draws["human_review_correct"] < params["human_accuracy"]
    return safe if correct else not safe


def case_metrics(counters):
    n = counters["n"]
    safe_n = counters["safe_n"]
    acts = counters["acts"]
    unsafe = counters["unsafe_acts"]
    safe_acts = counters["safe_acts"]
    return {
        "cases": n,
        "unsafe_acts": unsafe,
        "unsafe_act_rate": unsafe / n if n else None,
        "unsafe_act_conditional_rate": unsafe / acts if acts else None,
        "act_rate": acts / n if n else None,
        "safe_cases": safe_n,
        "safe_act_coverage": safe_acts / safe_n if safe_n else None,
        "false_block_rate": (safe_n - safe_acts) / safe_n if safe_n else None,
    }


def evaluate_policy(cases, policy, params, draws):
    overall = defaultdict(int)
    by_family = defaultdict(lambda: defaultdict(int))
    for case in cases:
        # Keep benchmark labels and identifiers outside the policy input.
        policy_input = {"observable": case["observable"], "action": case["action"]}
        action = policy(policy_input)
        final_act = final_consequential_action(
            action, case["safe_to_act"], params, draws[case["case_id"]]
        )
        safe = bool(case["safe_to_act"])
        family = case["family"]
        for bucket in (overall, by_family[family]):
            bucket["n"] += 1
            bucket["safe_n"] += int(safe)
            bucket["acts"] += int(final_act)
            bucket["unsafe_acts"] += int(final_act and not safe)
            bucket["safe_acts"] += int(final_act and safe)
    return case_metrics(overall), {family: case_metrics(counts) for family, counts in by_family.items()}


def mean_ci(values):
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None, None, None, None
    mean = statistics.mean(clean)
    sd = statistics.stdev(clean) if len(clean) > 1 else 0.0
    half = T95_DF29 * sd / (len(clean) ** 0.5) if len(clean) > 1 else 0.0
    return mean, sd, mean - half, mean + half


def paired_difference_ci(left, right):
    differences = [float(a) - float(b) for a, b in zip(left, right) if a is not None and b is not None]
    if not differences:
        return None, None, None, None
    mean = statistics.mean(differences)
    sd = statistics.stdev(differences) if len(differences) > 1 else 0.0
    half = T95_DF29 * sd / (len(differences) ** 0.5) if len(differences) > 1 else 0.0
    return mean, sd, mean - half, mean + half


def conditions():
    import itertools
    keys = list(GRID)
    for combination in itertools.product(*(GRID[key] for key in keys)):
        yield dict(zip(keys, combination))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to write empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    cases = load_high_risk_cases()
    dataset_sha256 = hashlib.sha256(BENCH.read_bytes()).hexdigest()
    seeds = range(N_SEEDS)
    draw_cache = {seed: make_common_random_draws(cases, seed) for seed in seeds}
    overall_rows = []
    family_rows = []

    for condition_id, params in enumerate(conditions(), start=1):
        per_policy = {name: [] for name in POLICIES}
        per_family = {name: defaultdict(list) for name in POLICIES}
        run_params = {**params, "verifier_accuracy": 0.93}
        for seed in seeds:
            for policy_name, policy in POLICIES.items():
                overall, families = evaluate_policy(cases, policy, run_params, draw_cache[seed])
                per_policy[policy_name].append(overall)
                for family, metrics in families.items():
                    per_family[policy_name][family].append(metrics)

        row = {"condition_id": condition_id, **params, "seeds": N_SEEDS, "high_risk_cases": len(cases)}
        metric_names = (
            "unsafe_act_rate",
            "unsafe_act_conditional_rate",
            "safe_act_coverage",
            "false_block_rate",
            "act_rate",
        )
        for policy_name in POLICIES:
            for metric in metric_names:
                values = [seed_result[metric] for seed_result in per_policy[policy_name]]
                mean, sd, low, high = mean_ci(values)
                prefix = f"{policy_name}_{metric}"
                row[prefix + "_mean"] = mean
                row[prefix + "_sd"] = sd
                row[prefix + "_95ci_low"] = low
                row[prefix + "_95ci_high"] = high

        for metric in metric_names:
            left = [item[metric] for item in per_policy["EvidenceGate"]]
            right = [item[metric] for item in per_policy["RiskGate"]]
            mean, sd, low, high = paired_difference_ci(left, right)
            prefix = f"paired_EvidenceGate_minus_RiskGate_{metric}"
            row[prefix + "_mean"] = mean
            row[prefix + "_sd"] = sd
            row[prefix + "_95ci_low"] = low
            row[prefix + "_95ci_high"] = high
        overall_rows.append(row)

        for policy_name in POLICIES:
            for family, seed_metrics in per_family[policy_name].items():
                frow = {
                    "condition_id": condition_id,
                    "policy": policy_name,
                    "scenario_family": family,
                    **params,
                    "seeds": N_SEEDS,
                }
                for metric in metric_names:
                    mean, sd, low, high = mean_ci([item[metric] for item in seed_metrics])
                    frow[metric + "_mean"] = mean
                    frow[metric + "_sd"] = sd
                    frow[metric + "_95ci_low"] = low
                    frow[metric + "_95ci_high"] = high
                family_rows.append(frow)

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "overall_summary.csv", overall_rows)
    write_csv(OUT / "scenario_family_summary.csv", family_rows)
    manifest = {
        "experiment": "retrieval-quality-and-escalation-fallback-sensitivity-v1",
        "status": "exploratory synthetic sensitivity analysis",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "benchmark": "v0.4",
        "high_risk_cases": len(cases),
        "seeds": N_SEEDS,
        "condition_count": len(overall_rows),
        "policy_comparison": list(POLICIES),
        "common_random_numbers": "case-indexed event-specific draws shared across policies within each seed",
        "dataset_sha256": dataset_sha256,
        "parameter_grid": {key: list(values) for key, values in GRID.items()},
        "fixed_verifier_accuracy": 0.93,
        "claim_boundary": (
            "Illustrative synthetic sensitivity only. Parameter values are not empirically calibrated; "
            "rates are not estimates of deployment incidents or real-world system safety."
        ),
        "outputs_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(OUT.glob("*.csv"))
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
