import unittest
from scripts.run_reconstruction_v1 import (
    mutate_case, resolve_action, REGIMES, signed_record, signature_valid,
    dual_lineage_action, sign_component_records, component_records_valid
)
from scripts.generate_benchmark import make


class ReconstructionProtocolTests(unittest.TestCase):
    def setUp(self):
        self.case = make(0, "C0_clean", 0)

    def test_attack_transformations_are_deterministic_and_nonmutating(self):
        original = self.case["observable"]["external"]["measured_weight"]
        changed = mutate_case(self.case, "timestamp_masking")
        self.assertGreater(
            changed["observable"]["external"]["authorization"]["expiry_day"],
            changed["observable"]["external"]["evaluation_day"],
        )
        self.assertEqual(self.case["observable"]["external"]["measured_weight"], original)

    def test_ed25519_signature_and_payload_binding(self):
        record = signed_record("evidence-root", {"case_id": "x", "digest": "abc"})
        self.assertTrue(signature_valid(record, {"evidence-root"}))
        self.assertFalse(signature_valid(record, {"other-root"}))
        record["payload"]["digest"] = "tampered"
        self.assertFalse(signature_valid(record, {"evidence-root"}))

    def test_regime_parameters_are_explicit_and_bounded(self):
        self.assertEqual(set(REGIMES), {"optimistic", "moderate", "harsh"})
        for params in REGIMES.values():
            for value in params.values():
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)

    def test_fail_open_when_escalation_unavailable_is_explicit(self):
        import random
        self.assertTrue(resolve_action("ESCALATE", False, {
            "human_accuracy": 1.0, "escalation_available": False,
            "verifier_accuracy": 1.0, "retrieval_success": 1.0,
        }, random.Random(1)))

    def test_dual_lineage_preserves_other_evidence_gate_blocks(self):
        correlated = make(8, "C8_correlated_verifier_failure", 0)
        case = {
            "case_id": "correlated-high",
            "observable": correlated["observable"],
            "action": {"risk_level": "HIGH"},
        }
        original_groups = [v["dependency_group"] for v in case["observable"]["machine"]["verifiers"]]
        spoofed = mutate_case(case, "dependency_spoof")
        self.assertEqual(dual_lineage_action(spoofed, original_groups), "ESCALATE")
        self.assertEqual(dual_lineage_action(spoofed, original_groups, {"lineage_A"}), "ESCALATE")
        self.assertEqual(dual_lineage_action(spoofed, original_groups, {"lineage_A", "lineage_B"}), "ACT")

        extraction_error = make(1, "C1_extraction_error", 0)
        other = {
            "case_id": "extraction-high",
            "observable": extraction_error["observable"],
            "action": {"risk_level": "HIGH"},
        }
        groups = [v["dependency_group"] for v in other["observable"]["machine"]["verifiers"]]
        self.assertEqual(dual_lineage_action(other, groups), "VERIFY")

    def test_component_attestations_are_role_scoped(self):
        original = {
            "case_id": "scoped-test",
            "observable": self.case["observable"],
            "action": {"risk_level": "HIGH"},
        }
        records = sign_component_records(original)
        self.assertTrue(component_records_valid(records, original))

        tampered = mutate_case(original, "external_masking")
        self.assertFalse(component_records_valid(records, tampered))

        # Only the sensor authority can re-attest the sensor component.
        from scripts.run_reconstruction_v1 import canonical_hash, component_payloads
        records["sensor_root"] = signed_record("sensor_root", {
            "case_id": tampered["case_id"],
            "component_sha256": canonical_hash(component_payloads(tampered)["sensor_root"]),
        })
        self.assertTrue(component_records_valid(records, tampered))


if __name__ == "__main__":
    unittest.main()
