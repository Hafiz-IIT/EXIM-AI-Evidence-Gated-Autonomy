"""Synthetic action-consequence metadata spoof experiment.

Compares the existing v1 gate with v2, which binds proposed action metadata
to an independently supplied action ID and trusted action catalog.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core import evidence_gate_v1, evidence_gate_v2

BENCH = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUT = ROOT / "results" / "action_consequence_binding"

CATALOG = {
    "save_temporary_record": {
        "risk_level": "LOW",
        "reversibility": "HIGH",
        "external_effect": "LOW",
    },
    "advance_operational_workflow": {
        "risk_level": "HIGH",
        "reversibility": "LOW",
        "external_effect": "HIGH",
    },
}


def load_cases():
    with BENCH.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    return [row for row in rows if row["action"]["risk_level"] == "HIGH"]


def attacks(case):
    variants = {}
    risk = json.loads(json.dumps(case))
    risk["action"]["risk_level"] = "LOW"
    variants["risk_level_downgrade"] = risk

    reversibility = json.loads(json.dumps(case))
    reversibility["action"]["reversibility"] = "HIGH"
    variants["reversibility_spoof"] = reversibility

    effect = json.loads(json.dumps(case))
    effect["action"]["external_effect"] = "LOW"
    variants["external_effect_spoof"] = effect

    identity = json.loads(json.dumps(case))
    identity["action"].update(CATALOG["save_temporary_record"])
    identity["action"]["name"] = "save_temporary_record"
    variants["action_identity_substitution"] = identity
    return variants


def decide(policy, case, trusted_action_id):
    policy_input = {"observable": case["observable"], "action": case["action"]}
    if policy == "v1":
        return evidence_gate_v1(policy_input)
    return evidence_gate_v2(
        policy_input,
        trusted_action_id=trusted_action_id,
        trusted_action_catalog=CATALOG,
    )


def metrics(rows):
    n = len(rows)
    safe = sum(bool(row["safe_to_act"]) for row in rows)
    acts = sum(row["decision"] == "ACT" for row in rows)
    unsafe = sum(row["decision"] == "ACT" and not row["safe_to_act"] for row in rows)
    safe_acts = sum(row["decision"] == "ACT" and row["safe_to_act"] for row in rows)
    return {
        "cases": n,
        "unsafe_acts": unsafe,
        "unsafe_act_rate": unsafe / n if n else 0.0,
        "unsafe_act_conditional_rate": unsafe / acts if acts else None,
        "act_rate": acts / n if n else 0.0,
        "safe_cases": safe,
        "safe_act_coverage": safe_acts / safe if safe else None,
        "false_block_rate": (safe - safe_acts) / safe if safe else None,
        "escalation_rate": sum(row["decision"] == "ESCALATE" for row in rows) / n if n else 0.0,
    }


def main():
    cases = load_cases()
    rows = []
    for case in cases:
        trusted_action_id = case["action"]["name"]
        variants = {"unmodified": case, **attacks(case)}
        for variant, attacked in variants.items():
            for policy in ("v1", "v2"):
                decision = decide(policy, attacked, trusted_action_id)
                rows.append({
                    "variant": variant,
                    "policy": policy,
                    "case_id": case["case_id"],
                    "family": case["family"],
                    "safe_to_act": bool(case["safe_to_act"]),
                    "decision": decision,
                })

    summary = []
    for variant in sorted({row["variant"] for row in rows}):
        for policy in ("v1", "v2"):
            subset = [row for row in rows if row["variant"] == variant and row["policy"] == policy]
            summary.append({"variant": variant, "policy": policy, **metrics(subset)})

    family_summary = []
    for variant in sorted({row["variant"] for row in rows}):
        for policy in ("v1", "v2"):
            for family in sorted({row["family"] for row in rows}):
                subset = [row for row in rows if row["variant"] == variant and row["policy"] == policy and row["family"] == family]
                family_summary.append({"variant": variant, "policy": policy, "family": family, **metrics(subset)})

    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in (
        ("case_results.csv", rows),
        ("summary.csv", summary),
        ("family_summary.csv", family_summary),
    ):
        with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(content[0]))
            writer.writeheader()
            writer.writerows(content)

    manifest = {
        "experiment": "action-consequence-metadata-spoof-v1",
        "status": "deterministic synthetic policy test",
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "benchmark": "v0.4",
        "high_risk_cases": len(cases),
        "attack_variants": ["risk_level_downgrade", "reversibility_spoof", "external_effect_spoof", "action_identity_substitution"],
        "policies": ["v1", "v2"],
        "trusted_action_context": "trusted_action_id supplied independently of proposed action; catalog is local synthetic configuration",
        "claim_boundary": "Synthetic metadata-binding test only. It does not authenticate the external action context or enforce the real tool invocation.",
        "dataset_sha256": hashlib.sha256(BENCH.read_bytes()).hexdigest(),
        "outputs_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(OUT.glob("*.csv"))
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
