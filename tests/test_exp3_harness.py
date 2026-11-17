import json
import unittest
import hashlib
import tempfile
from pathlib import Path

from experiments.exp3_real_models.harness import (
    assert_public_task_blinded,
    assign_splits,
    evaluate_case,
    prepare_tasks,
    build_public_task,
    normalize_extraction,
    normalize_verifier,
    parse_json_object,
    render_documents,
    summarize_results,
)


class Exp3BlindingAndSchemaTests(unittest.TestCase):
    def make_case(self, family, pair, risk="HIGH"):
        return {
            "case_id": f"{pair}-{risk}",
            "pair_id": pair,
            "family": family,
            "severity": "mild",
            "ground_truth": {"quantity": 5, "gross_weight": 7.5, "hs": "8542"},
            "fault": {"family": family},
            "safe_to_act": True,
            "observable": {
                "documents": {
                    "invoice": {"quantity": 5, "gross_weight": 7.5, "hs": "8542", "issue_day": 10},
                    "packing_list": {"quantity": 5, "gross_weight": 7.5, "hs": "8542", "issue_day": 10},
                    "declaration": {"quantity": 5, "gross_weight": 7.5, "hs": "8542", "issue_day": 10},
                },
                "external": {
                    "measured_weight": 7.5,
                    "inspection_item_type": "electronics",
                    "authorization": {"present": True, "issue_day": 10, "expiry_day": 20},
                    "evaluation_day": 15,
                },
                "machine": {"extraction": {}, "verifiers": []},
            },
            "action": {"risk_level": risk, "reversibility": "LOW", "external_effect": "HIGH"},
        }

    def test_public_task_omits_all_oracle_and_identity_fields(self):
        task = build_public_task(self.make_case("C4", "U-01-000"), "canonical")
        serialized = json.dumps(task).lower()
        for forbidden in ("ground_truth", "fault", "safe_to_act", "family", "severity", "pair_id", "case_id"):
            self.assertNotIn(forbidden, serialized)
        assert_public_task_blinded(task)

    def test_task_ids_are_salted_and_not_predictable_from_case_id(self):
        case = self.make_case("C4", "U-01-123")
        task = build_public_task(case, "canonical", "private-salt-for-test")
        predictable = hashlib.sha256(f"exp3-task-v1|{case['case_id']}|canonical".encode()).hexdigest()[:20]
        self.assertNotEqual(task["task_id"], predictable)
        self.assertEqual(len(task["task_id"]), 24)

    def test_prepare_keeps_task_salt_out_of_public_artifacts(self):
        cases = [self.make_case("C0", f"U-00-{i:03d}") for i in range(10)]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "cases.jsonl"
            benchmark.write_text("".join(json.dumps(x) + "\\n" for x in cases))
            manifest = prepare_tasks(benchmark, root / "prepared")
            private = json.loads((root / "prepared/private/private_metadata.json").read_text())
            public_text = (
                (root / "prepared/public/tasks.jsonl").read_text()
                + (root / "prepared/public/task_manifest.json").read_text()
            )
            self.assertIn("task_id_salt_sha256", manifest)
            self.assertNotIn(private["task_id_salt"], public_text)
            self.assertEqual(manifest["public_task_count"], 12)

    def test_provider_or_schema_failures_force_escalation(self):
        case = self.make_case("C0", "U-00-000")
        extraction = {"quantity": 5, "gross_weight": 7.5, "hs": "8542", "confidence": 0.99}
        verifiers = [
            {"model_id": "m1", "family_id": "family_a", "normalized": {"accept": True, "confidence": 0.9}, "parse_ok": True},
            {"model_id": "m2", "family_id": "family_b", "normalized": {"accept": True, "confidence": 0.9}, "parse_ok": True},
        ]
        self.assertEqual(evaluate_case(case, extraction, verifiers, provider_error=True)["controller_action"], "ESCALATE")
        self.assertEqual(evaluate_case(case, extraction, verifiers, extraction_parse_ok=False)["controller_action"], "ESCALATE")
        verifiers[1]["parse_ok"] = False
        self.assertEqual(evaluate_case(case, extraction, verifiers)["controller_action"], "ESCALATE")

    def test_split_is_deterministic_and_pair_level(self):
        cases = [self.make_case("C0", f"U-00-{i:03d}") for i in range(10)]
        first = assign_splits(cases)
        second = assign_splits(list(reversed(cases)))
        self.assertEqual(first, second)
        self.assertEqual(set(first.values()), {"development", "validation", "final_holdout"})

    def test_layout_ood_changes_rendering_without_changing_values(self):
        docs = self.make_case("C0", "U-00-000")["observable"]["documents"]
        canonical = render_documents(docs, "canonical")
        ood = render_documents(docs, "ood")
        self.assertNotEqual(canonical, ood)
        self.assertIn("7.5", ood)
        self.assertIn("8542", ood)

    def test_parse_json_fenced_response(self):
        self.assertEqual(parse_json_object('```json\n{"accept":true}\n```'), {"accept": True})

    def test_invalid_extraction_fails_closed(self):
        normalized, valid = normalize_extraction({"quantity": "unknown", "gross_weight": 7.5, "hs": "8542", "confidence": 0.9})
        self.assertFalse(valid)
        self.assertIsNone(normalized["quantity"])
        self.assertEqual(normalized["confidence"], 0.0)

    def test_invalid_verifier_fails_closed(self):
        normalized, valid = normalize_verifier({"accept": "yes", "confidence": 0.9})
        self.assertFalse(valid)
        self.assertFalse(normalized["accept"])

    def test_v1_gate_uses_family_labels_as_dependency_groups(self):
        from experiments.exp3_real_models.harness import evaluate_case
        case = self.make_case("C0", "U-00-000")
        extraction = {"quantity": 5, "gross_weight": 7.5, "hs": "8542", "confidence": 0.99}
        same_family = [
            {"model_id": "m1", "family_id": "family_a", "normalized": {"accept": True, "confidence": 0.9}, "parse_ok": True},
            {"model_id": "m2", "family_id": "family_a", "normalized": {"accept": True, "confidence": 0.9}},
        ]
        cross_family = [
            {"model_id": "m1", "family_id": "family_a", "normalized": {"accept": True, "confidence": 0.9}},
            {"model_id": "m2", "family_id": "family_b", "normalized": {"accept": True, "confidence": 0.9}},
        ]
        self.assertEqual(evaluate_case(case, extraction, same_family)["controller_action"], "ESCALATE")
        self.assertEqual(evaluate_case(case, extraction, cross_family)["controller_action"], "ACT")

    def test_summary_uses_safe_case_denominator_for_false_block(self):
        rows = [
            {"safe_to_act": True, "controller_action": "ESCALATE", "unsafe_act": False, "false_block": True, "verifier_cofailure": False, "verifier_family_count": 1, "total_latency_ms": 10, "estimated_cost_usd": 0.1},
            {"safe_to_act": False, "controller_action": "ACT", "unsafe_act": True, "false_block": False, "verifier_cofailure": True, "verifier_family_count": 2, "total_latency_ms": 20, "estimated_cost_usd": 0.2},
        ]
        summary = summarize_results(rows)
        self.assertEqual(summary["ICAR_high"], 0.5)
        self.assertEqual(summary["false_block_rate"], 1.0)
        self.assertEqual(summary["coverage"], 0.5)


if __name__ == "__main__":
    unittest.main()

