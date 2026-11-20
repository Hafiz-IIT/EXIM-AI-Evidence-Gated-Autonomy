import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EximTier2DatasetTests(unittest.TestCase):
    def test_exact_scenario_count_and_unique_ids(self):
        data = json.loads((ROOT / "data" / "exim_real_25.json").read_text(encoding="utf-8"))
        rows = data["scenarios"]
        self.assertEqual(data["scenario_count"], 25)
        self.assertEqual(len(rows), 25)
        self.assertEqual(len({row["scenario_id"] for row in rows}), 25)

    def test_category_balance_and_five_clean_controls(self):
        data = json.loads((ROOT / "data" / "exim_real_25.json").read_text(encoding="utf-8"))
        counts = {}
        for row in data["scenarios"]:
            counts[row["category"]] = counts.get(row["category"], 0) + 1
        expected_counts = {
            "document_mismatch": 4,
            "expired_certificate": 4,
            "sanctions_near_match": 4,
            "hs_classification_conflict": 3,
            "valid_control": 5,
            "missing_export_authorization": 1,
            "origin_conflict": 1,
            "dangerous_goods_documentation": 1,
            "expired_insurance": 1,
            "payment_instruction_tampering": 1,
        }
        self.assertEqual(counts, expected_counts)
        self.assertEqual(data["category_counts"], expected_counts)
        self.assertEqual(sum(row["expected_action"] == "ACT" for row in data["scenarios"]), 5)
        self.assertTrue(all(
            row["expected_action"] == ("ACT" if row["category"] == "valid_control" else "ESCALATE")
            for row in data["scenarios"]
        ))

    def test_evidence_issue_dates_precede_expiry(self):
        from datetime import datetime
        data = json.loads((ROOT / "data" / "exim_real_25.json").read_text(encoding="utf-8"))
        for row in data["scenarios"]:
            for evidence in row["evidence"]:
                issued = evidence.get("issued_at")
                expires = evidence.get("valid_until")
                if issued and expires:
                    self.assertLess(datetime.fromisoformat(issued.replace("Z", "+00:00")),
                                    datetime.fromisoformat(expires.replace("Z", "+00:00")),
                                    msg=f"{row['scenario_id']}: {evidence.get('document_type')}")

    def test_expired_records_are_expired_before_shipment(self):
        from datetime import datetime
        shipment_date = datetime.fromisoformat("2026-11-20T00:00:00+00:00")
        data = json.loads((ROOT / "data" / "exim_real_25.json").read_text(encoding="utf-8"))
        expired = [row for row in data["scenarios"] if row["category"] == "expired_certificate"]
        self.assertEqual(len(expired), 4)
        for row in expired:
            official = row["evidence"][0]
            expiry = datetime.fromisoformat(official["valid_until"].replace("Z", "+00:00"))
            self.assertLess(expiry, shipment_date, msg=row["scenario_id"])

    def test_document_type_matches_mismatch_context(self):
        data = json.loads((ROOT / "data" / "exim_real_25.json").read_text(encoding="utf-8"))
        expected = {
            "EXIM-DOC-MISMATCH-1": ["Bill of Lading", "Commercial Invoice"],
            "EXIM-DOC-MISMATCH-2": ["Carrier Manifest", "Packing List"],
            "EXIM-DOC-MISMATCH-3": ["Commercial Invoice", "Packing List"],
            "EXIM-DOC-MISMATCH-4": ["Shipping Bill", "Commercial Invoice"],
        }
        for row in data["scenarios"]:
            if row["scenario_id"] in expected:
                self.assertEqual([e["document_type"] for e in row["evidence"]], expected[row["scenario_id"]])

    def test_every_case_has_evidence_and_gold_action(self):
        data = json.loads((ROOT / "data" / "exim_real_25.json").read_text(encoding="utf-8"))
        for row in data["scenarios"]:
            self.assertIn(row["expected_action"], {"ACT", "ESCALATE"})
            self.assertTrue(row["evidence"])
            self.assertTrue(row["decision_question"])


if __name__ == "__main__":
    unittest.main()
