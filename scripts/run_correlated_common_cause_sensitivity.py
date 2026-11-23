"""Correlated common-cause error sensitivity for evidence-gated autonomy.

A shared latent shock creates positive dependence among retrieval, verifier and
human-review errors while preserving each channel's marginal error probability.
This is an illustrative synthetic stress model, not a field-calibrated model.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
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
OUT = ROOT / "results" / "correlated_common_cause_sensitivity"
N_SEEDS = 20
T95_DF19 = 2.093
POLICIES = {"EvidenceGate": evidence_gate_v1, "RiskGate": risk_gate}

GRID = {
    "retrieval_accuracy": (0.50, 0.75, 0.95),
    "human_accuracy": (0.75, 0.90, 0.98),
    "verifier_accuracy": (0.85, 0.93, 0.98),
    "common_shock_fraction": (0.0, 0.5, 1.0),
}
FIXED = {
    "retrieval_availability": 0.75,
    "escalation_availability": 0.95,
    "unavailable_fallback": "DEFER",
}


def load_high_risk_cases():
    with BENCH.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    cases = [row for row in rows if row["action"]["risk_level"] == "HIGH"]
    if len(cases) != 700:
        raise ValueError(f"Expected 700 HIGH-risk cases, found {len(cases)}")
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("HIGH-risk case IDs are not unique")
    return cases


def common_shock_mass(params):
    """Largest common-shock mass that preserves all three error marginals."""
    minimum_error = min(
        1.0 - params["retrieval_accuracy"],
        1.0 - params["human_accuracy"],
        1.0 - params["verifier_accuracy"],
    )
    return params["common_shock_fraction"] * minimum_error


def residual_error_probability(accuracy, shock_mass):
    """Residual independent error rate after a shared all-channel shock."""
    marginal_error = 1.0 - float(accuracy)
    if not 0.0 <= shock_mass <= marginal_error or shock_mass >= 1.0:
        raise ValueError("Common-shock mass must be below every channel's error rate")
    return (marginal_error - shock_mass) / (1.0 - shock_mass)


def make_correlated_draws(cases, seed):
    """Case-indexed common shock plus independent channel-specific noise."""
    draws = {}
    for case in cases:
        material = f"ega-correlated-errors-v1|{seed}|{case['case_id']}".encode("utf-8")
        case_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
        rng = random.Random(case_seed)
        draws[case["case_id"]] = {
            "common_shock": rng.random(),
            "verifier_noise": rng.random(),
            "retrieval_noise": rng.random(),
            "human_noise": rng.random(),
            "retrieval_available": rng.random(),
            "escalation_available": rng.random(),
        }
    return draws


def channel_correct(draws, channel, accuracy, shock_mass):
    if draws["common_shock"] < shock_mass:
        return False
    residual = residual_error_probability(accuracy, shock_mass)
    return draws[f"{channel}_noise"] >= residual


def escalation_outcome(safe, params, draws, shock_mass):
    if draws["escalation_available"] >= params["escalation_availability"]:
        return params["unavailable_fallback"] == "ACT"
    correct = channel_correct(draws, "human", params["human_accuracy"], shock_mass)
    return bool(safe) if correct else not bool(safe)


def final_consequential_action(policy_action, safe_to_act, params, draws):
    """Resolve policy action using correlated correctness errors."""
    safe = bool(safe_to_act)
    shock_mass = common_shock_mass(params)
    if policy_action == "ACT":
        return True
    if policy_action == "DEFER":
        return False
    if policy_action == "VERIFY":
        correct = channel_correct(draws, "verifier", params["verifier_accuracy"], shock_mass)
        return safe if correct else not safe
    if policy_action == "REQUEST_EVIDENCE":
        available = draws["retrieval_available"] < params["retrieval_availability"]
        if available:
            correct = channel_correct(draws, "retrieval", params["retrieval_accuracy"], shock_mass)
            return safe if correct else not safe
        return escalation_outcome(safe, params, draws, shock_mass)
    if policy_action == "ESCALATE":
        return escalation_outcome(safe, params, draws, shock_mass)
    raise ValueError(f"Unknown policy action: {policy_action}")


def precompute_policy_actions(cases):
    cached = {name: {} for name in POLICIES}
    for name, policy in POLICIES.items():
        for case in cases:
            policy_input = {"observable": case["observable"], "action": case["action"]}
            cached[name][case["case_id"]] = policy(policy_input)
    return cached


def metrics(counters):
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


def evaluate_policy(cases, policy_actions, params, draws):
    counters = defaultdict(int)
    by_family = defaultdict(lambda: defaultdict(int))
    for case in cases:
        decision = final_consequential_action(
            policy_actions[case["case_id"]], case["safe_to_act"], params,
            draws[case["case_id"]],
        )
        safe = bool(case["safe_to_act"])
        for bucket in (counters, by_family[case["family"]]):
            bucket["n"] += 1
            bucket["safe_n"] += int(safe)
            bucket["acts"] += int(decision)
            bucket["unsafe_acts"] += int(decision and not safe)
            bucket["safe_acts"] += int(decision and safe)
    return metrics(counters), {name: metrics(row) for name, row in by_family.items()}


def evaluate_serial_evidence_gate(cases, params, draws):
    """Stylized serial gate: retrieval and verifier must agree; disagreement escalates."""
    counters = defaultdict(int)
    by_family = defaultdict(lambda: defaultdict(int))
    shock_mass = common_shock_mass(params)
    for case in cases:
        safe = bool(case["safe_to_act"])
        case_draws = draws[case["case_id"]]
        retrieval_available = case_draws["retrieval_available"] < params["retrieval_availability"]
        if not retrieval_available:
            decision = escalation_outcome(safe, params, case_draws, shock_mass)
        else:
            retrieval_says_safe = safe if channel_correct(
                case_draws, "retrieval", params["retrieval_accuracy"], shock_mass
            ) else not safe
            verifier_says_safe = safe if channel_correct(
                case_draws, "verifier", params["verifier_accuracy"], shock_mass
            ) else not safe
            if retrieval_says_safe == verifier_says_safe:
                decision = retrieval_says_safe
            else:
                decision = escalation_outcome(safe, params, case_draws, shock_mass)
        for bucket in (counters, by_family[case["family"]]):
            bucket["n"] += 1
            bucket["safe_n"] += int(safe)
            bucket["acts"] += int(decision)
            bucket["unsafe_acts"] += int(decision and not safe)
            bucket["safe_acts"] += int(decision and safe)
    return metrics(counters), {name: metrics(row) for name, row in by_family.items()}


def mean_ci(values):
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None, None, None, None
    mean = statistics.mean(clean)
    sd = statistics.stdev(clean) if len(clean) > 1 else 0.0
    half = T95_DF19 * sd / (len(clean) ** 0.5) if len(clean) > 1 else 0.0
    return mean, sd, mean - half, mean + half


def paired_difference_ci(left, right):
    diffs = [float(a) - float(b) for a, b in zip(left, right) if a is not None and b is not None]
    if not diffs:
        return None, None, None, None
    mean = statistics.mean(diffs)
    sd = statistics.stdev(diffs) if len(diffs) > 1 else 0.0
    half = T95_DF19 * sd / (len(diffs) ** 0.5) if len(diffs) > 1 else 0.0
    return mean, sd, mean - half, mean + half


def conditions():
    keys = list(GRID)
    for values in itertools.product(*(GRID[key] for key in keys)):
        yield dict(zip(keys, values))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to write empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def paired_shock_effects(seed_rows):
    """Paired within-seed changes from rho=0 to rho=0.5 and rho=max."""
    metrics_to_compare = (
        "unsafe_act_rate", "unsafe_act_conditional_rate", "safe_act_coverage",
        "false_block_rate", "act_rate",
    )
    base_keys = ("retrieval_accuracy", "human_accuracy", "verifier_accuracy")
    lookup = {}
    policies = ("EvidenceGate", "RiskGate", "SerialEvidenceGate")
    for row in seed_rows:
        base = tuple(float(row[name]) for name in base_keys)
        seed = int(row["seed"])
        shock_fraction = float(row["common_shock_fraction"])
        for policy in policies:
            lookup[(base, seed, policy, shock_fraction)] = row
    output = []
    base_conditions = list(itertools.product(*(GRID[key] for key in base_keys)))
    for base in base_conditions:
        base_tuple = tuple(float(value) for value in base)
        for policy in policies:
            for target_fraction in (0.5, 1.0):
                for metric in metrics_to_compare:
                    left = [
                        lookup[(base_tuple, seed, policy, target_fraction)][f"{policy}_{metric}"]
                        for seed in range(N_SEEDS)
                    ]
                    right = [
                        lookup[(base_tuple, seed, policy, 0.0)][f"{policy}_{metric}"]
                        for seed in range(N_SEEDS)
                    ]
                    mean, sd, low, high = paired_difference_ci(left, right)
                    output.append({
                        "retrieval_accuracy": base_tuple[0],
                        "human_accuracy": base_tuple[1],
                        "verifier_accuracy": base_tuple[2],
                        "policy": policy,
                        "comparison": f"shock_{target_fraction}_minus_independent",
                        "metric": metric,
                        "paired_mean_difference": mean,
                        "paired_sd": sd,
                        "paired_95ci_low": low,
                        "paired_95ci_high": high,
                        "seeds": N_SEEDS,
                    })
    return output


def main():
    cases = load_high_risk_cases()
    policy_cache = precompute_policy_actions(cases)
    draws_by_seed = {seed: make_correlated_draws(cases, seed) for seed in range(N_SEEDS)}
    overall_rows = []
    family_rows = []
    seed_rows = []
    metric_names = (
        "unsafe_act_rate", "unsafe_act_conditional_rate", "safe_act_coverage",
        "false_block_rate", "act_rate",
    )

    for condition_id, condition in enumerate(conditions(), start=1):
        params = {**FIXED, **condition}
        shock = common_shock_mass(params)
        policy_names = [*POLICIES, "SerialEvidenceGate"]
        per_policy = {name: [] for name in policy_names}
        per_family = {name: defaultdict(list) for name in policy_names}
        for seed in range(N_SEEDS):
            draws = draws_by_seed[seed]
            for name in POLICIES:
                overall, families = evaluate_policy(cases, policy_cache[name], params, draws)
                per_policy[name].append(overall)
                for family, result in families.items():
                    per_family[name][family].append(result)
            serial_overall, serial_families = evaluate_serial_evidence_gate(cases, params, draws)
            per_policy["SerialEvidenceGate"].append(serial_overall)
            for family, result in serial_families.items():
                per_family["SerialEvidenceGate"][family].append(result)
            seed_row = {
                "condition_id": condition_id, "seed": seed,
                **params, "common_shock_mass": shock,
            }
            for name in policy_names:
                for metric in metric_names:
                    seed_row[f"{name}_{metric}"] = per_policy[name][-1][metric]
            seed_rows.append(seed_row)

        row = {
            "condition_id": condition_id, **params,
            "common_shock_mass": shock,
            "seeds": N_SEEDS, "high_risk_cases": len(cases),
        }
        for name in policy_names:
            for metric in metric_names:
                mean, sd, low, high = mean_ci([item[metric] for item in per_policy[name]])
                prefix = f"{name}_{metric}"
                row[prefix + "_mean"] = mean
                row[prefix + "_sd"] = sd
                row[prefix + "_95ci_low"] = low
                row[prefix + "_95ci_high"] = high
        for left_name, right_name in (("EvidenceGate", "RiskGate"), ("SerialEvidenceGate", "RiskGate")):
            for metric in metric_names:
                mean, sd, low, high = paired_difference_ci(
                    [item[metric] for item in per_policy[left_name]],
                    [item[metric] for item in per_policy[right_name]],
                )
                prefix = f"paired_{left_name}_minus_{right_name}_{metric}"
                row[prefix + "_mean"] = mean
                row[prefix + "_sd"] = sd
                row[prefix + "_95ci_low"] = low
                row[prefix + "_95ci_high"] = high
        overall_rows.append(row)

        for name in policy_names:
            for family, seed_metrics in per_family[name].items():
                frow = {
                    "condition_id": condition_id, "policy": name,
                    "scenario_family": family, **params,
                    "common_shock_mass": shock, "seeds": N_SEEDS,
                }
                for metric in metric_names:
                    mean, sd, low, high = mean_ci([item[metric] for item in seed_metrics])
                    frow[metric + "_mean"] = mean
                    frow[metric + "_sd"] = sd
                    frow[metric + "_95ci_low"] = low
                    frow[metric + "_95ci_high"] = high
                family_rows.append(frow)

    OUT.mkdir(parents=True, exist_ok=True)
    shock_effect_rows = paired_shock_effects(seed_rows)
    write_csv(OUT / "overall_summary.csv", overall_rows)
    write_csv(OUT / "scenario_family_summary.csv", family_rows)
    write_csv(OUT / "seed_level_results.csv", seed_rows)
    write_csv(OUT / "paired_shock_effects.csv", shock_effect_rows)
    manifest = {
        "experiment": "correlated-common-cause-retrieval-verifier-human-sensitivity-v2",
        "status": "exploratory synthetic sensitivity analysis",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "benchmark": "v0.4 HIGH-risk subset",
        "high_risk_cases": len(cases),
        "seeds": N_SEEDS,
        "condition_count": len(overall_rows),
        "policy_comparison": [*POLICIES, "SerialEvidenceGate"],
        "serial_gate_definition": "Stylized two-source serial gate: retrieved evidence and verifier assessments must agree to decide; disagreement or retrieval unavailability escalates to human review. This is an analytical comparator, not the current EvidenceGate implementation.",
        "fixed_assumptions": FIXED,
        "parameter_grid": {key: list(values) for key, values in GRID.items()},
        "correlation_model": (
            "Shared shock Z with probability rho forces all available correctness channels to err; "
            "otherwise channel j has residual error (e_j-rho)/(1-rho), preserving marginal error e_j. "
            "rho = common_shock_fraction * min(e_retrieval, e_human, e_verifier)."
        ),
        "common_random_numbers": "case-indexed shared shock and channel-specific draws reused across policies",
        "dataset_sha256": hashlib.sha256(BENCH.read_bytes()).hexdigest(),
        "claim_boundary": (
            "Illustrative common-cause stress model only. Marginal accuracies and shock fractions are not "
            "empirically calibrated; outcomes are not estimates of deployment incident rates."
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
