"""Provider-neutral (OpenAI-compatible) Experiment 3 harness.

The public task builder never copies benchmark oracle fields into model-facing
requests. The evaluator reads a separate private map only after responses have
been persisted. This harness currently evaluates Evidence Gate v1 only; exact
historical v2/v3 controllers remain blocked on issue #3.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from src.core import evidence_gate_v1

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
FORBIDDEN_PUBLIC_KEYS = {
    "ground_truth", "fault", "safe_to_act", "family", "severity",
    "fingerprint", "pair_id", "underlying_id", "case_id",
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _opaque_task_id(case_id: str, layout: str) -> str:
    return hashlib.sha256(f"exp3-task-v1|{case_id}|{layout}".encode()).hexdigest()[:20]


def _render_document(kind: str, document: dict | None, layout: str) -> str:
    if document is None:
        return f"[{kind.replace('_', ' ').upper()} NOT PROVIDED]"
    fields = [
        ("quantity", document.get("quantity")),
        ("gross_weight", document.get("gross_weight")),
        ("hs", document.get("hs")),
        ("issue_day", document.get("issue_day")),
    ]
    if layout == "table":
        lines = [f"{kind.replace('_', ' ').title()}",
                 "| Field | Declared value |", "|---|---|"]
        lines.extend(f"| {key} | {value} |" for key, value in fields if value is not None)
        return "\n".join(lines)
    if layout == "ood":
        labels = {
            "quantity": "QTY / PACKED UNITS",
            "gross_weight": "GROSS WT (KG)",
            "hs": "TARIFF / HS CODE",
            "issue_day": "DOC ISSUE DAY",
        }
        order = ("hs", "issue_day", "quantity", "gross_weight")
        lines = [f"{kind.replace('_', ' ').upper()} — ITEM DECLARATION"]
        for key in order:
            value = document.get(key)
            if value is not None:
                lines.append(f"{labels[key]} : {value}")
        return "\n".join(lines)
    lines = [f"DOCUMENT TYPE: {kind.replace('_', ' ').upper()}"]
    lines.extend(f"{key}: {value}" for key, value in fields if value is not None)
    return "\n".join(lines)


def render_documents(documents: dict, layout: str = "canonical") -> str:
    return "\n\n".join(
        _render_document(kind, documents.get(kind), layout)
        for kind in ("invoice", "packing_list", "declaration")
    )


def assign_splits(high_risk_cases: list[dict]) -> dict[str, str]:
    """Stable 60/20/20 split by underlying pair, stratified within family."""
    grouped: dict[str, set[str]] = defaultdict(set)
    for case in high_risk_cases:
        grouped[case["family"]].add(case["pair_id"])
    assignments = {}
    for family, pair_ids in grouped.items():
        ordered = sorted(pair_ids, key=lambda p: hashlib.sha256(f"exp3-split-v1|{family}|{p}".encode()).hexdigest())
        n = len(ordered)
        n_dev = int(n * 0.60)
        n_val = int(n * 0.20)
        for index, pair_id in enumerate(ordered):
            split = "development" if index < n_dev else "validation" if index < n_dev + n_val else "final_holdout"
            assignments[pair_id] = split
    return assignments


def build_public_task(case: dict, layout: str) -> dict:
    """Build a model-facing task from allowed observable evidence only."""
    observable = case["observable"]
    external = observable["external"]
    auth = external["authorization"]
    task = {
        "task_id": _opaque_task_id(case["case_id"], layout),
        "action_context": {
            "risk_level": case["action"]["risk_level"],
            "reversibility": case["action"]["reversibility"],
            "external_effect": case["action"]["external_effect"],
        },
        "documents_text": render_documents(observable["documents"], layout),
        "external_observations": {
            "measured_weight": external["measured_weight"],
            "inspection_item_type": external["inspection_item_type"],
            "authorization": {
                "present": auth["present"],
                "issue_day": auth["issue_day"],
                "expiry_day": auth["expiry_day"],
            },
            "evaluation_day": external["evaluation_day"],
        },
    }
    assert_public_task_blinded(task)
    return task


def assert_public_task_blinded(value: Any) -> None:
    if isinstance(value, dict):
        leaked = FORBIDDEN_PUBLIC_KEYS.intersection(value.keys())
        if leaked:
            raise ValueError(f"forbidden oracle/identity keys in model-facing task: {sorted(leaked)}")
        for child in value.values():
            assert_public_task_blinded(child)
    elif isinstance(value, list):
        for child in value:
            assert_public_task_blinded(child)


def prepare_tasks(benchmark_path: Path, output_dir: Path) -> dict:
    cases = read_jsonl(benchmark_path)
    high = [case for case in cases if case["action"]["risk_level"] == "HIGH"]
    if not high:
        raise ValueError("benchmark contains no HIGH-risk cases")
    split_map = assign_splits(high)
    public_tasks = []
    private_map = []
    for case in high:
        split = split_map[case["pair_id"]]
        layouts = (
            [("development", "canonical")] if split == "development"
            else [("validation", "table")] if split == "validation"
            else [("final_holdout_id", "canonical"), ("final_holdout_ood", "ood")]
        )
        for split_name, layout in layouts:
            task = build_public_task(case, layout)
            public_tasks.append(task)
            private_map.append({
                "task_id": task["task_id"],
                "case_id": case["case_id"],
                "pair_id": case["pair_id"],
                "family": case["family"],
                "severity": case["severity"],
                "split": split_name,
                "safe_to_act": case["safe_to_act"],
                "ground_truth": case["ground_truth"],
                "action": case["action"],
                "observable": case["observable"],
            })
    public_dir = output_dir / "public"
    private_dir = output_dir / "private"
    write_jsonl(public_dir / "tasks.jsonl", public_tasks)
    write_jsonl(private_dir / "evaluation_map.jsonl", private_map)
    counts = Counter(item["split"] for item in private_map)
    manifest = {
        "protocol": "exp3-real-models-v1",
        "benchmark_path": str(benchmark_path),
        "benchmark_sha256": sha256_file(benchmark_path),
        "high_risk_case_count": len(high),
        "unique_underlying_pair_count": len(split_map),
        "public_task_count": len(public_tasks),
        "split_counts": dict(sorted(counts.items())),
        "public_tasks_sha256": sha256_file(public_dir / "tasks.jsonl"),
        "prompt_sha256": {
            name: sha256_file(PROMPT_DIR / name)
            for name in ("extract_v1.txt", "verify_v1.txt")
        },
        "split_rule": "deterministic SHA-256 ordering within benchmark family; 60% development, 20% validation, 20% final holdout by pair_id",
        "model_facing_blinding": "no case_id, pair_id, family, severity, fault, ground_truth, safe_to_act or fingerprint fields",
        "layouts": {"development": "canonical", "validation": "table", "final_holdout_id": "canonical", "final_holdout_ood": "ood"},
        "status": "prepared_only_no_model_calls",
    }
    (public_dir / "task_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8").strip()


def build_extraction_messages(task: dict) -> list[dict]:
    payload = {"action_context": task["action_context"], "documents_text": task["documents_text"]}
    return [
        {"role": "system", "content": load_prompt("extract_v1.txt")},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def build_verifier_messages(task: dict, extraction: dict) -> list[dict]:
    payload = {
        "action_context": task["action_context"],
        "documents_text": task["documents_text"],
        "external_observations": task["external_observations"],
        "extractor_claim": extraction,
    }
    return [
        {"role": "system", "content": load_prompt("verify_v1.txt")},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def parse_json_object(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^\`\`\`(?:json)?\s*", "", text)
        text = re.sub(r"\s*\`\`\`$", "", text)
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("model response must be a JSON object")
    return value


def normalize_extraction(value: dict) -> tuple[dict, bool]:
    try:
        if not {"quantity", "gross_weight", "hs", "confidence"}.issubset(value):
            raise ValueError("missing required extraction keys")
        quantity = value.get("quantity")
        weight = value.get("gross_weight")
        hs = value.get("hs")
        confidence = float(value.get("confidence", 0.0))
        if quantity is not None and (not isinstance(quantity, (int, float)) or isinstance(quantity, bool) or not math.isfinite(float(quantity))):
            raise ValueError("quantity must be numeric or null")
        if weight is not None and (not isinstance(weight, (int, float)) or isinstance(weight, bool) or not math.isfinite(float(weight))):
            raise ValueError("gross_weight must be numeric or null")
        if hs is not None and not isinstance(hs, str):
            raise ValueError("hs must be a string or null")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be in [0,1]")
        return {"quantity": quantity, "gross_weight": weight, "hs": hs, "confidence": confidence}, True
    except (TypeError, ValueError):
        return {"quantity": None, "gross_weight": None, "hs": None, "confidence": 0.0}, False


def normalize_verifier(value: dict) -> tuple[dict, bool]:
    accept = value.get("accept")
    confidence = value.get("confidence", 0.0)
    reasons = value.get("reason_codes", [])
    valid = isinstance(accept, bool) and isinstance(confidence, (int, float)) and not isinstance(confidence, bool) and 0 <= float(confidence) <= 1 and isinstance(reasons, list)
    if not valid:
        return {"accept": False, "confidence": 0.0, "reason_codes": ["invalid_model_response"]}, False
    return {"accept": accept, "confidence": float(confidence), "reason_codes": [str(x) for x in reasons]}, True


def _endpoint(base_url: str) -> str:
    value = base_url.rstrip("/")
    return value if value.endswith("/chat/completions") else value + "/chat/completions"


def call_openai_compatible(
    model_spec: dict,
    messages: list[dict],
    settings: dict,
    transport: Callable | None = None,
) -> dict:
    key_name = model_spec["api_key_env"]
    api_key = os.environ.get(key_name)
    if not api_key:
        raise RuntimeError(f"missing API credential in environment variable {key_name}")
    body = {
        "model": model_spec["model"],
        "messages": messages,
        "temperature": settings.get("temperature", 0),
        "max_tokens": settings.get("max_tokens", 500),
    }
    if settings.get("seed") is not None:
        body["seed"] = settings["seed"]
    if model_spec.get("json_mode", False):
        body["response_format"] = {"type": "json_object"}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = _endpoint(model_spec["base_url"])
    max_retries = int(settings.get("max_retries", 2))
    errors = []
    for attempt in range(max_retries + 1):
        started = time.perf_counter()
        try:
            if transport is None:
                request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(request, timeout=float(settings.get("timeout_seconds", 90))) as response:
                    raw = json.loads(response.read().decode("utf-8"))
            else:
                raw = transport(url, headers, body)
            latency_ms = (time.perf_counter() - started) * 1000
            content = raw["choices"][0]["message"]["content"]
            usage = raw.get("usage", {})
            prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
            completion_tokens = int(usage.get("completion_tokens", 0) or 0)
            in_price = model_spec.get("input_usd_per_1k_tokens")
            out_price = model_spec.get("output_usd_per_1k_tokens")
            cost = None if in_price is None or out_price is None else (
                prompt_tokens * float(in_price) + completion_tokens * float(out_price)
            ) / 1000.0
            return {
                "content": content,
                "raw_response": raw,
                "usage": usage,
                "latency_ms": latency_ms,
                "estimated_cost_usd": cost,
                "attempts": attempt + 1,
                "errors": errors,
            }
        except Exception as exc:
            errors.append({"attempt": attempt + 1, "error_type": type(exc).__name__, "message": str(exc)[:500]})
            if attempt >= max_retries:
                raise RuntimeError(json.dumps(errors)) from exc
            time.sleep(min(2 ** attempt, 8))
    raise RuntimeError("unreachable model call state")


def _numeric_equal(left, right, tolerance=1e-9) -> bool:
    try:
        return abs(float(left) - float(right)) <= tolerance
    except (TypeError, ValueError):
        return False


def extraction_matches_truth(extraction: dict, truth: dict) -> bool:
    return (
        _numeric_equal(extraction.get("quantity"), truth.get("quantity"))
        and _numeric_equal(extraction.get("gross_weight"), truth.get("gross_weight"))
        and extraction.get("hs") == truth.get("hs")
    )


def evaluate_case(case: dict, extraction: dict, verifier_results: list[dict]) -> dict:
    observable = json.loads(json.dumps(case["observable"]))
    observable.setdefault("machine", {})
    observable["machine"]["extraction"] = extraction
    observable["machine"]["classification"] = {"hs": extraction.get("hs"), "confidence": extraction.get("confidence", 0.0)}
    observable["machine"]["verifiers"] = [
        {
            "verifier_id": result["model_id"],
            "accept": result["normalized"]["accept"],
            "reliability": result["normalized"]["confidence"],
            "dependency_group": result["family_id"],
            "type": "external_model",
        }
        for result in verifier_results
    ]
    action = evidence_gate_v1({"observable": observable, "action": case["action"]})
    safe = bool(case["safe_to_act"])
    extraction_correct = extraction_matches_truth(extraction, case["ground_truth"])
    accepts = [item["normalized"]["accept"] for item in verifier_results]
    return {
        "controller_action": action,
        "safe_to_act": safe,
        "unsafe_act": action == "ACT" and not safe,
        "false_block": action != "ACT" and safe,
        "extraction_correct": extraction_correct,
        "verifier_accept_count": sum(bool(x) for x in accepts),
        "verifier_count": len(accepts),
        "verifier_cofailure": len(accepts) >= 2 and all(accepts) and not extraction_correct,
        "verifier_family_count": len({x["family_id"] for x in verifier_results}),
    }


def summarize_results(rows: list[dict]) -> dict:
    n = len(rows)
    safe_rows = [x for x in rows if x["safe_to_act"]]
    unsafe_rows = [x for x in rows if not x["safe_to_act"]]
    acts = [x for x in rows if x["controller_action"] == "ACT"]
    return {
        "n_cases": n,
        "unsafe_ACTs": sum(bool(x["unsafe_act"]) for x in rows),
        "ICAR_high": sum(bool(x["unsafe_act"]) for x in rows) / n if n else None,
        "false_blocks": sum(bool(x["false_block"]) for x in rows),
        "false_block_rate": sum(bool(x["false_block"]) for x in rows) / len(safe_rows) if safe_rows else None,
        "safe_case_count": len(safe_rows),
        "unsafe_case_count": len(unsafe_rows),
        "ACT_count": len(acts),
        "coverage": len(acts) / n if n else None,
        "verifier_cofailure_count": sum(bool(x["verifier_cofailure"]) for x in rows),
        "mean_verifier_family_count": sum(x["verifier_family_count"] for x in rows) / n if n else None,
        "total_latency_ms": sum(float(x.get("total_latency_ms") or 0) for x in rows),
        "estimated_cost_usd": None if any(x.get("estimated_cost_usd") is None for x in rows) else sum(float(x["estimated_cost_usd"]) for x in rows),
    }


def run_condition(
    *,
    config: dict,
    condition: dict,
    split: str,
    prepared_dir: Path,
    output_dir: Path,
    max_tasks: int | None = None,
    transport: Callable | None = None,
) -> dict:
    public_tasks = {x["task_id"]: x for x in read_jsonl(prepared_dir / "public" / "tasks.jsonl")}
    private_rows = [x for x in read_jsonl(prepared_dir / "private" / "evaluation_map.jsonl") if x["split"] == split]
    if condition.get("holdout_only") and not split.startswith("final_holdout"):
        raise ValueError("holdout-only model condition cannot run on development/validation")
    if any(config["models"][name].get("holdout_only") for name in [condition["extractor_model"], *condition["verifier_models"]]) and not split.startswith("final_holdout"):
        raise ValueError("a holdout-only model cannot run on development/validation")
    if max_tasks is not None:
        if split.startswith("final_holdout"):
            raise ValueError("partial final-holdout runs are prohibited")
        private_rows = private_rows[:max_tasks]
    models = config["models"]
    extractor_spec = models[condition["extractor_model"]]
    verifier_specs = [models[name] for name in condition["verifier_models"]]
    if len(verifier_specs) != 2:
        raise ValueError("Experiment 3 requires exactly two verifier roles")
    prompt_hashes = {
        name: sha256_file(PROMPT_DIR / name)
        for name in ("extract_v1.txt", "verify_v1.txt")
    }
    model_identity = {
        "extractor": condition["extractor_model"],
        "verifiers": condition["verifier_models"],
        "families": [extractor_spec["family_id"]] + [x["family_id"] for x in verifier_specs],
    }
    if split.startswith("final_holdout"):
        freeze = config.get("freeze", {})
        expected_model_hash = sha256_bytes(canonical_json({"models": models, "conditions": config["conditions"]}))
        task_manifest = json.loads((prepared_dir / "public" / "task_manifest.json").read_text(encoding="utf-8"))
        if freeze.get("status") != "frozen" or not freeze.get("frozen_at"):
            raise ValueError("final holdout requires a frozen configuration with frozen_at")
        if freeze.get("prompt_sha256") != prompt_hashes:
            raise ValueError("final holdout prompt hashes differ from frozen values")
        if freeze.get("benchmark_sha256") != task_manifest["benchmark_sha256"]:
            raise ValueError("final holdout benchmark hash differs from frozen value")
        if freeze.get("model_config_sha256") != expected_model_hash:
            raise ValueError("final holdout model/condition configuration differs from frozen value")
    output_dir.mkdir(parents=True, exist_ok=True)
    run_started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    raw_path = output_dir / "raw_responses.jsonl"
    errors_path = output_dir / "retry_errors.jsonl"
    rows = []
    raw_records = []
    error_records = []
    raw_path.write_text("", encoding="utf-8")
    errors_path.write_text("", encoding="utf-8")

    def persist_raw(record):
        raw_records.append(record)
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\\n")

    def persist_errors(records):
        for record in records:
            error_records.append(record)
            with errors_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\\n")
    for private in private_rows:
        task = public_tasks[private["task_id"]]
        assert_public_task_blinded(task)
        extractor_call = call_openai_compatible(extractor_spec, build_extraction_messages(task), config["settings"], transport)
        persist_raw({
            "task_id": task["task_id"], "role": "extractor", "model_id": condition["extractor_model"],
            "family_id": extractor_spec["family_id"], "prompt_sha256": prompt_hashes["extract_v1.txt"],
            "content": extractor_call["content"], "raw_response": extractor_call["raw_response"],
            "usage": extractor_call["usage"], "latency_ms": extractor_call["latency_ms"],
            "estimated_cost_usd": extractor_call["estimated_cost_usd"], "attempts": extractor_call["attempts"],
        })
        persist_errors([{"task_id": task["task_id"], "role": "extractor", **e} for e in extractor_call["errors"]])
        try:
            extraction_raw = parse_json_object(extractor_call["content"])
            extraction, extraction_ok = normalize_extraction(extraction_raw)
        except Exception:
            extraction, extraction_ok = normalize_extraction({})
        verifier_results = []
        for index, (model_name, spec) in enumerate(zip(condition["verifier_models"], verifier_specs), start=1):
            call = call_openai_compatible(spec, build_verifier_messages(task, extraction), config["settings"], transport)
            try:
                verifier_raw = parse_json_object(call["content"])
                normalized, verifier_ok = normalize_verifier(verifier_raw)
            except Exception:
                normalized, verifier_ok = normalize_verifier({})
            result = {"model_id": model_name, "family_id": spec["family_id"], "normalized": normalized, "parse_ok": verifier_ok}
            verifier_results.append(result)
            persist_raw({
                "task_id": task["task_id"], "role": f"verifier_{index}", "model_id": model_name,
                "family_id": spec["family_id"], "prompt_sha256": prompt_hashes["verify_v1.txt"],
                "content": call["content"], "raw_response": call["raw_response"],
                "usage": call["usage"], "latency_ms": call["latency_ms"],
                "estimated_cost_usd": call["estimated_cost_usd"], "attempts": call["attempts"],
            })
            persist_errors([{"task_id": task["task_id"], "role": f"verifier_{index}", **e} for e in call["errors"]])
        metrics = evaluate_case(private, extraction, verifier_results)
        calls = [extractor_call]
        # The verifier calls are present in raw_records; recover their per-case metrics from raw records.
        case_raw = [x for x in raw_records if x["task_id"] == task["task_id"]]
        total_latency = sum(float(x["latency_ms"]) for x in case_raw)
        costs = [x["estimated_cost_usd"] for x in case_raw]
        total_cost = None if any(x is None for x in costs) else sum(float(x) for x in costs)
        rows.append({
            "task_id": task["task_id"], "case_id": private["case_id"], "split": split,
            "condition": condition["condition_id"], "controller_action": metrics["controller_action"],
            "safe_to_act": metrics["safe_to_act"], "unsafe_act": metrics["unsafe_act"],
            "false_block": metrics["false_block"], "extraction_correct": metrics["extraction_correct"],
            "extraction_parse_ok": extraction_ok,
            "verifier_accept_count": metrics["verifier_accept_count"], "verifier_count": metrics["verifier_count"],
            "verifier_cofailure": metrics["verifier_cofailure"], "verifier_family_count": metrics["verifier_family_count"],
            "verifier_families": ";".join(x["family_id"] for x in verifier_results),
            "total_latency_ms": total_latency, "estimated_cost_usd": total_cost,
        })
    csv_path = output_dir / "case_results.csv"
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    summary = summarize_results(rows)
    summary.update({"split": split, "condition": condition["condition_id"], "model_identity": model_identity})
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    task_manifest = json.loads((prepared_dir / "public" / "task_manifest.json").read_text(encoding="utf-8"))
    run_manifest = {
        "protocol": "exp3-real-models-v1",
        "status": "completed" if rows else "empty",
        "started_at_utc": run_started_at,
        "benchmark_sha256": task_manifest["benchmark_sha256"],
        "task_manifest_sha256": sha256_file(prepared_dir / "public" / "task_manifest.json"),
        "prompt_sha256": prompt_hashes,
        "model_identity": model_identity,
        "model_specs": {
            name: {k: v for k, v in spec.items() if k != "api_key"}
            for name, spec in models.items()
        },
        "settings": config["settings"],
        "split": split,
        "condition": condition["condition_id"],
        "n_cases": len(rows),
        "raw_responses_sha256": sha256_file(raw_path),
        "case_results_sha256": sha256_file(csv_path) if csv_path.exists() else None,
        "summary_sha256": sha256_file(output_dir / "summary.json"),
        "retry_error_count": len(error_records),
        "note": "Family IDs are configuration labels, not proof of independent training, ownership, data or infrastructure.",
    }
    (output_dir / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
    return summary
