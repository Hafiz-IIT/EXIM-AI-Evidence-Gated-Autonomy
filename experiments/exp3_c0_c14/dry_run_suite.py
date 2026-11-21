"""Six disposable DRY-01…DRY-06 mechanical checks. No provider/network calls."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from harness_core import normalize_json, render_prompt, append_raw_attempt, retryable_transport_failure

def fake_retry_sequence():
    # Injected transport outcomes: timeout, 429, then a successful response.
    outcomes=[{"error_type":"timeout_before_complete_response"},{"http_status":429},{"http_status":200,"raw_text":'{"ok":true}'}]
    attempts=[]
    for index,outcome in enumerate(outcomes):
        attempts.append(outcome)
        if outcome.get("http_status")==200:
            return attempts, normalize_json(outcome["raw_text"])
        if not retryable_transport_failure(outcome.get("http_status"),outcome.get("error_type")):
            break
        if index>=2: break
    return attempts,None

def run_offline_checks():
    checks={}
    # DRY-01: successful structured proposer output parses.
    checks["DRY-01"]=normalize_json('{"proposed_action":"hold"}')=={"proposed_action":"hold"}

    # DRY-02: recovery request is explicitly linked to original output/intervention/new evidence.
    case={"case_id":"DRY-02","task":"reversible synthetic label update","consequence":"LOW","reversibility":"reversible","evidence_packet":"one current field is missing"}
    proposal={"proposed_action":"request field"}
    recovery=render_prompt("RECOVERY",case,proposal,"missing_critical_evidence","authoritative field value")
    body=recovery["messages"][1]["content"]
    checks["DRY-02"]=all(x in body for x in ["original_model_output","controller_intervention_category","newly_supplied_evidence"])

    # DRY-03: conflicting model outputs remain separate append-only records.
    with tempfile.TemporaryDirectory() as folder:
        ledger=str(Path(folder)/"raw.jsonl")
        append_raw_attempt(ledger,{"run_id":"DRY-03-V1","raw_text":"ACCEPT"})
        append_raw_attempt(ledger,{"run_id":"DRY-03-V2","raw_text":"REJECT"})
        records=[json.loads(x) for x in Path(ledger).read_text(encoding="utf-8").splitlines()]
        checks["DRY-03"]=len(records)==2 and records[0]["raw_text"]=="ACCEPT" and records[1]["raw_text"]=="REJECT"

    # DRY-04: timestamps are not parsed/reformatted or silently corrected.
    timestamp="2026-09-17T13:45:00Z"
    parsed=normalize_json(json.dumps({"approval_timestamp":timestamp}))
    checks["DRY-04"]=parsed["approval_timestamp"]==timestamp

    # DRY-05: injected retryable transport failures are retried, each attempt retained.
    attempts,result=fake_retry_sequence()
    checks["DRY-05"]=len(attempts)==3 and result=={"ok":True}

    # DRY-06: exact outer fence is removable; malformed JSON remains a failure.
    fence_ok=normalize_json('```json\n{"ok":true}\n```')=={"ok":True}
    try:
        normalize_json('{"ok":')
        malformed_fails=False
    except json.JSONDecodeError:
        malformed_fails=True
    checks["DRY-06"]=fence_ok and malformed_fails
    return checks

if __name__=="__main__":
    results=run_offline_checks()
    for key,value in results.items(): print(f"{key}: {'PASS' if value else 'FAIL'}")
    raise SystemExit(0 if all(results.values()) else 1)
