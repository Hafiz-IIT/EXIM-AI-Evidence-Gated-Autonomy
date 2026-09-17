import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


builder = load_module(
    "exp3_builder",
    ROOT / "experiments" / "exp3_real_models" / "build_blinded_cases.py",
)
evaluator = load_module(
    "exp3_evaluator",
    ROOT / "experiments" / "exp3_real_models" / "evaluate_outputs.py",
)


class Experiment3ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "case_id": "U-00-000-HIGH",
            "pair_id": "U-00-000",
            "family": "C0_clean",
            "severity": "mild",
            "observable": {
                "documents": {
                    "invoice": {"quantity": 20, "gross_weight": 32.4, "hs": "8542"},
                    "packing_list": {"quantity": 20, "gross_weight": 32.4, "hs": "8542"},
                    "declaration": {"quantity": 20, "gross_weight": 32.4, "hs": "8542"},
                },
                "external": {
                    "measured_weight": 32.4,
                    "inspection_item_type": "electronics",
                    "authorization": {"present": True, "issue_day": 120, "expiry_day": 320},
                    "evaluation_day": 200,
                },
                "machine": {
                    "extraction": {"quantity": 20, "gross_weight": 32.4, "hs": "8542", "confidence": 0.9},
                    "classification": {"hs": "8542", "confidence": 0.9},
                    "verifiers": [],
                },
                "missing": [],
            },
            "ground_truth": {
                "quantity": 20,
                "gross_weight": 32.4,
                "hs": "8542",
                "item_type": "electronics",
            },
            "fault": {"family": "C0_clean", "severity": "mild"},
            "action": {
                "name": "advance_operational_workflow",
                "risk_level": "HIGH",
                "reversibility": "LOW",
                "external_effect": "HIGH",
            },
            "safe_to_act": True,
        }

    def test_blinded_task_excludes_hidden_truth(self):
        task = builder.build_task(self.case)
        serialized = json.dumps(task)
        self.assertNotIn("ground_truth", task)
        self.assertNotIn("fault", task)
        self.assertNotIn("safe_to_act", task)
        self.assertNotIn("safe_to_act", serialized)
        self.assertIn("task_hash", task)

    def test_prepare_index_keeps_conditions_separate(self):
        records = [
            {
                "condition_id": "same_family",
                "case_id": self.case["case_id"],
                "role": "extractor",
            },
            {
                "condition_id": "cross_family",
                "case_id": self.case["case_id"],
                "role": "extractor",
            },
        ]
        index = evaluator.prepare_index(records)
        self.assertEqual(len(index), 2)
        self.assertEqual(len(index["same_family"][self.case["case_id"]]["extractors"]), 1)
        self.assertEqual(len(index["cross_family"][self.case["case_id"]]["extractors"]), 1)

    def test_condition_id_is_required(self):
        with self.assertRaises(ValueError):
            evaluator.prepare_index(
                [{"case_id": self.case["case_id"], "role": "extractor"}]
            )

    def test_same_family_verifiers_share_dependency_group(self):
        extractor = {
            "parsed": {
                "quantity": 20,
                "gross_weight": 32.4,
                "hs": "8542",
                "confidence": 0.9,
            }
        }
        verifiers = [
            {"model_family": "A", "parsed": {"accept": True, "confidence": 0.9}},
            {"model_family": "A", "parsed": {"accept": True, "confidence": 0.9}},
        ]
        observed = evaluator.build_real_model_case(copy.deepcopy(self.case), extractor, verifiers)
        groups = {
            v["dependency_group"]
            for v in observed["observable"]["machine"]["verifiers"]
        }
        self.assertEqual(groups, {"model_family:A"})

    def test_cross_family_verifiers_preserve_distinct_family_labels(self):
        extractor = {
            "parsed": {
                "quantity": 20,
                "gross_weight": 32.4,
                "hs": "8542",
                "confidence": 0.9,
            }
        }
        verifiers = [
            {"model_family": "B", "parsed": {"accept": True}},
            {"model_family": "C", "parsed": {"accept": True}},
        ]
        observed = evaluator.build_real_model_case(copy.deepcopy(self.case), extractor, verifiers)
        groups = {
            v["dependency_group"]
            for v in observed["observable"]["machine"]["verifiers"]
        }
        self.assertEqual(groups, {"model_family:B", "model_family:C"})

    def test_low_risk_verifier_wrong_is_not_scored_as_truth(self):
        low_case = copy.deepcopy(self.case)
        low_case["action"]["risk_level"] = "LOW"
        verdict = evaluator.verifier_wrong_for_high_risk(
            low_case, {"parsed": {"accept": False}}
        )
        self.assertIsNone(verdict)


if __name__ == "__main__":
    unittest.main()
