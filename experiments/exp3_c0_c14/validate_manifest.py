#!/usr/bin/env python3
"""Offline structural validator for the Experiment 3 disposable dry-run manifest.

This module makes no network requests and cannot call a model provider.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

EXPECTED = 28
ALLOWED_STAGES = {"PROPOSER", "V1", "V2", "RECOVERY"}
ALLOWED_FAMILIES = {"G", "Z", "O"}

def validate(data: dict) -> list[str]:
    errors=[]
    calls=data.get("calls", [])
    if data.get("calls_total") != EXPECTED or len(calls) != EXPECTED:
        errors.append(f"expected exactly {EXPECTED} calls")
    ids=[x.get("run_id") for x in calls]
    if len(ids) != len(set(ids)):
        errors.append("duplicate run_id")
    for i, call in enumerate(calls, start=1):
        if call.get("sequence") != i:
            errors.append(f"sequence mismatch at row {i}")
        if call.get("family") not in ALLOWED_FAMILIES:
            errors.append(f"unknown family at row {i}")
        if call.get("stage") not in ALLOWED_STAGES:
            errors.append(f"unknown stage at row {i}")
        dep=call.get("depends_on")
        deps=dep if isinstance(dep, list) else ([] if dep is None else [dep])
        if any(not isinstance(x, int) or x < 1 or x >= i for x in deps):
            errors.append(f"invalid dependency at row {i}")
        if call.get("stage") == "PROPOSER" and deps:
            errors.append(f"proposer row must not have dependencies at row {i}")
        if call.get("stage") in {"V1", "V2"}:
            proposer_family = call.get("run_id", "").removeprefix(call.get("case_id", "") + "-")[:1]
            expected = next((x.get("sequence") for x in calls
                             if x.get("case_id") == call.get("case_id")
                             and x.get("stage") == "PROPOSER"
                             and x.get("family") == proposer_family), None)
            if deps != [expected]:
                errors.append(f"verifier must depend on its exact proposer for {call.get('run_id')}")
        if call.get("stage") == "RECOVERY" and deps != [25, 26, 27]:
            errors.append("recovery must depend on proposer, V1 and V2 outputs")
    providers=data.get("provider_families", {})
    if set(providers) != ALLOWED_FAMILIES:
        errors.append("provider family set must be exactly G/Z/O")
    if providers.get("Z", {}).get("model") != "@cf/zai-org/glm-4.7-flash":
        errors.append("Z must use the qualified Cloudflare GLM-4.7-Flash model ID")
    if any("mistral" in str(x).lower() for x in providers.values()):
        errors.append("Mistral must not appear as an active provider")
    policy=data.get("zero_spend_policy", {})
    if policy.get("api_spend_usd_max") != 0 or policy.get("billing_activation") is not False:
        errors.append("zero-spend policy was weakened")
    if policy.get("paid_fallback") is not False or policy.get("automatic_model_substitution") is not False:
        errors.append("paid fallback or automatic substitution must remain disabled")
    if data.get("status") != "BLOCKED_NOT_EXECUTABLE":
        errors.append("manifest must remain blocked pending account and case-ID gates")
    if not data.get("blocking_issues"):
        errors.append("blocking issues must be explicit")
    cases_path=Path(__file__).with_name("routing_cases_v0.json")
    if cases_path.exists():
        routing=json.loads(cases_path.read_text(encoding="utf-8"))
        case_rows=routing.get("cases",[])
        expected_cases={f"DR-0{i}" for i in range(1,7)}
        actual_cases={x.get("case_id") for x in case_rows}
        if actual_cases != expected_cases:
            errors.append("routing fixture bank must contain DR-01…DR-06 exactly once")
        if len(case_rows)!=6:
            errors.append("routing fixture bank must contain six disposable cases")
        if any(x.get("dataset_role")=="SCORED" for x in case_rows):
            errors.append("disposable routing fixtures cannot be scored")
        if data.get("routing_case_file") != cases_path.name:
            errors.append("manifest must point to the recovered routing fixture file")
        if data.get("calls") and {x.get("case_id") for x in data["calls"]} != expected_cases:
            errors.append("28-call route case IDs do not match recovered disposable fixtures")
    else:
        errors.append("recovered DR-01…DR-06 routing fixture file is missing")
    return errors

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", default=str(Path(__file__).with_name("dry_run_manifest_v2.json")))
    args=parser.parse_args()
    data=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    errors=validate(data)
    if errors:
        print("FAIL")
        for error in errors: print(f"- {error}")
        return 1
    print(f"PASS: {EXPECTED} rows, unique IDs, valid dependencies, G/Z/O routing, zero-spend guardrails.")
    print("NOTE: structural validity is not execution authorization; manifest remains blocked.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
