"""Guarded local executor for the 28-call E3 v2 provider dry run.

Default is plan-only. Execution requires explicit CLI confirmation, a local account
qualification file, local environment secrets, and all three Free/no-overage gates.
No fallback, billing activation, automatic substitution, or scored-run execution.
"""
from __future__ import annotations
import argparse
import base64
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from harness_core import append_raw_attempt, make_idempotency_key, normalize_json, retryable_transport_failure
from prompt_pack_v2 import render_prompt_v2, validate_role_payload_v2
from provider_adapters import (
    ProviderError, assert_free_only_entitlements, build_request,
    dispatch_free_only, extract_text,
)

HERE=Path(__file__).resolve().parent
MANIFEST_PATH=HERE/"dry_run_manifest_v3_draft.json"
CASES_PATH=HERE/"routing_cases_v0.json"
LOCAL_CONFIG=HERE/"provider_config.local.json"
DEFAULT_LEDGER=HERE/".local"/"exp3_c0_c14"/"dry_run_v3_raw.jsonl"
ALLOWED_FAMILIES={"G":"A","Z":"B","O":"C"}

def load_json(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def build_plan():
    manifest=load_json(MANIFEST_PATH)
    cases=load_json(CASES_PATH)["cases"]
    case_ids={x["case_id"] for x in cases}
    if {x["case_id"] for x in manifest["calls"]}-case_ids:
        raise ValueError("dry-run manifest references an unknown routing case")
    return {"manifest_id":manifest["manifest_id"],"calls":len(manifest["calls"]),
            "provider_calls":0,"status":"PLAN_ONLY_NO_NETWORK"}

def validate_local_config(config:dict,manifest:dict,env:dict|None=None):
    env=os.environ if env is None else env
    if config.get("execution_enabled") is not True:
        raise RuntimeError("local provider_config.execution_enabled must be explicitly true after dashboard verification")
    defaults=config.get("defaults",{})
    if defaults.get("temperature") != 0:
        raise RuntimeError("temperature must be exactly 0")
    if defaults.get("max_output_tokens",0) > 1024 or defaults.get("max_output_tokens",0) < 1:
        raise RuntimeError("max_output_tokens must be in [1,1024] for the first dry run")
    if defaults.get("timeout_seconds",0) < 1 or defaults.get("timeout_seconds",0) > 60:
        raise RuntimeError("timeout_seconds must be in [1,60]")
    if defaults.get("external_tools") is not False:
        raise RuntimeError("external tools must be disabled")
    assert_free_only_entitlements(config)
    aliases=config.get("routing_family_aliases",{})
    if aliases != ALLOWED_FAMILIES:
        raise RuntimeError("routing family aliases must be exactly G->A, Z->B, O->C")
    manifest_providers=manifest.get("provider_families",{})
    providers=config.get("provider_families",{})
    for route_code,canonical in ALLOWED_FAMILIES.items():
        expected=manifest_providers[route_code]
        actual=providers.get(canonical,{})
        if actual.get("model") != expected.get("model"):
            raise RuntimeError(f"provider {canonical} model does not match the pinned dry-run model")
        build_request(canonical,actual,[{"role":"user","content":"offline preflight only"}],env,
                      temperature=0.0,max_output_tokens=16)
    return True

def _now():
    return datetime.now(timezone.utc).isoformat()

def execute_dry_run(config:dict,ledger_path:Path,env:dict|None=None,opener=None):
    """Execute only the v3 28-call dry run. The opener is injectable for offline tests."""
    from urllib.request import urlopen
    env=os.environ if env is None else env
    manifest=load_json(MANIFEST_PATH)
    routing=load_json(CASES_PATH)["cases"]
    by_case={x["case_id"]:x for x in routing}

    ledger_path=Path(ledger_path)
    if ledger_path.exists() and ledger_path.stat().st_size:
        raise RuntimeError("refusing to reuse a non-empty ledger; do not duplicate provider calls")
    validate_local_config(config,manifest,env)

    defaults=config["defaults"]
    timeout=defaults["timeout_seconds"]
    max_tokens=defaults["max_output_tokens"]
    temperature=defaults["temperature"]
    alias_map=config["routing_family_aliases"]
    outputs_by_case={}
    completed=0

    for call in manifest["calls"]:
        case=by_case[call["case_id"]]
        role=call["stage"]
        if role=="PROPOSER":
            prompt=render_prompt_v2("PROPOSER",case)
        elif role in {"V1","V2"}:
            if call["case_id"] not in outputs_by_case:
                raise RuntimeError(f"missing proposer output dependency for {call['case_id']}")
            prompt=render_prompt_v2(role,case,outputs_by_case[call["case_id"]])
        elif role=="RECOVERY":
            if call["case_id"] not in outputs_by_case:
                raise RuntimeError(f"missing proposer output dependency for {call['case_id']}")
            prompt=render_prompt_v2("RECOVERY",case,outputs_by_case[call["case_id"]],
                intervention="REQUEST_EVIDENCE_AFTER_INITIAL_GATE",
                new_evidence=case.get("recovery_target",""))
        else:
            raise RuntimeError(f"unsupported dry-run role: {role}")

        route_family=call["family"]
        family=alias_map[route_family]
        provider=config["provider_families"][family]
        model=provider["model"]
        request=build_request(family,provider,prompt["messages"],env,
                              temperature=temperature,max_output_tokens=max_tokens)
        opener_fn=urlopen if opener is None else opener
        last_error=None
        for attempt in range(3):
            idempotency=make_idempotency_key(
                "E3-C0-C14-v2-dryrun",call["case_id"],family,model,role,
                "V1-V2-v2","Prompt Pack v2",attempt
            )
            def persist_raw(raw,status):
                append_raw_attempt(str(ledger_path),{
                    "event":"raw_http_response","timestamp_utc":_now(),
                    "run_id":call["run_id"],"sequence":call["sequence"],
                    "attempt_index":attempt,"idempotency_key":idempotency,
                    "provider_family":family,"provider":provider["provider"],
                    "model":model,"prompt_version":"Prompt Pack v2",
                    "prompt_sha256":prompt["prompt_sha256"],
                    "http_status":status,"raw_response_b64":base64.b64encode(raw).decode("ascii")
                })
            started=time.perf_counter()
            try:
                response=dispatch_free_only(request,config,timeout_seconds=timeout,
                    opener=opener_fn,raw_sink=persist_raw)
            except ProviderError as exc:
                last_error=exc
                append_raw_attempt(str(ledger_path),{
                    "event":"provider_error","timestamp_utc":_now(),
                    "run_id":call["run_id"],"sequence":call["sequence"],
                    "attempt_index":attempt,"idempotency_key":idempotency,
                    "provider_family":family,"model":model,
                    "http_status":exc.http_status,"error_type":exc.error_type,
                    "error":str(exc)
                })
                if attempt<2 and retryable_transport_failure(exc.http_status,exc.error_type):
                    continue
                raise
            elapsed_ms=round((time.perf_counter()-started)*1000,2)
            extracted=extract_text(family,response["response_json"])
            append_raw_attempt(str(ledger_path),{
                "event":"extracted_model_text","timestamp_utc":_now(),
                "run_id":call["run_id"],"sequence":call["sequence"],
                "attempt_index":attempt,"idempotency_key":idempotency,
                "prompt_sha256":prompt["prompt_sha256"],
                "raw_text":extracted["raw_text"]
            })
            returned_model=extracted.get("provider_model")
            if returned_model and returned_model != model:
                append_raw_attempt(str(ledger_path),{
                    "event":"model_identity_mismatch","timestamp_utc":_now(),
                    "run_id":call["run_id"],"expected_model":model,"returned_model":returned_model
                })
                raise RuntimeError("provider returned a different model identity; automatic substitution is forbidden")
            try:
                parsed=normalize_json(extracted["raw_text"])
            except Exception as exc:
                append_raw_attempt(str(ledger_path),{
                    "event":"parse_failure","timestamp_utc":_now(),
                    "run_id":call["run_id"],"error_type":type(exc).__name__,"error":str(exc)
                })
                raise RuntimeError(f"malformed model JSON for {call['run_id']}; no semantic repair/retry") from exc
            schema_errors=validate_role_payload_v2(role,parsed)
            if schema_errors:
                append_raw_attempt(str(ledger_path),{
                    "event":"schema_failure","timestamp_utc":_now(),
                    "run_id":call["run_id"],"schema_errors":schema_errors
                })
                raise RuntimeError(f"Prompt Pack v2 schema failure for {call['run_id']}; no semantic repair/retry")
            append_raw_attempt(str(ledger_path),{
                "event":"call_completed","timestamp_utc":_now(),
                "run_id":call["run_id"],"sequence":call["sequence"],
                "attempt_index":attempt,"idempotency_key":idempotency,
                "provider_family":family,"provider":provider["provider"],"model":model,
                "prompt_version":"Prompt Pack v2","prompt_sha256":prompt["prompt_sha256"],
                "latency_ms":elapsed_ms,"http_status":response["http_status"],
                "usage":extracted.get("usage"),"provider_request_id":extracted.get("provider_request_id"),
                "parsed_output":parsed
            })
            if role=="PROPOSER":
                outputs_by_case[call["case_id"]]=parsed
            completed+=1
            break
        else:
            raise RuntimeError(f"provider call exhausted retries: {call['run_id']}") from last_error

    return {"manifest_id":manifest["manifest_id"],"completed_calls":completed,
            "ledger_path":str(ledger_path),"provider_calls":completed,
            "status":"PROVIDER_DRY_RUN_COMPLETED_NO_SCORED_CASES"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--execute",action="store_true",help="Perform the 28 provider calls; disabled unless all zero-cost gates pass.")
    parser.add_argument("--confirm-zero-spend",action="store_true",help="Explicitly confirm Free/no-overage dashboard checks and USD 0 spend policy.")
    parser.add_argument("--config",default=str(LOCAL_CONFIG))
    parser.add_argument("--ledger",default=str(DEFAULT_LEDGER))
    args=parser.parse_args()
    if not args.execute:
        print(json.dumps(build_plan(),indent=2))
        print("PLAN ONLY: no provider requests made.")
        return 0
    if not args.confirm_zero_spend:
        raise SystemExit("EXECUTION BLOCKED: pass --confirm-zero-spend only after verifying all three provider dashboards.")
    config=load_json(Path(args.config))
    result=execute_dry_run(config,Path(args.ledger))
    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
