import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


prepare = load_module("exp3_prepare", ROOT / "scripts" / "exp3_prepare.py")
score = load_module("exp3_score", ROOT / "scripts" / "exp3_score.py")
validate = load_module("exp3_validate_outputs", ROOT / "scripts" / "exp3_validate_outputs.py")


class Exp3HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cases_path = ROOT / "data" / "benchmark" / "cases.jsonl"
        if not cases_path.exists():
            cls.skipTest(cls, "Generate data/benchmark/cases.jsonl before running harness tests")
        cls.cases = prepare.load_jsonl(cases_path)

    def test_render_case_excludes_hidden_truth_fields(self):
        forbidden = {"family", "severity", "fault", "ground_truth", "safe_to_act"}
        for case in self.cases[:50]:
            rendered = prepare.render_case(case)
            rendered_lower = rendered.lower()
            for field in forbidden:
                self.assertNotIn(field.lower(), rendered_lower)

    def test_pair_integrity(self):
        assignment = prepare.stratified_pair_split(self.cases)
        prepare.ensure_pair_integrity(self.cases, assignment)
        pair_ids = {c["pair_id"] for c in self.cases}
        self.assertEqual(set(assignment), pair_ids)

    def test_split_is_deterministic(self):
        a = prepare.stratified_pair_split(self.cases)
        b = prepare.stratified_pair_split(self.cases)
        self.assertEqual(a, b)

    def test_split_has_no_pair_leakage(self):
        assignment = prepare.stratified_pair_split(self.cases)
        seen = {}
        for case in self.cases:
            split = assignment[case["pair_id"]]
            if case["pair_id"] in seen:
                self.assertEqual(seen[case["pair_id"]], split)
            seen[case["pair_id"]] = split

    def test_wilson_zero_success_upper_bound_is_nonzero(self):
        lo, hi = score.wilson(0, 500)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)
        self.assertLess(hi, 0.02)

    def test_exact_mcnemar_symmetry(self):
        self.assertEqual(score.exact_mcnemar_p(3, 8), score.exact_mcnemar_p(8, 3))
        self.assertEqual(score.exact_mcnemar_p(0, 0), 1.0)

    def test_cautious_routes_are_not_terminal_false_blocks(self):
        safe_case = next(c for c in self.cases if c["safe_to_act"])
        for decision in ("VERIFY", "REQUEST_EVIDENCE", "ESCALATE"):
            result = score.classify(safe_case, decision)
            self.assertEqual(result["safe_case_deferred"], 0)
            self.assertEqual(result["safe_case_routed_for_more_review"], 1)
        deferred = score.classify(safe_case, "DEFER")
        self.assertEqual(deferred["safe_case_deferred"], 1)

    def test_unknown_decision_rejected(self):
        safe_case = next(c for c in self.cases if c["safe_to_act"])
        with self.assertRaises(ValueError):
            score.classify(safe_case, "MAYBE")

    def test_output_validator_accepts_minimal_valid_record(self):
        record = {
            "case_id": "case-1",
            "split": "dev",
            "role": "verifier_a",
            "provider": "example",
            "model": "example-model",
            "timestamp": "2026-09-17T00:00:00Z",
            "input_sha256": "a" * 64,
            "system_prompt_sha256": "b" * 64,
            "user_prompt_sha256": "c" * 64,
            "raw_response": "{}",
            "parse_ok": True,
            "latency_ms": 1,
            "retry_count": 0,
            "parsed": {
                "accept": True,
                "confidence": 0.9,
                "issues": [],
                "requested_evidence": []
            }
        }
        validate.validate_record(record)


if __name__ == "__main__":
    unittest.main()
