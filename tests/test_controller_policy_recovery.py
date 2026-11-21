import copy
import unittest

from scripts.generate_benchmark import make
from src.core import (
    always_act, confidence_gate, document_agreement, always_verify,
    selective_abstention, weak_strong, risk_gate, evidence_gate_v1,
)


def case():
    generated = make(0, "C0_clean", 0)
    return {
        "observable": copy.deepcopy(generated["observable"]),
        "action": {"risk_level": "HIGH"},
    }


class HistoricalControllerRecoveryTests(unittest.TestCase):
    def test_b1_always_act(self):
        self.assertEqual(always_act(case()), "ACT")

    def test_b2_confidence_threshold_is_point_nine(self):
        c = case()
        c["observable"]["machine"]["extraction"]["confidence"] = 0.90
        self.assertEqual(confidence_gate(c), "ACT")
        c["observable"]["machine"]["extraction"]["confidence"] = 0.899999
        self.assertEqual(confidence_gate(c), "DEFER")

    def test_b3_requires_complete_agreeing_documents(self):
        c = case()
        self.assertEqual(document_agreement(c), "ACT")
        c["observable"]["documents"]["invoice"] = None
        self.assertEqual(document_agreement(c), "DEFER")

    def test_b4_always_verify(self):
        self.assertEqual(always_verify(case()), "VERIFY")

    def test_b5_requires_confidence_and_no_verifier_rejection(self):
        c = case()
        c["observable"]["machine"]["extraction"]["confidence"] = 0.90
        self.assertEqual(selective_abstention(c), "ACT")
        c["observable"]["machine"]["verifiers"][0]["accept"] = False
        self.assertEqual(selective_abstention(c), "DEFER")

    def test_b6_exact_upper_and_lower_thresholds(self):
        c = case()
        c["observable"]["machine"]["extraction"]["confidence"] = 0.94
        self.assertEqual(weak_strong(c), "ACT")
        c["observable"]["machine"]["extraction"]["confidence"] = 0.75
        self.assertEqual(weak_strong(c), "VERIFY")
        c["observable"]["machine"]["extraction"]["confidence"] = 0.749999
        self.assertEqual(weak_strong(c), "DEFER")

    def test_b7_high_risk_always_verifies(self):
        c = case()
        c["observable"]["machine"]["extraction"]["confidence"] = 0.99
        self.assertEqual(risk_gate(c), "VERIFY")

    def test_b7_low_risk_uses_point_nine_threshold(self):
        c = case()
        c["action"]["risk_level"] = "LOW"
        c["observable"]["machine"]["extraction"]["confidence"] = 0.90
        self.assertEqual(risk_gate(c), "ACT")
        c["observable"]["machine"]["extraction"]["confidence"] = 0.89
        self.assertEqual(risk_gate(c), "DEFER")

    def test_b8_clean_high_risk_case_can_act(self):
        self.assertEqual(evidence_gate_v1(case()), "ACT")


if __name__ == "__main__":
    unittest.main()
