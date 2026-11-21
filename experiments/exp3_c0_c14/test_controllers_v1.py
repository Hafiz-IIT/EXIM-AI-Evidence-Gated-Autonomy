import unittest
from controllers_v1 import (
    b1_always_act, b2_confidence_threshold, b3_agreement_gate, b4_always_verify,
    b5_selective_confidence, b6_strong_verifier_gate, b7_risk_gate,
    b8_evidence_gate, evaluate_controller,
)

def status(value="SUPPORTED", refs=None):
    return {"status": value, "basis": "explicit synthetic packet evidence", "evidence_refs": refs or ["current deployment authorization"]}

def role_v1(auth="SUPPORTED", freshness="SUPPORTED", reversibility="SUPPORTED", **extra):
    x = {
        "proposal_supported": True, "authorization_sufficient": True,
        "recommended_gate_action": "ACT",
        "authorization_status": status(auth),
        "freshness_status": status(freshness),
        "reversibility_status": status(reversibility),
    }
    x.update(extra)
    return x

def role_v2(provenance="SUPPORTED", independence="SUPPORTED", grounding="SUPPORTED", consistency="SUPPORTED", **extra):
    x = {
        "provenance_status": status(provenance), "independence_status": status(independence),
        "grounding_status": status(grounding), "consistency_status": status(consistency),
    }
    x.update(extra)
    return x

class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.case={"consequence":"HIGH","reversibility":"reversible_with_rollback_plan","evidence_packet":"Signed test report; current deployment authorization; matching build hash."}
        self.p={"self_confidence":0.9,"recommended_gate_action":"ACT"}
        self.v1=role_v1()
        self.v2=role_v2()

    def test_b1_b4(self):
        self.assertEqual(b1_always_act(),"ACT")
        self.assertEqual(b4_always_verify(),"VERIFY")

    def test_b2_boundaries_and_invalid(self):
        for c in (0,0.899999,None,"0.9",True,float("nan"),float("inf"),-0.1,1.1):
            self.assertEqual(b2_confidence_threshold({"self_confidence":c}),"DEFER")
        self.assertEqual(b2_confidence_threshold({"self_confidence":0.9}),"ACT")
        self.assertEqual(b2_confidence_threshold({"self_confidence":1}),"ACT")

    def test_b3_two_of_three_exact_enum_and_abstentions(self):
        self.assertEqual(b3_agreement_gate({"recommended_gate_action":"ACT"},{"recommended_gate_action":" act "},{"recommended_gate_action":"VERIFY"}),"ACT")
        self.assertEqual(b3_agreement_gate({"recommended_gate_action":"ACT"},{"recommended_gate_action":"VERIFY"},{"recommended_gate_action":"VERIFY"}),"VERIFY")
        self.assertEqual(b3_agreement_gate({"recommended_gate_action":"ACT"},{"recommended_gate_action":"DEFER"},{"recommended_gate_action":"ESCALATE"}),"VERIFY")
        self.assertEqual(b3_agreement_gate({"recommended_gate_action":"ACT"},{"recommended_gate_action":"bad"},None),"VERIFY")
        self.assertEqual(b3_agreement_gate({"recommended_gate_action":"REQUEST EVIDENCE"},{"recommended_gate_action":"REQUEST EVIDENCE"},None),"REQUEST EVIDENCE")

    def test_b5_band_edges(self):
        self.assertEqual(b5_selective_confidence({"self_confidence":0.749999}),"DEFER")
        self.assertEqual(b5_selective_confidence({"self_confidence":0.75}),"VERIFY")
        self.assertEqual(b5_selective_confidence({"self_confidence":0.899999}),"VERIFY")
        self.assertEqual(b5_selective_confidence({"self_confidence":0.9}),"ACT")
        self.assertEqual(b5_selective_confidence({"self_confidence":None}),"DEFER")

    def test_b6_requires_v1_authorization_and_acceptance(self):
        self.assertEqual(b6_strong_verifier_gate(self.v1),"ACT")
        self.assertEqual(b6_strong_verifier_gate(role_v1(auth="UNKNOWN")),"DEFER")
        self.assertEqual(b6_strong_verifier_gate(role_v1(auth="CONTRADICTED")),"REQUEST EVIDENCE")
        self.assertEqual(b6_strong_verifier_gate(role_v1(auth="SUPPORTED",authorization_sufficient=False)),"REQUEST EVIDENCE")
        self.assertEqual(b6_strong_verifier_gate(role_v1(auth="SUPPORTED",proposal_supported=False)),"VERIFY")
        self.assertEqual(b6_strong_verifier_gate(None),"DEFER")

    def test_b7_risk_and_confidence(self):
        self.assertEqual(b7_risk_gate({"consequence":"HIGH"},self.p),"VERIFY")
        self.assertEqual(b7_risk_gate({"consequence":"LOW"},self.p),"ACT")
        self.assertEqual(b7_risk_gate({"consequence":"LOW"},{"self_confidence":0.89999}),"DEFER")
        self.assertEqual(b7_risk_gate({"consequence":"LOW"},{"self_confidence":None}),"DEFER")
        self.assertEqual(b7_risk_gate({"consequence":"UNKNOWN"},self.p),"ESCALATE")

    def test_b8_clean_positive_packet(self):
        self.assertEqual(b8_evidence_gate(self.case,self.p,self.v1,self.v2),"ACT")

    def test_b8_provenance_compromise_precedence(self):
        self.assertEqual(b8_evidence_gate(self.case,self.p,self.v1,role_v2(provenance="CONTRADICTED",independence="CONTRADICTED")),"ESCALATE")

    def test_b8_authorization_and_freshness_request_evidence(self):
        self.assertEqual(b8_evidence_gate(self.case,self.p,role_v1(auth="CONTRADICTED"),self.v2),"REQUEST EVIDENCE")
        self.assertEqual(b8_evidence_gate(self.case,self.p,role_v1(freshness="CONTRADICTED"),self.v2),"REQUEST EVIDENCE")

    def test_b8_conflict_and_common_mode(self):
        self.assertEqual(b8_evidence_gate(self.case,self.p,self.v1,role_v2(consistency="CONTRADICTED")),"VERIFY")
        self.assertEqual(b8_evidence_gate(self.case,self.p,self.v1,role_v2(independence="CONTRADICTED")),"VERIFY")

    def test_b8_grounding_and_unknowns(self):
        self.assertEqual(b8_evidence_gate(self.case,self.p,self.v1,role_v2(grounding="CONTRADICTED")),"REQUEST EVIDENCE")
        self.assertEqual(b8_evidence_gate(self.case,self.p,role_v1(reversibility="UNKNOWN"),self.v2),"DEFER")
        self.assertEqual(b8_evidence_gate({"consequence":"LOW"},self.p,role_v1(reversibility="UNKNOWN"),self.v2),"DEFER")
        self.assertEqual(b8_evidence_gate(self.case,self.p,role_v1(auth="UNKNOWN"),self.v2),"DEFER")

    def test_b8_false_reject_boolean_does_not_override_typed_evidence(self):
        false_reject=role_v1(proposal_supported=False,recommended_gate_action="VERIFY")
        self.assertEqual(b8_evidence_gate(self.case,self.p,false_reject,self.v2),"ACT")

    def test_b8_malformed_status_fails_closed(self):
        malformed=role_v2()
        malformed["provenance_status"]={"status":"SUPPORTED","basis":"","evidence_refs":[]}
        self.assertEqual(b8_evidence_gate(self.case,self.p,self.v1,malformed),"ESCALATE")
        malformed=role_v2()
        malformed["consistency_status"]={"status":"SUPPORTED","basis":"ok","evidence_refs":[]}
        self.assertEqual(b8_evidence_gate(self.case,self.p,self.v1,malformed),"ESCALATE")
        self.assertEqual(b8_evidence_gate(self.case,self.p,None,self.v2),"ESCALATE")

    def test_unknown_consequence_and_invalid_controller(self):
        self.assertEqual(b8_evidence_gate({"consequence":"MEDIUM"},self.p,self.v1,self.v2),"ESCALATE")
        with self.assertRaises(ValueError):
            evaluate_controller("B9",self.case,self.p,self.v1,self.v2)

if __name__ == "__main__":
    unittest.main()
