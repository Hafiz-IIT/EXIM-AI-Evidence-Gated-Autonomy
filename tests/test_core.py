import copy
import unittest

from scripts.generate_benchmark import make
from src.core import evidence_gate_v1, evidence_gate_v2, visible_features


def clean_high_risk_case():
    underlying = make(0, "C0_clean", 0)
    return {
        "observable": copy.deepcopy(underlying["observable"]),
        "action": {"risk_level": "HIGH"},
    }



class TrustedActionConsequenceTests(unittest.TestCase):
    CATALOG = {
        "save_temporary_record": {
            "risk_level": "LOW",
            "reversibility": "HIGH",
            "external_effect": "LOW",
        },
        "advance_operational_workflow": {
            "risk_level": "HIGH",
            "reversibility": "LOW",
            "external_effect": "HIGH",
        },
    }

    def test_risk_downgrade_cannot_bypass_high_risk_checks(self):
        case = clean_high_risk_case()
        case["observable"]["provenance"] = {
            "integrity_status": "corrupted",
            "document_set_sha256": "bad",
        }
        self.assertEqual(evidence_gate_v1(case), "ESCALATE")
        case["action"] = {
            "name": "advance_operational_workflow",
            "risk_level": "LOW",
            "reversibility": "LOW",
            "external_effect": "HIGH",
        }
        self.assertEqual(evidence_gate_v1(case), "ACT")
        self.assertEqual(
            evidence_gate_v2(
                case,
                trusted_action_id="advance_operational_workflow",
                trusted_action_catalog=self.CATALOG,
            ),
            "ESCALATE",
        )

    def test_action_name_must_match_independent_authorization_context(self):
        case = clean_high_risk_case()
        case["action"] = {
            "name": "save_temporary_record",
            "risk_level": "LOW",
            "reversibility": "HIGH",
            "external_effect": "LOW",
        }
        self.assertEqual(
            evidence_gate_v2(
                case,
                trusted_action_id="advance_operational_workflow",
                trusted_action_catalog=self.CATALOG,
            ),
            "ESCALATE",
        )

    def test_each_consequence_metadata_mismatch_fails_closed(self):
        for field, value in (
            ("risk_level", "LOW"),
            ("reversibility", "HIGH"),
            ("external_effect", "LOW"),
        ):
            case = clean_high_risk_case()
            case["action"] = {
                "name": "advance_operational_workflow",
                **self.CATALOG["advance_operational_workflow"],
            }
            case["action"][field] = value
            with self.subTest(field=field):
                self.assertEqual(
                    evidence_gate_v2(
                        case,
                        trusted_action_id="advance_operational_workflow",
                        trusted_action_catalog=self.CATALOG,
                    ),
                    "ESCALATE",
                )

    def test_unknown_action_or_missing_trusted_context_fails_closed(self):
        case = clean_high_risk_case()
        self.assertEqual(
            evidence_gate_v2(
                case,
                trusted_action_id="unknown-action",
                trusted_action_catalog=self.CATALOG,
            ),
            "ESCALATE",
        )
        self.assertEqual(
            evidence_gate_v2(
                case,
                trusted_action_id="advance_operational_workflow",
                trusted_action_catalog={},
            ),
            "ESCALATE",
        )

    def test_valid_trusted_action_preserves_existing_gate_decision(self):
        case = clean_high_risk_case()
        case["action"] = {
            "name": "advance_operational_workflow",
            **self.CATALOG["advance_operational_workflow"],
        }
        self.assertEqual(evidence_gate_v1(case), "ACT")
        self.assertEqual(
            evidence_gate_v2(
                case,
                trusted_action_id="advance_operational_workflow",
                trusted_action_catalog=self.CATALOG,
            ),
            "ACT",
        )


class EvidenceGateCompletenessTests(unittest.TestCase):
    def test_complete_consistent_case_can_act(self):
        case = clean_high_risk_case()
        self.assertTrue(visible_features(case)["complete"])
        self.assertEqual(evidence_gate_v1(case), "ACT")

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
