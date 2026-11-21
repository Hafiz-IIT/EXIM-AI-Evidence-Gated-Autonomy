"""Offline render all 630 E3 v2 primary prompts; no network or provider calls."""
from __future__ import annotations
import json
from pathlib import Path
from prompt_pack_v2 import render_prompt_v2

HERE=Path(__file__).resolve().parent

def stub_proposer():
    return {"proposed_action":"offline fixture only","self_confidence":0.5,"evidence_used":[],
      "missing_evidence":[],"conflicts_detected":[],"freshness_concerns":[],"provenance_concerns":[],
      "dependency_concerns":[],"authorization_evidence":[],"recommended_gate_action":"DEFER"}

def validate():
    manifest=json.loads((HERE/"primary_run_manifest_v3_draft.json").read_text(encoding="utf-8"))
    cases=json.loads((HERE/"cases_public_v1.json").read_text(encoding="utf-8"))["cases"]
    by_id={case["case_id"]:case for case in cases}
    proposal=stub_proposer()
    rendered=0
    unknown_reversibility_cases={cid for cid,case in by_id.items() if case.get("reversibility") is None}
    unknown_seen=set()
    for call in manifest["calls"]:
        case=by_id[call["case_id"]]
        role=call["role"]
        if role=="PROPOSER":
            prompt=render_prompt_v2("PROPOSER",case)
        elif role in {"V1","V2"}:
            prompt=render_prompt_v2(role,case,proposal)
        else:
            raise AssertionError(f"unexpected role in primary manifest: {role}")
        serialized=json.dumps(prompt["messages"],ensure_ascii=False,sort_keys=True)
        if call["case_id"] in serialized or "case_id" in serialized:
            raise AssertionError(f"case metadata leaked into prompt: {call['run_id']}")
        if prompt["prompt_version"]!="Prompt Pack v2" or len(prompt["prompt_sha256"])!=64:
            raise AssertionError(f"bad rendered prompt metadata: {call['run_id']}")
        if call["case_id"] in unknown_reversibility_cases:
            if "NOT_SPECIFIED_IN_FROZEN_SOURCE" not in serialized:
                raise AssertionError(f"UNKNOWN reversibility sentinel missing: {call['run_id']}")
            unknown_seen.add(call["case_id"])
        rendered+=1
    if rendered!=630:
        raise AssertionError(f"expected 630 rendered prompts, got {rendered}")
    if unknown_seen!=unknown_reversibility_cases:
        raise AssertionError("not all 12 source-unknown reversibility cases were rendered")
    return {"rendered_prompts":rendered,"unknown_reversibility_cases":len(unknown_seen),"provider_calls":0,"status":"PASS_OFFLINE_RENDER_ONLY"}

if __name__=="__main__":
    print(json.dumps(validate(),indent=2))
