import json
import unittest
from pathlib import Path

class ReversibilityAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(Path(__file__).with_name("reversibility_assessment_v1.json").read_text(encoding="utf-8"))

    def test_all_30_frozen_cases_are_accounted_for_once(self):
        ids=[x["case_id"] for x in self.data["cases"]]
        self.assertEqual(len(ids),30)
        self.assertEqual(len(set(ids)),30)

    def test_counts_match_source_assessment(self):
        rows=self.data["cases"]
        self.assertEqual(sum(x["reversibility"]=="reversible" for x in rows),14)
        self.assertEqual(sum(x["reversibility"]=="irreversible" for x in rows),3)
        self.assertEqual(sum(x["reversibility"]=="reversible_with_rollback_plan" for x in rows),1)
        self.assertEqual(sum(x["reversibility"]=="not_specified" for x in rows),12)

    def test_unknown_cases_are_not_inferred_from_consequence(self):
        for row in self.data["cases"]:
            self.assertTrue(row["source_url"].startswith("https://app.notion.com/"))
            if row["reversibility"]=="not_specified":
                self.assertIn(row["basis"],{"no_explicit_reversibility_statement","destructive_but_reversal_not_defined"})

    def test_hidden_gold_fields_are_not_in_assessment(self):
        for row in self.data["cases"]:
            self.assertNotIn("gold_decision",row)
            self.assertNotIn("hidden_ground_truth",row)
            self.assertNotIn("recovery_target",row)

if __name__=="__main__": unittest.main()
