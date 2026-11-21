import json
import tempfile
import unittest
from pathlib import Path

from execute_dry_run_v3 import (
    MANIFEST_PATH, build_plan, execute_dry_run, validate_local_config
)

def status():
    return {"status":"UNKNOWN","basis":"No supporting excerpt found; status remains UNKNOWN","evidence_refs":[]}

def output_for(role):
    if role=="PROPOSER":
        return {"proposed_action":"hold pending evidence","self_confidence":0.5,"evidence_used":[],
          "missing_evidence":["current authorization"],"conflicts_detected":[],"freshness_concerns":[],
          "provenance_concerns":[],"dependency_concerns":[],"authorization_evidence":[],
          "recommended_gate_action":"DEFER"}
    if role=="V1":
        return {"proposal_supported":False,"authorization_sufficient":False,"critical_missing_evidence":[],
          "freshness_failures":[],"freshness_event":"UNKNOWN","consequence_mismatch":[],
          "reversibility_concerns":[],"false_assumptions":[],"verifier_confidence":0.2,
          "recommended_gate_action":"DEFER","freshness_status":status(),
          "authorization_status":status(),"reversibility_status":status()}
    if role=="V2":
        return {"proposal_supported":False,"evidence_consistent":False,"grounding_sufficient":False,
          "provenance_concerns":[],"dependency_concerns":[],"contradictions":[],
          "possible_common_mode_failures":[],"verifier_confidence":0.2,"recommended_gate_action":"DEFER",
          "provenance_status":status(),"independence_status":status(),
          "grounding_status":status(),"consistency_status":status()}
    return {"blocking_uncertainty":"authorization missing","minimum_evidence_request":["current authorization"],
      "acceptable_source":["authenticated authority"],"unsafe_substitutes":["verbal assurance"],
      "next_gate_action_if_received_and_valid":"VERIFY"}

class FakeResponse:
    status=200
    def __init__(self,body): self.body=body
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self): return self.body

class FakeOpener:
    def __init__(self): self.calls=0
    def __call__(self,request,timeout=60):
        self.calls+=1
        if "generativelanguage.googleapis.com" in request.full_url:
            family="A"
            body=json.loads(request.data)
            prompt=body["contents"][0]["parts"][0]["text"]
        elif "api.cloudflare.com" in request.full_url:
            family="B"
            body=json.loads(request.data)
            prompt=body["messages"][-1]["content"]
        else:
            family="C"
            body=json.loads(request.data)
            prompt=body["messages"][-1]["content"]
        if prompt.startswith("Propose"):
            role="PROPOSER"
        elif prompt.startswith("Evaluate authorization"):
            role="V1"
        elif prompt.startswith("Evaluate provenance"):
            role="V2"
        else:
            role="RECOVERY"
        text=json.dumps(output_for(role),separators=(",",":"))
        if family=="A":
            response={"modelVersion":"gemini-2.5-flash","responseId":f"fake-{self.calls}",
              "candidates":[{"content":{"parts":[{"text":text}]},"finishReason":"STOP"}],
              "usageMetadata":{"promptTokenCount":1,"candidatesTokenCount":1}}
        else:
            response={"id":f"fake-{self.calls}","model":body["model"],
              "choices":[{"message":{"content":text},"finish_reason":"stop"}],
              "usage":{"prompt_tokens":1,"completion_tokens":1}}
        return FakeResponse(json.dumps(response).encode("utf-8"))

class ExecuteDryRunTests(unittest.TestCase):
    def setUp(self):
        self.manifest=json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.config={
          "execution_enabled":True,
          "routing_family_aliases":{"G":"A","Z":"B","O":"C"},
          "defaults":{"temperature":0,"max_output_tokens":1024,"timeout_seconds":60,
            "external_tools":False,"paid_fallback":False,"prepaid_credits":False,
            "automatic_model_substitution":False,"api_spend_usd_max":0},
          "provider_families":{}
        }
        for route,canonical in (("G","A"),("Z","B"),("O","C")):
            provider=dict(self.manifest["provider_families"][route])
            provider.update({"account_free_tier_verified":True,"billing_state":"free_no_paid_overage","quota_verified":True})
            self.config["provider_families"][canonical]=provider
        self.env={"GEMINI_API_KEY":"test-only","CLOUDFLARE_API_TOKEN":"test-only",
          "CLOUDFLARE_ACCOUNT_ID":"fake-account","GROQ_API_KEY":"test-only"}

    def test_plan_is_28_calls_and_no_network(self):
        plan=build_plan()
        self.assertEqual(plan["calls"],28)
        self.assertEqual(plan["provider_calls"],0)

    def test_unverified_config_fails_before_network(self):
        config=json.loads(json.dumps(self.config))
        config["provider_families"]["B"]["quota_verified"]=False
        with self.assertRaisesRegex(RuntimeError,"quota"):
            validate_local_config(config,self.manifest,self.env)

    def test_execution_flag_must_be_explicit(self):
        config=json.loads(json.dumps(self.config))
        config["execution_enabled"]=False
        with self.assertRaisesRegex(RuntimeError,"execution_enabled"):
            validate_local_config(config,self.manifest,self.env)

    def test_exact_model_identity_required(self):
        config=json.loads(json.dumps(self.config))
        config["provider_families"]["C"]["model"]="some-other-model"
        with self.assertRaisesRegex(RuntimeError,"pinned dry-run model"):
            validate_local_config(config,self.manifest,self.env)

    def test_full_28_call_flow_with_fake_transport_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/"raw.jsonl"
            fake=FakeOpener()
            result=execute_dry_run(self.config,ledger,self.env,opener=fake)
            self.assertEqual(result["completed_calls"],28)
            self.assertEqual(result["provider_calls"],28)
            self.assertEqual(fake.calls,28)
            rows=[json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(sum(x["event"]=="raw_http_response" for x in rows),28)
            self.assertEqual(sum(x["event"]=="call_completed" for x in rows),28)
            self.assertEqual(sum(x["event"]=="provider_error" for x in rows),0)
            self.assertEqual(sum(x["event"]=="run_started" for x in rows),1)
            self.assertEqual(sum(x["event"]=="run_completed" for x in rows),1)

    def test_nonempty_ledger_prevents_duplicate_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/"raw.jsonl"
            ledger.write_text('{"event":"existing"}\n',encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError,"non-empty ledger"):
                execute_dry_run(self.config,ledger,self.env,opener=lambda *a,**k: (_ for _ in ()).throw(AssertionError("network called")))

if __name__=="__main__": unittest.main()
