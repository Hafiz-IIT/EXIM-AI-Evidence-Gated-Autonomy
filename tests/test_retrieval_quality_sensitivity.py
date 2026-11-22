import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "retrieval_quality_sensitivity",
    ROOT / "scripts" / "run_retrieval_quality_sensitivity.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RetrievalQualitySensitivityTests(unittest.TestCase):
    def setUp(self):
        self.draws = {
            "verifier_correct": 0.1,
            "retrieval_available": 0.1,
            "retrieval_correct": 0.99,
            "escalation_available": 0.1,
            "human_review_correct": 0.1,
        }

    def test_successful_but_inaccurate_retrieval_can_reverse_the_decision(self):
        params = {
            "retrieval_availability": 1.0,
            "retrieval_accuracy": 0.5,
            "human_accuracy": 0.9,
            "escalation_availability": 1.0,
            "unavailable_fallback": "DEFER",
            "verifier_accuracy": 0.93,
        }
        # The case is actually unsafe. Retrieval is available but wrong;
        # the model receives a misleading evidence packet and ACTs.
        self.assertTrue(MODULE.final_consequential_action("REQUEST_EVIDENCE", False, params, self.draws))

    def test_failed_retrieval_escalation_unavailability_is_fail_closed_or_open(self):
        draws = dict(self.draws, retrieval_available=0.99, escalation_available=0.99)
        base = {
            "retrieval_availability": 0.5,
            "retrieval_accuracy": 0.99,
            "human_accuracy": 0.99,
            "escalation_availability": 0.5,
            "unavailable_fallback": "DEFER",
            "verifier_accuracy": 0.93,
        }
        self.assertFalse(MODULE.final_consequential_action("REQUEST_EVIDENCE", False, base, draws))
        open_params = dict(base, unavailable_fallback="ACT")
        self.assertTrue(MODULE.final_consequential_action("REQUEST_EVIDENCE", False, open_params, draws))

    def test_common_random_draws_are_deterministic(self):
        case = {"case_id": "C1", "family": "C1", "safe_to_act": False}
        self.assertEqual(
            MODULE.make_common_random_draws([case], 7),
            MODULE.make_common_random_draws([case], 7),
        )
        self.assertNotEqual(
            MODULE.make_common_random_draws([case], 7),
            MODULE.make_common_random_draws([case], 8),
        )

    def test_condition_grid_has_162_prespecified_combinations(self):
        rows = list(MODULE.conditions())
        self.assertEqual(len(rows), 162)
        self.assertEqual({row["unavailable_fallback"] for row in rows}, {"ACT", "DEFER"})

    def test_policy_never_receives_gold_label_fields(self):
        case = {
            "case_id": "C0-HIGH",
            "family": "C0_clean",
            "safe_to_act": False,
            "ground_truth": {"secret": "gold"},
            "observable": {},
            "action": {"risk_level": "HIGH"},
        }
        seen = {}
        def policy(input_case):
            seen.update(input_case)
            return "DEFER"
        params = {
            "retrieval_availability": 0.9,
            "retrieval_accuracy": 0.9,
            "human_accuracy": 0.9,
            "escalation_availability": 0.9,
            "unavailable_fallback": "DEFER",
            "verifier_accuracy": 0.93,
        }
        MODULE.evaluate_policy([case], policy, params, {"C0-HIGH": self.draws})
        self.assertEqual(set(seen), {"observable", "action"})
        self.assertNotIn("safe_to_act", seen)
        self.assertNotIn("ground_truth", seen)

    def test_paired_difference_uses_seed_level_pairs(self):
        mean, sd, low, high = MODULE.paired_difference_ci([0.2, 0.4, 0.6], [0.1, 0.3, 0.5])
        self.assertAlmostEqual(mean, 0.1)
        self.assertAlmostEqual(sd, 0.0)
        self.assertAlmostEqual(low, 0.1)
        self.assertAlmostEqual(high, 0.1)


if __name__ == "__main__":
    unittest.main()
