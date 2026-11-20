import copy
import unittest

from scripts.generate_benchmark import make
from src.core import _canonical_hash, evidence_gate_v1, visible_features
from src.provenance import canonical_sha256


def clean_high_risk_case():
    underlying = make(0, "C0_clean", 0)
    return {
        "observable": copy.deepcopy(underlying["observable"]),
        "action": {"risk_level": "HIGH"},
    }


class EvidenceGateCompletenessTests(unittest.TestCase):
    def test_complete_consistent_case_can_act(self):
        case = clean_high_risk_case()
        self.assertTrue(visible_features(case)["complete"])
        self.assertEqual(evidence_gate_v1(case), "ACT")

    def test_string_false_verifier_decisions_fail_closed(self):
        case = clean_high_risk_case()
        for verifier in case["observable"]["machine"]["verifiers"]:
            verifier["accept"] = "false"
        self.assertFalse(visible_features(case)["verifier_schema_valid"])
        self.assertEqual(evidence_gate_v1(case), "ESCALATE")

    def test_missing_verifier_dependency_group_fails_closed(self):
        case = clean_high_risk_case()
        del case["observable"]["machine"]["verifiers"][0]["dependency_group"]
        self.assertFalse(visible_features(case)["verifier_schema_valid"])
        self.assertEqual(evidence_gate_v1(case), "ESCALATE")

    def test_low_risk_cannot_bypass_invalid_provenance(self):
        case = clean_high_risk_case()
        case["action"]["risk_level"] = "LOW"
        case["observable"]["provenance"] = {
            "integrity_status": "invalid",
            "document_set_sha256": "forged",
        }
        self.assertFalse(visible_features(case)["provenance_valid"])
        self.assertEqual(evidence_gate_v1(case), "ESCALATE")

    def test_low_risk_cannot_bypass_duplicate_document_kinds(self):
        case = clean_high_risk_case()
        case["action"]["risk_level"] = "LOW"
        case["observable"]["document_instances"] = [
            {"kind": "invoice"}, {"kind": "invoice"}
        ]
        self.assertTrue(visible_features(case)["duplicate_document_kind"])
        self.assertEqual(evidence_gate_v1(case), "ESCALATE")

    def test_unicode_document_hash_matches_attestation_canonicalization(self):
        payload = [{"kind": "invoice", "description": "Bengali বাংলা and export", "quantity": 3}]
        self.assertEqual(_canonical_hash(payload), canonical_sha256(payload))

    def test_missing_invoice_requests_evidence(self):
        case = clean_high_risk_case()
        case["observable"]["documents"]["invoice"] = None
        self.assertFalse(visible_features(case)["complete"])
        self.assertEqual(evidence_gate_v1(case), "REQUEST_EVIDENCE")

    def test_missing_packing_list_requests_evidence(self):
        case = clean_high_risk_case()
        case["observable"]["documents"]["packing_list"] = None
        self.assertFalse(visible_features(case)["complete"])
        self.assertEqual(evidence_gate_v1(case), "REQUEST_EVIDENCE")

    def test_missing_declaration_requests_evidence(self):
        case = clean_high_risk_case()
        case["observable"]["documents"]["declaration"] = None
        self.assertFalse(visible_features(case)["complete"])
        self.assertEqual(evidence_gate_v1(case), "REQUEST_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
