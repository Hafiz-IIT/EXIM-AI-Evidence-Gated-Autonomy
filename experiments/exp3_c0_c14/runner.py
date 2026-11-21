"""Safe CLI entry point for recovered C0-C14 Experiment 3.

Default behavior is plan-only. This version intentionally refuses model execution:
provider account entitlements and end-to-end provider dry-run acceptance are not yet verified.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load_json(name):
    return json.loads((HERE/name).read_text(encoding="utf-8"))

def build_plan(kind:str)->dict:
    if kind in {"routing","routing-v3"}:
        manifest=load_json("dry_run_manifest_v3_draft.json" if kind=="routing-v3" else "dry_run_manifest_v2.json")
        cases=load_json("routing_cases_v0.json")["cases"]
    else:
        manifest=load_json("primary_run_manifest_v3_draft.json" if kind=="primary-v3" else "primary_run_manifest_v2_draft.json")
        cases=load_json("cases_public_v1.json")["cases"]
    by_id={x["case_id"]:x for x in cases}
    unknown=sorted({x["case_id"] for x in manifest["calls"]}-set(by_id))
    if unknown: raise ValueError("manifest has unknown cases: "+", ".join(unknown))
    rows=[]
    for call in manifest["calls"]:
        provider_code=call.get("family") or call.get("model_family")
        provider=manifest.get("provider_families",{}).get(provider_code)
        if provider is None:
            provider=load_json("primary_run_manifest_v3_draft.json" if kind=="primary-v3" else "primary_run_manifest_v2_draft.json")["providers"].get(provider_code)
        rows.append({
          "sequence":call["sequence"],"run_id":call["run_id"],"case_id":call["case_id"],
          "stage":call["stage"],"role":call.get("role",call["stage"]),
          "family":provider_code,"model":provider["model"] if provider else None,
          "depends_on":call.get("depends_on")
        })
    return {"status":"PLAN_ONLY_NO_NETWORK","manifest_id":manifest["manifest_id"],"manifest_status":manifest["status"],"calls":len(rows),"rows":rows,"execution_enabled":False,"blocking_issues":manifest.get("blocking_issues",[])}

def execute(_plan):
    raise RuntimeError("EXECUTION BLOCKED: this runner version is plan-only. Do not bypass the v2 prompt/controller/analysis freeze, provider dry-run, and Free/quota gates.")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",choices=("routing","routing-v3","primary","primary-v3"),default="routing-v3")
    parser.add_argument("--plan-only",action="store_true",help="Print the deterministic plan; default behavior.")
    parser.add_argument("--execute",action="store_true",help="Refused until all frozen scientific and zero-cost gates are satisfied.")
    args=parser.parse_args()
    plan=build_plan(args.manifest)
    if args.execute: execute(plan)
    print(json.dumps({k:v for k,v in plan.items() if k!="rows"}|{"first_rows":plan["rows"][:5]},indent=2))
    print("No provider requests were made.")

if __name__=="__main__":
    main()
