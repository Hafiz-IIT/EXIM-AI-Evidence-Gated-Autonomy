import json
import unittest
from harness_core import normalize_json, validate_role_payload, render_prompt, build_execution_plan

class HarnessCoreTests(unittest.TestCase):
    def test_plain_json(self):
        self.assertEqual(normalize_json('{"x":1}'), {"x":1})
    def test_bom_and_outer_fence(self):
        self.assertEqual(normalize_json('\ufeff```json\n{"x":1}\n```'), {"x":1})
    def test_malformed_json_stays_failure(self):
        with self.assertRaises(json.JSONDecodeError):
            normalize_json('{"x":1')
    def test_nested_or_extra_fence_not_repaired(self):
        with self.assertRaises(json.JSONDecodeError):
            normalize_json('prefix ```json\n{"x":1}\n```')
    def test_missing_keys_reported(self):
        errors=validate_role_payload("PROPOSER", {"self_confidence":0.5})
        self.assertTrue(any("missing required key" in x for x in errors))
    def test_unknown_action_rejected(self):
        obj={"proposed_action":"x","self_confidence":0.5,"evidence_used":[],"missing_evidence":[],"conflicts_detected":[],"freshness_concerns":[],"provenance_concerns":[],"dependency_concerns":[],"authorization_evidence":[],"recommended_gate_action":"MAGIC"}
        self.assertTrue(any("decision space" in x for x in validate_role_payload("PROPOSER",obj)))
    def test_reversibility_must_not_be_inferred(self):
        case={"case_id":"x","task":"t","consequence":"LOW","evidence_packet":"e"}
        with self.assertRaisesRegex(ValueError,"reversibility"):
            render_prompt("PROPOSER",case)
    def test_verifier_requires_frozen_proposal(self):
        case={"case_id":"x","task":"t","consequence":"LOW","evidence_packet":"e","reversibility":"reversible"}
        with self.assertRaisesRegex(ValueError,"frozen proposer"):
            render_prompt("V1",case)
    def test_prompt_hash_deterministic(self):
        case={"case_id":"x","task":"t","consequence":"LOW","evidence_packet":"e","reversibility":"reversible"}
        a=render_prompt("PROPOSER",case); b=render_prompt("PROPOSER",case)
        self.assertEqual(a["prompt_sha256"],b["prompt_sha256"])
    def test_plan_only(self):
        m={"calls":[{"case_id":"x"}]}
        p=build_execution_plan(m,[{"case_id":"x"}])
        self.assertEqual(p["status"],"PLAN_ONLY_NO_NETWORK")
        self.assertFalse(p["execution_enabled"])

if __name__=="__main__": unittest.main()
