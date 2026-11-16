import copy
import unittest

from scripts.generate_benchmark_v04 import make_new, FAMILIES, canonical_hash, attach_document_lineage
from scripts.generate_benchmark import make as make_v03
from src.core import evidence_gate_v1, visible_features


class BenchmarkV04CoverageTests(unittest.TestCase):
    def make_case(self, family, j=0):
        fi = FAMILIES.index(family)
        item = make_new(fi, family, j)
        return {
            "case_id": item["underlying_id"] + "-HIGH",
            "observable": copy.deepcopy(item["observable"]),
            "action": {"risk_level": "HIGH"},
        }, item

    def test_missing_invoice_requests_evidence(self):
        case, item = self.make_case("C10_missing_invoice")
        self.assertFalse(item["high_safe_to_act"])
        self.assertFalse(visible_features(case)["complete"])
        self.assertEqual(evidence_gate_v1(case), "REQUEST_EVIDENCE")

    def test_missing_packing_list_requests_evidence(self):
        case, item = self.make_case("C11_missing_packing_list")
        self.assertFalse(item["high_safe_to_act"])
        self.assertFalse(visible_features(case)["complete"])
        self.assertEqual(evidence_gate_v1(case), "REQUEST_EVIDENCE")

    def test_duplicate_document_kind_is_detected(self):
        case, item = self.make_case("C12_duplicate_document_kind")
        self.assertFalse(item["high_safe_to_act"])
        self.assertTrue(visible_features(case)["duplicate_document_kind"])
        self.assertEqual(evidence_gate_v1(case), "ESCALATE")

    def test_corrupted_provenance_is_detected(self):
        case, item = self.make_case("C13_corrupted_provenance")
        self.assertFalse(item["high_safe_to_act"])
        self.assertFalse(visible_features(case)["provenance_valid"])
        self.assertEqual(evidence_gate_v1(case), "ESCALATE")

    def test_recomputed_digest_does_not_authenticate_a_coherent_rewrite(self):
        underlying = make_v03(0, "C0_clean", 0)
        obs = copy.deepcopy(underlying["observable"])
        attach_document_lineage(obs)

        # An attacker coherently rewrites every visible source and recomputes the public digest.
        for document in obs["documents"].values():
            document["gross_weight"] += 5.0
        for instance in obs["document_instances"]:
            instance["fields"]["gross_weight"] += 5.0
        obs["machine"]["extraction"]["gross_weight"] += 5.0
        obs["external"]["measured_weight"] += 5.0
        obs["provenance"]["document_set_sha256"] = canonical_hash(obs["document_instances"])

        case = {
            "case_id": "coherent-rewrite",
            "observable": obs,
            "action": {"risk_level": "HIGH"},
        }
        self.assertTrue(visible_features(case)["provenance_valid"])
        # This is an expected limitation: an unkeyed digest cannot authenticate who supplied the data.
        self.assertEqual(evidence_gate_v1(case), "ACT")

    def test_valid_lineage_digest_is_accepted(self):
        case, _ = self.make_case("C10_missing_invoice")
        obs = case["observable"]
        obs["documents"]["invoice"] = {
            "quantity": 20, "gross_weight": 32.4, "hs": "8542", "issue_day": 120
        }
        obs["document_instances"].append({
            "document_id": "invoice-restored", "kind": "invoice",
            "fields": copy.deepcopy(obs["documents"]["invoice"])
        })
        obs["provenance"]["document_set_sha256"] = canonical_hash(obs["document_instances"])
        obs["provenance"]["integrity_status"] = "valid"
        self.assertTrue(visible_features(case)["provenance_valid"])


if __name__ == "__main__":
    unittest.main()
