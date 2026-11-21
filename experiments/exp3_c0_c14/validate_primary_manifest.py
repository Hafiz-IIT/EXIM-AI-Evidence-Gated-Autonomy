#!/usr/bin/env python3
"""Offline validator for the proposed 630-call C0-C14 primary matrix."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

EXPECTED={"3A":90,"3B":90,"3C":90,"3D":180,"3E":180}
FAMILIES={"A","B","C"}

def validate(manifest:dict,cases:dict)->list[str]:
    errors=[]
    calls=manifest.get("calls",[])
    if len(calls)!=630: errors.append("primary matrix must contain exactly 630 calls")
    ids=[x.get("run_id") for x in calls]
    if len(ids)!=len(set(ids)): errors.append("duplicate run_id")
    counts={stage:sum(x.get("stage")==stage for x in calls) for stage in EXPECTED}
    if counts!=EXPECTED: errors.append(f"stage counts mismatch: {counts}")
    case_ids={x.get("case_id") for x in cases.get("cases",[])}
    if len(case_ids)!=30: errors.append("public case bank must contain 30 cases")
    if {x.get("case_id") for x in calls}!=case_ids: errors.append("manifest case set differs from frozen public case bank")
    for call in calls:
        f=call.get("proposer_family")
        role=call.get("role")
        if f not in FAMILIES or call.get("model_family") not in FAMILIES: errors.append(f"unknown family in {call.get('run_id')}")
        dep=call.get("depends_on")
        if call.get("stage")=="3A":
            if role!="PROPOSER" or dep is not None: errors.append(f"bad proposer row {call.get('run_id')}")
        else:
            if dep not in ids: errors.append(f"unresolved dependency {call.get('run_id')}")
            if role not in {"V1","V2"}: errors.append(f"bad verifier role {call.get('run_id')}")
        if call.get("stage")=="3B" and (call.get("model_family")!=f or role!="V1"): errors.append("3B must be same-family V1")
        if call.get("stage")=="3C" and (call.get("model_family")!={"A":"B","B":"C","C":"A"}[f] or role!="V1"): errors.append("3C rotation/role mismatch")
        if call.get("stage")=="3D" and call.get("model_family")!=f: errors.append("3D must use same-family verifiers")
        if call.get("stage")=="3E" and call.get("model_family")==f: errors.append("3E must use non-proposer families")
    if manifest.get("status")!="BLOCKED_NOT_EXECUTABLE": errors.append("draft must remain blocked")
    if manifest.get("zero_spend_policy",{}).get("api_spend_usd_max")!=0: errors.append("zero-spend cap missing")
    if not manifest.get("operational_role_interpretation",{}).get("note"): errors.append("role interpretation must be disclosed")
    return errors

def main()->int:
    here=Path(__file__).parent
    parser=argparse.ArgumentParser()
    parser.add_argument("manifest",nargs="?",default="primary_run_manifest_v2_draft.json")
    args=parser.parse_args()
    manifest=json.loads((here/args.manifest).read_text(encoding="utf-8"))
    cases=json.loads((here/"cases_public_v1.json").read_text(encoding="utf-8"))
    errors=validate(manifest,cases)
    if errors:
        print("FAIL")
        for e in errors: print("- "+e)
        return 1
    print("PASS: 630 unique calls; 30 cases; 90/90/90/180/180 stage counts; provider-family routing valid.")
    print("BLOCKED: this validates structure only, not account eligibility, prompt completeness or authorization to execute.")
    return 0
if __name__=="__main__": raise SystemExit(main())
