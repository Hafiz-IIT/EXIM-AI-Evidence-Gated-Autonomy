import json
import unittest
from pathlib import Path

class CaseBlindingTests(unittest.TestCase):
    def test_public_case_export_contains_only_model_input_fields_and_internal_id(self):
        path=Path(__file__).with_name("cases_public_v1.json")
        data=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(data["cases"]),30)
        allowed={"case_id","task","consequence","reversibility","evidence_packet"}
        for case in data["cases"]:
            self.assertEqual(set(case),allowed)
            for forbidden in ("gold_decision","hidden_ground_truth","attacked_dimension","recovery_target","case_notes","condition","pair_id","domain"):
                self.assertNotIn(forbidden,case)

    def test_reversibility_is_not_fabricated(self):
        data=json.loads(Path(__file__).with_name("cases_public_v1.json").read_text(encoding="utf-8"))
        self.assertTrue(all(case["reversibility"] is None for case in data["cases"]))

    def test_non_prompt_metadata_is_separate(self):
        data=json.loads(Path(__file__).with_name("case_registry_metadata_v1.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["rows"]),30)
        self.assertNotIn("Gold Decision",data.get("purpose",""))

if __name__=="__main__": unittest.main()
