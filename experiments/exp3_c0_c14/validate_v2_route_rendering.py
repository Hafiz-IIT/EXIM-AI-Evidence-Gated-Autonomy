"""Offline Prompt Pack v2 rendering acceptance for the 28-call route; no network."""
from __future__ import annotations
import json
from pathlib import Path
from prompt_pack_v2 import render_prompt_v2

HERE=Path(__file__).resolve().parent
ROLES={"PROPOSER":"PROPOSER","V1":"V1","V2":"V2","RECOVERY":"RECOVERY"}

def stub_proposer():
    return {
      "proposed_action":"offline fixture only","self_confidence":0.5,"evidence_used":[],
      "missing_evidence":[],"conflicts_detected":[],"freshness_concerns":[],
      "provenance_concerns":[],"dependency_concerns":[],"authorization_evidence":[],
      "recommended_gate_action":"DEFER"
    }

def validate():
    manifest=json.loads((HERE/"dry_run_manifest_v3_draft.json").read_text(encoding="utf-8"))
    cases=json.loads((HERE/"routing_cases_v0.json").read_text(encoding="utf-8"))["cases"]
    by_id={case["case_id"]:case for case in cases}
    proposer_outputs={case_id:stub_proposer() for case_id in by_id}
    hashes=[]
    rendered=[]
    for call in manifest["calls"]:
        case=by_id[call["case_id"]]
        role=ROLES[call["stage"]]
        if role=="PROPOSER":
            prompt=render_prompt_v2(role,case)
        elif role in {"V1","V2"}:
            prompt=render_prompt_v2(role,case,proposer_outputs[call["case_id"]])
        else:
            prompt=render_prompt_v2(role,case,proposer_outputs[call["case_id"]],
                intervention="offline route-render acceptance only",
                new_evidence=case.get("recovery_target","synthetic recovery evidence fixture"))
        serialized=json.dumps(prompt["messages"],ensure_ascii=False,sort_keys=True)
        if call["case_id"] in serialized or "case_id" in serialized:
            raise AssertionError(f"case metadata leaked into prompt: {call['run_id']}")
        if prompt["prompt_version"]!="Prompt Pack v2" or len(prompt["prompt_sha256"])!=64:
            raise AssertionError(f"bad prompt version/hash: {call['run_id']}")
        hashes.append(prompt["prompt_sha256"])
        rendered.append({"run_id":call["run_id"],"role":role,"hash":prompt["prompt_sha256"]})
    if len(rendered)!=28:
        raise AssertionError(f"expected 28 rendered prompts, got {len(rendered)}")
    if len(set(x["run_id"] for x in rendered))!=28:
        raise AssertionError("duplicate run IDs in rendered route")
    if len(set(hashes))!=28:
        raise AssertionError("rendered prompt hashes are not unique")
    return {"rendered_calls":len(rendered),"unique_prompt_hashes":len(set(hashes)),"provider_calls":0,"status":"PASS_OFFLINE_RENDER_ONLY"}

if __name__=="__main__":
    result=validate()
    print(json.dumps(result,indent=2))
