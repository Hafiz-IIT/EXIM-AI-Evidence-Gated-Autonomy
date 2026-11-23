import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("annotation_builder", "scripts/build_annotation_packet.py")
SCORER = load_module("annotation_scorer", "scripts/score_annotation_agreement.py")


def case(case_id, pair_id, family, risk, safe):
    return {
        "case_id": case_id,
        "pair_id": pair_id,
        "family": family,
        "severity": "HIGH" if risk == "HIGH" else "LOW",
        "observable": {"documents": {"invoice": {"amount": 10}}, "provenance": {"integrity_status": "valid"}},
        "action": {
            "name": "advance_operational_workflow" if risk == "HIGH" else "save_temporary_record",
            "risk_level": risk,
            "reversibility": "LOW" if risk == "HIGH" else "HIGH",
            "external_effect": "HIGH" if risk == "HIGH" else "LOW",
        },
        "safe_to_act": safe,
        "fault": {"family": family},
        "fingerprint": f"fingerprint-{pair_id}",
    }


class AnnotationPacketTests(unittest.TestCase):
    def test_packet_is_deterministic_stratified_and_blinded(self):
        cases = []
        for family in ("C0_clean", "C1_extraction_error"):
            for i in range(3):
                pair = f"{family}-{i}"
                cases.append(case(pair + "-LOW", pair, family, "LOW", True))
                cases.append(case(pair + "-HIGH", pair, family, "HIGH", i == 0))
        packet, key = BUILDER.build_packet(cases, per_family=2, seed=17)
        packet2, key2 = BUILDER.build_packet(cases, per_family=2, seed=17)
        self.assertEqual(packet, packet2)
        self.assertEqual(key, key2)
        self.assertEqual(len(packet), 8)
        self.assertEqual(len(key), 8)
        forbidden = {"case_id", "pair_id", "family", "severity", "gold_safe_to_act", "fault_json", "fingerprint"}
        self.assertFalse(forbidden.intersection(packet[0]))
        self.assertTrue(forbidden.issubset(key[0]))
        self.assertEqual(len({row["annotation_id"] for row in packet}), len(packet))

    def test_packet_rejects_malformed_pairs(self):
        malformed = [case("A", "P", "C0_clean", "LOW", True)]
        with self.assertRaises(ValueError):
            BUILDER.build_packet(malformed, per_family=1, seed=1)


class AnnotationAgreementTests(unittest.TestCase):
    def test_krippendorff_alpha_perfect_agreement(self):
        result = SCORER.krippendorff_alpha_nominal([["ACT", "ACT"], ["DEFER", "DEFER"]])
        self.assertAlmostEqual(result["alpha"], 1.0)
        self.assertAlmostEqual(result["observed_agreement"], 1.0)

    def test_krippendorff_alpha_complete_disagreement(self):
        result = SCORER.krippendorff_alpha_nominal([["ACT", "DEFER"], ["ACT", "DEFER"]])
        self.assertAlmostEqual(result["alpha"], -1.0)
        self.assertAlmostEqual(result["observed_agreement"], 0.0)

    def test_alpha_handles_variable_annotator_counts(self):
        result = SCORER.krippendorff_alpha_nominal([["A", "A", "B"], ["B", "B"]])
        self.assertEqual(result["usable_items"], 2)
        self.assertEqual(result["total_ratings"], 5)
        self.assertIsNotNone(result["alpha"])

    def test_alpha_is_undefined_when_all_ratings_have_one_category(self):
        result = SCORER.krippendorff_alpha_nominal([["ACT", "ACT"], ["ACT", "ACT"]])
        self.assertIsNone(result["alpha"])
        self.assertEqual(result["observed_agreement"], 1.0)


if __name__ == "__main__":
    unittest.main()
