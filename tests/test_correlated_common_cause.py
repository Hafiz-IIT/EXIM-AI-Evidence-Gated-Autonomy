import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "correlated_common_cause",
    ROOT / "scripts" / "run_correlated_common_cause_sensitivity.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CorrelatedCommonCauseTests(unittest.TestCase):
    def test_grid_has_81_conditions(self):
        self.assertEqual(len(list(MODULE.conditions())), 81)

    def test_zero_shock_reduces_to_independent_marginals(self):
        self.assertAlmostEqual(MODULE.residual_error_probability(0.93, 0.0), 0.07)
        self.assertEqual(MODULE.residual_error_probability(0.75, 0.0), 0.25)

    def test_common_shock_preserves_each_marginal_error_rate(self):
        for accuracy, rho in ((0.85, 0.02), (0.93, 0.02), (0.98, 0.02), (0.75, 0.02)):
            residual = MODULE.residual_error_probability(accuracy, rho)
            marginal = rho + (1.0 - rho) * residual
            self.assertAlmostEqual(marginal, 1.0 - accuracy)

    def test_shared_shock_induces_positive_pairwise_error_covariance(self):
        rho = 0.02
        e1, e2 = 0.15, 0.25
        q1 = MODULE.residual_error_probability(1.0 - e1, rho)
        q2 = MODULE.residual_error_probability(1.0 - e2, rho)
        joint = rho + (1.0 - rho) * q1 * q2
        covariance = joint - e1 * e2
        self.assertGreater(covariance, 0.0)

    def test_shock_mass_never_exceeds_any_marginal_error(self):
        params = {
            "retrieval_accuracy": 0.95,
            "human_accuracy": 0.98,
            "verifier_accuracy": 0.93,
            "common_shock_fraction": 1.0,
        }
        rho = MODULE.common_shock_mass(params)
        self.assertLessEqual(rho, 1.0 - params["retrieval_accuracy"])
        self.assertLessEqual(rho, 1.0 - params["human_accuracy"])
        self.assertLessEqual(rho, 1.0 - params["verifier_accuracy"])

    def test_draws_are_deterministic_and_case_indexed(self):
        cases = [{"case_id": "A"}, {"case_id": "B"}]
        self.assertEqual(MODULE.make_correlated_draws(cases, 7), MODULE.make_correlated_draws(cases, 7))
        self.assertNotEqual(MODULE.make_correlated_draws(cases, 7), MODULE.make_correlated_draws(cases, 8))

    def test_serial_gate_shared_shock_can_bypass_human_review(self):
        case = {"case_id": "U1", "family": "test", "safe_to_act": False}
        params = {
            "retrieval_accuracy": 0.98, "human_accuracy": 0.98,
            "verifier_accuracy": 0.98, "common_shock_fraction": 1.0,
            "retrieval_availability": 1.0, "escalation_availability": 1.0,
            "unavailable_fallback": "DEFER",
        }
        draws = {"U1": {
            "common_shock": 0.001, "retrieval_noise": 0.99,
            "verifier_noise": 0.99, "human_noise": 0.99,
            "retrieval_available": 0.0, "escalation_available": 0.0,
        }}
        overall, _ = MODULE.evaluate_serial_evidence_gate([case], params, draws)
        self.assertEqual(overall["unsafe_acts"], 1)

    def test_serial_gate_escalates_when_retrieval_and_verifier_disagree(self):
        case = {"case_id": "S1", "family": "test", "safe_to_act": True}
        params = {
            "retrieval_accuracy": 0.75, "human_accuracy": 0.75,
            "verifier_accuracy": 0.75, "common_shock_fraction": 0.0,
            "retrieval_availability": 1.0, "escalation_availability": 1.0,
            "unavailable_fallback": "DEFER",
        }
        draws = {"S1": {
            "common_shock": 0.5, "retrieval_noise": 0.0,
            "verifier_noise": 0.99, "human_noise": 0.99,
            "retrieval_available": 0.0, "escalation_available": 0.0,
        }}
        overall, _ = MODULE.evaluate_serial_evidence_gate([case], params, draws)
        self.assertEqual(overall["safe_act_coverage"], 1.0)

    def test_paired_shock_effects_use_same_seed_across_correlation_levels(self):
        rows = []
        metrics = (
            "unsafe_act_rate", "unsafe_act_conditional_rate", "safe_act_coverage",
            "false_block_rate", "act_rate",
        )
        policies = ("EvidenceGate", "RiskGate", "SerialEvidenceGate")
        for retrieval in (0.50, 0.75, 0.95):
            for human in (0.75, 0.90, 0.98):
                for verifier in (0.85, 0.93, 0.98):
                    for seed in range(MODULE.N_SEEDS):
                        for fraction in (0.0, 0.5, 1.0):
                            row = {
                                "retrieval_accuracy": retrieval,
                                "human_accuracy": human,
                                "verifier_accuracy": verifier,
                                "seed": seed, "common_shock_fraction": fraction,
                            }
                            for policy in policies:
                                for metric in metrics:
                                    row[f"{policy}_{metric}"] = seed / 100 + fraction / 10
                            rows.append(row)
        effects = MODULE.paired_shock_effects(rows)
        self.assertEqual(len(effects), 810)
        selected = next(
            row for row in effects
            if row["retrieval_accuracy"] == 0.5
            and row["human_accuracy"] == 0.75
            and row["verifier_accuracy"] == 0.85
            and row["policy"] == "SerialEvidenceGate"
            and row["comparison"] == "shock_0.5_minus_independent"
            and row["metric"] == "unsafe_act_rate"
        )
        self.assertAlmostEqual(selected["paired_mean_difference"], 0.05)
        self.assertAlmostEqual(selected["paired_95ci_low"], 0.05)
        self.assertAlmostEqual(selected["paired_95ci_high"], 0.05)

    def test_paired_difference_uses_seed_level_pairs(self):
        mean, sd, low, high = MODULE.paired_difference_ci([0.2, 0.4, 0.6], [0.1, 0.3, 0.5])
        self.assertAlmostEqual(mean, 0.1)
        self.assertAlmostEqual(sd, 0.0)
        self.assertAlmostEqual(low, 0.1)
        self.assertAlmostEqual(high, 0.1)


if __name__ == "__main__":
    unittest.main()
