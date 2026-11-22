import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("action_consequence", ROOT / "scripts" / "run_action_consequence_spoof.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ActionConsequenceBindingTests(unittest.TestCase):
    def test_risk_downgrade_attack_is_rejected_by_v2(self):
        case = {
            "case_id": "case-1",
            "family": "C13_corrupted_provenance",
            "safe_to_act": False,
            "observable": {"documents": {}, "external": {}, "machine": {}},
            "action": {
                "name": "advance_operational_workflow",
                "risk_level": "LOW",
                "reversibility": "LOW",
                "external_effect": "HIGH",
            },
        }
        self.assertEqual(MODULE.decide("v1", case, "advance_operational_workflow"), "ACT")
        self.assertEqual(MODULE.decide("v2", case, "advance_operational_workflow"), "ESCALATE")

    def test_action_identity_substitution_is_rejected_by_v2(self):
        case = {
            "observable": {},
            "action": {
                "name": "save_temporary_record",
                "risk_level": "LOW",
                "reversibility": "HIGH",
                "external_effect": "LOW",
            },
        }
        self.assertEqual(MODULE.decide("v2", case, "advance_operational_workflow"), "ESCALATE")

    def test_metadata_variants_preserve_original_and_attack_copies(self):
        original = {
            "action": {
                "name": "advance_operational_workflow",
                "risk_level": "HIGH",
                "reversibility": "LOW",
                "external_effect": "HIGH",
            }
        }
        variants = MODULE.attacks(original)
        self.assertEqual(original["action"]["risk_level"], "HIGH")
        self.assertEqual(variants["risk_level_downgrade"]["action"]["risk_level"], "LOW")
        self.assertEqual(variants["reversibility_spoof"]["action"]["reversibility"], "HIGH")
        self.assertEqual(variants["external_effect_spoof"]["action"]["external_effect"], "LOW")
        self.assertEqual(variants["action_identity_substitution"]["action"]["name"], "save_temporary_record")


if __name__ == "__main__":
    unittest.main()
