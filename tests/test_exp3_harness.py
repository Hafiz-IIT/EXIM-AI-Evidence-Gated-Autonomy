import json
import unittest
import hashlib
import tempfile
import os
import csv
import subprocess
import sys
from pathlib import Path

from experiments.exp3_real_models.harness import (
    assert_public_task_blinded,
    assign_splits,
    evaluate_case,
    estimate_condition_cost,
    prepare_tasks,
    run_condition,
    verify_prepared_package,
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

    def test_prepared_package_detects_private_map_tampering(self):
        cases = [self.make_case("C0", f"U-00-{i:03d}") for i in range(10)]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "cases.jsonl"
            benchmark.write_text("".join(json.dumps(x) + "\n" for x in cases))
            prepared = root / "prepared"
            prepare_tasks(benchmark, prepared)
            private_map = prepared / "private" / "evaluation_map.jsonl"
            private_map.write_text(private_map.read_text() + "{}\n")
            with self.assertRaisesRegex(ValueError, "private evaluation map hash"):
                verify_prepared_package(prepared)

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
            benchmark.write_text("".join(json.dumps(x) + "\n" for x in cases))
            manifest = prepare_tasks(benchmark, root / "prepared")
            private = json.loads((root / "prepared/private/private_metadata.json").read_text())
            public_text = (
                (root / "prepared/public/tasks.jsonl").read_text()
                + (root / "prepared/public/task_manifest.json").read_text()
            )
            self.assertIn("task_id_salt_sha256", manifest)
            self.assertNotIn(private["task_id_salt"], public_text)
            self.assertEqual(manifest["public_task_count"], 12)

    def test_cost_estimator_reports_rough_preflight_estimate(self):
        case = self.make_case("C0", "U-00-000")
        task = build_public_task(case, "canonical", "cost-test-salt")
        models = {
            "extractor": {"family_id": "family_a", "input_usd_per_1k_tokens": 1.0, "output_usd_per_1k_tokens": 2.0},
            "verifier_a": {"family_id": "family_b", "input_usd_per_1k_tokens": 1.0, "output_usd_per_1k_tokens": 2.0},
            "verifier_b": {"family_id": "family_c", "input_usd_per_1k_tokens": 1.0, "output_usd_per_1k_tokens": 2.0},
        }
        config = {"models": models, "settings": {"max_tokens": 100}}
        condition = {"extractor_model": "extractor", "verifier_models": ["verifier_a", "verifier_b"]}
        estimate = estimate_condition_cost([task], condition, config)
        self.assertEqual(estimate["api_call_count"], 3)
        self.assertTrue(estimate["cost_known"])
        self.assertGreater(estimate["preflight_estimated_cost_usd"], 0)

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

    def test_freeze_rejects_inline_provider_secrets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = root / "config.json"
            config_path.write_text(json.dumps({
                "models": {"m": {"provider": "mock", "base_url": "https://api.test/v1", "model": "m", "family_id": "f", "api_key_env": "KEY", "api_key": "do-not-store"}},
                "conditions": [], "settings": {},
            }))
            prepared = root / "prepared"
            (prepared / "public").mkdir(parents=True)
            (prepared / "private").mkdir()
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.run([
                    sys.executable, "scripts/freeze_exp3_config.py",
                    "--config", str(config_path), "--prepared-dir", str(prepared), "--output", str(root / "frozen.json"),
                ], cwd=Path(__file__).resolve().parents[1], check=True, capture_output=True, text=True)

    def test_freeze_binds_task_manifest_and_unique_holdout_family(self):
        cases = [self.make_case("C0", f"U-00-{i:03d}") for i in range(10)]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "cases.jsonl"
            benchmark.write_text("".join(json.dumps(x) + "\n" for x in cases))
            prepared = root / "prepared"
            prepare_tasks(benchmark, prepared)
            models = {}
            for name, family, holdout in [
                ("model_a", "family_a", False), ("model_b", "family_b", False),
                ("model_c", "family_c", False), ("model_d", "family_d", True),
            ]:
                models[name] = {
                    "provider": "mock", "base_url": "https://api.test/v1",
                    "model": "mock-" + name, "family_id": family,
                    "api_key_env": "EXP3_UNUSED_KEY", "holdout_only": holdout,
                }
            conditions = [
                {"condition_id": "same_model", "extractor_model": "model_a", "verifier_models": ["model_a", "model_a"]},
                {"condition_id": "cross_family", "extractor_model": "model_a", "verifier_models": ["model_b", "model_c"]},
                {"condition_id": "family_holdout", "extractor_model": "model_a", "verifier_models": ["model_b", "model_d"], "holdout_only": True},
            ]
            config_path = root / "config.json"
            config_path.write_text(json.dumps({"models": models, "conditions": conditions, "settings": {}}))
            output = root / "frozen.json"
            subprocess.run([
                sys.executable, "scripts/freeze_exp3_config.py",
                "--config", str(config_path), "--prepared-dir", str(prepared), "--output", str(output),
            ], cwd=Path(__file__).resolve().parents[1], check=True, capture_output=True, text=True)
            frozen = json.loads(output.read_text())["freeze"]
            manifest_path = prepared / "public" / "task_manifest.json"
            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(frozen["task_manifest_sha256"], hashlib.sha256(manifest_path.read_bytes()).hexdigest())
            self.assertEqual(frozen["public_tasks_sha256"], manifest["public_tasks_sha256"])
            self.assertEqual(frozen["task_id_salt_sha256"], manifest["task_id_salt_sha256"])
            private_meta = json.loads((prepared / "private" / "private_metadata.json").read_text())
            self.assertEqual(frozen["private_evaluation_map_sha256"], private_meta["private_evaluation_map_sha256"])

    def test_cost_estimator_cli_writes_report_without_api_keys(self):
        cases = [self.make_case("C0", f"U-00-{i:03d}") for i in range(10)]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "cases.jsonl"
            benchmark.write_text("".join(json.dumps(x) + "\n" for x in cases))
            prepared = root / "prepared"
            prepare_tasks(benchmark, prepared)
            models = {
                name: {
                    "model": "mock-" + name, "provider": "mock",
                    "base_url": "https://api.test/v1", "family_id": family,
                    "api_key_env": "EXP3_NOT_REQUIRED_FOR_ESTIMATE",
                    "input_usd_per_1k_tokens": 0.5, "output_usd_per_1k_tokens": 1.0,
                }
                for name, family in [("extractor", "family_a"), ("verifier_a", "family_b"), ("verifier_b", "family_c")]
            }
            condition = {"condition_id": "same_model", "extractor_model": "extractor", "verifier_models": ["verifier_a", "verifier_b"]}
            config_path = root / "config.json"
            config_path.write_text(json.dumps({"models": models, "conditions": [condition], "settings": {"max_tokens": 100}}))
            output = root / "estimate.json"
            subprocess.run([
                sys.executable, "scripts/estimate_exp3_cost.py",
                "--config", str(config_path), "--prepared-dir", str(prepared),
                "--splits", "development", "--conditions", "same_model",
                "--output", str(output),
            ], cwd=Path(__file__).resolve().parents[1], check=True, capture_output=True, text=True)
            report = json.loads(output.read_text())
            self.assertEqual(report["status"], "estimated_no_model_calls")
            self.assertEqual(report["runs"][0]["api_call_count"], 18)
            self.assertGreater(report["total_preflight_estimated_cost_usd"], 0)

    def test_preflight_budget_blocks_before_api_key_check(self):
        cases = [self.make_case("C0", f"U-00-{i:03d}") for i in range(10)]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "cases.jsonl"
            benchmark.write_text("".join(json.dumps(x) + "\n" for x in cases))
            prepared = root / "prepared"
            prepare_tasks(benchmark, prepared)
            models = {
                name: {
                    "model": "mock-" + name, "provider": "mock",
                    "base_url": "https://example.invalid/v1", "family_id": family,
                    "api_key_env": "EXP3_NEVER_SET", "input_usd_per_1k_tokens": 10.0,
                    "output_usd_per_1k_tokens": 10.0,
                }
                for name, family in [("extractor", "family_a"), ("verifier_a", "family_b"), ("verifier_b", "family_c")]
            }
            condition = {"condition_id": "budget-test", "extractor_model": "extractor", "verifier_models": ["verifier_a", "verifier_b"]}
            config = {
                "models": models, "conditions": [condition],
                "settings": {"max_tokens": 500, "max_preflight_estimated_cost_usd": 0.000001},
            }
            with self.assertRaisesRegex(RuntimeError, "exceeds configured budget"):
                run_condition(
                    config=config, condition=condition, split="development",
                    prepared_dir=prepared, output_dir=root / "should-not-run", max_tasks=1,
                )
            self.assertFalse((root / "should-not-run").exists())

    def test_provider_failure_is_logged_and_forces_escalation(self):
        cases = [self.make_case("C0", f"U-00-{i:03d}") for i in range(10)]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "cases.jsonl"
            benchmark.write_text("".join(json.dumps(x) + "\n" for x in cases))
            prepared = root / "prepared"
            prepare_tasks(benchmark, prepared)
            models = {
                "extractor": {"model": "mock-extractor", "provider": "mock", "base_url": "https://example.invalid/v1", "family_id": "family_a", "api_key_env": "EXP3_TEST_KEY"},
                "verifier_a": {"model": "mock-verifier-a", "provider": "mock", "base_url": "https://example.invalid/v1", "family_id": "family_b", "api_key_env": "EXP3_TEST_KEY"},
                "verifier_b": {"model": "mock-verifier-b", "provider": "mock", "base_url": "https://example.invalid/v1", "family_id": "family_c", "api_key_env": "EXP3_TEST_KEY"},
            }
            condition = {"condition_id": "mock-failure", "extractor_model": "extractor", "verifier_models": ["verifier_a", "verifier_b"]}
            config = {"models": models, "conditions": [condition], "settings": {"max_retries": 0, "timeout_seconds": 1}}
            previous = os.environ.get("EXP3_TEST_KEY")
            os.environ["EXP3_TEST_KEY"] = "test-only-not-a-real-key"
            try:
                def fail_transport(url, headers, body):
                    raise RuntimeError("simulated provider outage")
                summary = run_condition(
                    config=config, condition=condition, split="development",
                    prepared_dir=prepared, output_dir=root / "run",
                    max_tasks=1, transport=fail_transport,
                )
            finally:
                if previous is None:
                    os.environ.pop("EXP3_TEST_KEY", None)
                else:
                    os.environ["EXP3_TEST_KEY"] = previous
            rows = list(csv.DictReader((root / "run/case_results.csv").open()))
            manifest = json.loads((root / "run/run_manifest.json").read_text())
            provider_errors = (root / "run/provider_errors.jsonl").read_text().splitlines()
            self.assertEqual(rows[0]["controller_action"], "ESCALATE")
            self.assertEqual(rows[0]["provider_error"], "True")
            self.assertEqual(manifest["status"], "completed_with_provider_errors")
            self.assertEqual(manifest["provider_error_count"], 1)
            self.assertEqual(len(provider_errors), 1)

    def test_v1_gate_uses_family_labels_as_dependency_groups(self):
        from experiments.exp3_real_models.harness import evaluate_case
        case = self.make_case("C0", "U-00-000")
        extraction = {"quantity": 5, "gross_weight": 7.5, "hs": "8542", "confidence": 0.99}
        same_family = [
            {"model_id": "m1", "family_id": "family_a", "normalized": {"accept": True, "confidence": 0.9}, "parse_ok": True},
            {"model_id": "m2", "family_id": "family_a", "normalized": {"accept": True, "confidence": 0.9}, "parse_ok": True},
        ]
        cross_family = [
            {"model_id": "m1", "family_id": "family_a", "normalized": {"accept": True, "confidence": 0.9}, "parse_ok": True},
            {"model_id": "m2", "family_id": "family_b", "normalized": {"accept": True, "confidence": 0.9}, "parse_ok": True},
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

