"""Deterministic synthetic signed-catalog and executor-binding threat experiment."""
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

from src.action_authorization import authorize_action, sign_catalog, verify_execution_binding

BENCH = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUT = ROOT / "results" / "signed_action_catalog_threats"
KEY = b"synthetic-test-key-not-for-production"
VERSION = "catalog-2026-11-01"
CATALOG = {
    "save_temporary_record": {"risk_level": "LOW", "reversibility": "HIGH", "external_effect": "LOW"},
    "advance_operational_workflow": {"risk_level": "HIGH", "reversibility": "LOW", "external_effect": "HIGH"},
}


def load_cases():
    with BENCH.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()
                and json.loads(line)["action"]["risk_level"] == "HIGH"]


def main():
    manifest = sign_catalog(VERSION, CATALOG, KEY)
    tampered = json.loads(json.dumps(manifest))
    tampered["payload"]["actions"]["advance_operational_workflow"]["risk_level"] = "LOW"
    rows = []
    cases = load_cases()
    for case in cases:
        action = dict(case["action"])
        trusted_id = action["name"]
        attacks = [
            ("baseline", action, manifest, VERSION, trusted_id, VERSION),
            ("catalog_tampering", {**action, "risk_level": "LOW"}, tampered, VERSION, trusted_id, VERSION),
            ("stale_catalog", action, manifest, "catalog-newer", trusted_id, "catalog-newer"),
            ("action_alias_substitution", {
                "name": "save_temporary_record", **CATALOG["save_temporary_record"]
            }, manifest, VERSION, trusted_id, VERSION),
        ]
        for attack, proposed, used_manifest, expected_version, invoke_id, current_version in attacks:
            token = authorize_action(
                proposed, trusted_action_id=trusted_id, manifest=used_manifest,
                key=KEY, expected_catalog_version=expected_version,
            )
            authorized = token is not None
            executor_ok = bool(token) and verify_execution_binding(
                token, invoked_action_id=invoke_id,
                current_catalog_version=current_version, key=KEY,
            )
            rows.append({
                "case_id": case["case_id"], "family": case["family"],
                "attack": attack, "authorized": authorized,
                "executor_binding_accepted": executor_ok,
            })

        token = authorize_action(
            action, trusted_action_id=trusted_id, manifest=manifest,
            key=KEY, expected_catalog_version=VERSION,
        )
        rows.append({
            "case_id": case["case_id"], "family": case["family"],
            "attack": "executor_tool_substitution", "authorized": token is not None,
            "executor_binding_accepted": bool(token) and verify_execution_binding(
                token, invoked_action_id="save_temporary_record",
                current_catalog_version=VERSION, key=KEY,
            ),
        })
        rows.append({
            "case_id": case["case_id"], "family": case["family"],
            "attack": "post_authorization_version_change", "authorized": token is not None,
            "executor_binding_accepted": bool(token) and verify_execution_binding(
                token, invoked_action_id=trusted_id,
                current_catalog_version="catalog-2026-11-02", key=KEY,
            ),
        })

    summary = []
    for attack in sorted({row["attack"] for row in rows}):
        subset = [row for row in rows if row["attack"] == attack]
        summary.append({
            "attack": attack, "cases": len(subset),
            "authorization_accepts": sum(row["authorized"] for row in subset),
            "executor_binding_accepts": sum(row["executor_binding_accepted"] for row in subset),
        })
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in (("case_results.csv", rows), ("summary.csv", summary)):
        with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    manifest_out = {
        "experiment": "signed-action-catalog-threats-v1",
        "status": "deterministic synthetic trust-boundary conformance test",
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "benchmark": "v0.4 HIGH-risk subset",
        "cases": len(cases),
        "attack_classes": sorted({row["attack"] for row in rows}),
        "signing": "HMAC-SHA256 with a synthetic in-process test key; not production key management",
        "claim_boundary": "Checks catalog integrity, version pinning, action identity and executor binding functions only; no real external tool is invoked.",
        "dataset_sha256": hashlib.sha256(BENCH.read_bytes()).hexdigest(),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest_out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": manifest_out, "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
