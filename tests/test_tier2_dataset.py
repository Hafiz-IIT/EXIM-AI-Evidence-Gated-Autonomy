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
        self.assertEqual(counts, data["category_counts"])
        self.assertEqual(sum(row["expected_action"] == "ACT" for row in data["scenarios"]), 5)

    def test_every_case_has_evidence_and_gold_action(self):
        data = json.loads((ROOT / "data" / "exim_real_25.json").read_text(encoding="utf-8"))
        for row in data["scenarios"]:
            self.assertIn(row["expected_action"], {"ACT", "ESCALATE"})
            self.assertTrue(row["evidence"])
            self.assertTrue(row["decision_question"])


if __name__ == "__main__":
    unittest.main()
