import unittest
from feature_mapper import map_evidence_features

class FeatureMapperTests(unittest.TestCase):
    def setUp(self):
        self.case={"consequence":"HIGH","reversibility":"irreversible unless rollback is proven"}
        self.proposer={"missing_evidence":["current approval"],"conflicts_detected":[],"freshness_concerns":[],"provenance_concerns":[],"dependency_concerns":["shared identity provider"],"authorization_evidence":[]}
        self.v1={"critical_missing_evidence":["current approval"],"freshness_failures":[],"consequence_mismatch":[],"reversibility_concerns":["rollback not demonstrated"],"false_assumptions":[],"proposal_supported":False,"authorization_sufficient":False}
        self.v2={"provenance_concerns":[],"dependency_concerns":["same identity provider"],"contradictions":[],"possible_common_mode_failures":["shared identity provider"],"grounding_sufficient":False,"proposal_supported":False,"evidence_consistent":True}

    def test_explicit_fields_map_without_action_decision(self):
        result=map_evidence_features(self.case,self.proposer,self.v1,self.v2)
        self.assertEqual(result["mapping_status"],"valid")
        self.assertEqual(result["features"]["completeness"]["missing_evidence"],["current approval"])
        self.assertFalse(result["features"]["grounding"]["sufficient"])
        self.assertEqual(result["features"]["independence"]["common_mode_failures"],["shared identity provider"])
        self.assertNotIn("controller_action",result)

    def test_missing_verifier_output_is_not_treated_as_acceptance(self):
        result=map_evidence_features(self.case,self.proposer,None,None)
        self.assertEqual(result["mapping_status"],"incomplete")
        self.assertIn("v1:missing_verifier_output",result["mapping_errors"])
        self.assertIsNone(result["features"]["grounding"]["sufficient"])
        self.assertIsNone(result["features"]["verifier_status"]["v1_authorization_sufficient"])

    def test_missing_reversibility_is_explicit_error(self):
        case={"consequence":"LOW","reversibility":None}
        result=map_evidence_features(case,self.proposer,self.v1,self.v2)
        self.assertEqual(result["mapping_status"],"incomplete")
        self.assertIn("case.reversibility:missing_or_invalid",result["mapping_errors"])

if __name__=="__main__": unittest.main()
