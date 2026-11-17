from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

SEED = 314159
SPLIT_FRACTIONS = {"dev": 0.20, "validation": 0.20, "test": 0.60}


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def render_case(case: Dict[str, Any]) -> str:
    """Render observable evidence without exposing hidden benchmark truth/fault labels."""
    o = case["observable"]
    docs = o["documents"]
    ext = o["external"]
    action = case["action"]

    lines = [
        "CASE EVIDENCE PACKET",
        f"Proposed action: {action['name']}",
        f"Action risk: {action['risk_level']}",
        f"Reversibility: {action['reversibility']}",
        f"External effect: {action['external_effect']}",
        "",
        "DOCUMENTS",
    ]
    for name in ("invoice", "packing_list", "declaration"):
        doc = docs.get(name)
        if doc is None:
            lines.append(f"{name}: MISSING")
        else:
            lines.append(
                f"{name}: quantity={doc['quantity']}; gross_weight={doc['gross_weight']}; "
                f"hs={doc['hs']}; issue_day={doc['issue_day']}"
            )

    auth = ext["authorization"]
    lines.extend(
        [
            "",
            "EXTERNAL OBSERVATIONS",
            f"measured_weight={ext['measured_weight']}",
            f"inspection_item_type={ext['inspection_item_type']}",
            f"evaluation_day={ext['evaluation_day']}",
            f"authorization_present={auth['present']}",
            f"authorization_issue_day={auth['issue_day']}",
            f"authorization_expiry_day={auth['expiry_day']}",
        ]
    )
    return "\n".join(lines) + "\n"


def stratified_pair_split(cases: Iterable[Dict[str, Any]]) -> Dict[str, str]:
    by_pair: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for case in cases:
        by_pair[case["pair_id"]].append(case)

    strata: Dict[tuple, List[str]] = defaultdict(list)
    for pair_id, pair_cases in by_pair.items():
        exemplar = pair_cases[0]
        strata[(exemplar["family"], exemplar["severity"])].append(pair_id)

    assignment: Dict[str, str] = {}
    rng = random.Random(SEED)

    for key in sorted(strata):
        ids = sorted(strata[key])
        rng.shuffle(ids)
        n = len(ids)
        n_dev = round(n * SPLIT_FRACTIONS["dev"])
        n_val = round(n * SPLIT_FRACTIONS["validation"])
        # Remainder always goes to test so every pair is assigned exactly once.
        for pair_id in ids[:n_dev]:
            assignment[pair_id] = "dev"
        for pair_id in ids[n_dev:n_dev + n_val]:
            assignment[pair_id] = "validation"
        for pair_id in ids[n_dev + n_val:]:
            assignment[pair_id] = "test"

    return assignment


def ensure_pair_integrity(cases: List[Dict[str, Any]], assignment: Dict[str, str]) -> None:
    seen = defaultdict(set)
    for case in cases:
        seen[case["pair_id"]].add(case["action"]["risk_level"])
        assert case["pair_id"] in assignment
    broken = {p: risks for p, risks in seen.items() if risks != {"LOW", "HIGH"}}
    if broken:
        raise ValueError(f"Broken LOW/HIGH pairs: {broken}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="data/benchmark/cases.jsonl")
    parser.add_argument("--out", default="data/exp3")
    args = parser.parse_args()

    cases_path = Path(args.cases)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if not cases_path.exists():
        raise SystemExit(
            f"{cases_path} is missing. Run `python scripts/generate_benchmark.py` first."
        )

    cases = load_jsonl(cases_path)
    assignment = stratified_pair_split(cases)
    ensure_pair_integrity(cases, assignment)

    manifest = {
        "experiment": "exp3",
        "benchmark_version": "0.3",
        "split_seed": SEED,
        "fractions": SPLIT_FRACTIONS,
        "n_cases": len(cases),
        "n_pairs": len(assignment),
        "pairs": {},
    }

    task_files = {split: (out / f"tasks_{split}.jsonl").open("w", encoding="utf-8") for split in SPLIT_FRACTIONS}
    try:
        for pair_id in sorted(assignment):
            split = assignment[pair_id]
            pair_cases = sorted(
                [c for c in cases if c["pair_id"] == pair_id],
                key=lambda c: c["action"]["risk_level"],
            )
            manifest["pairs"][pair_id] = {
                "split": split,
                "case_ids": [c["case_id"] for c in pair_cases],
                "input_hashes": {},
            }
            for case in pair_cases:
                rendered = render_case(case)
                rendered_hash = sha256_text(rendered)
                task = {
                    "case_id": case["case_id"],
                    "pair_id": case["pair_id"],
                    "split": split,
                    "action": case["action"],
                    "rendered_input": rendered,
                    "rendered_sha256": rendered_hash,
                }
                # Deliberately exclude: family, severity, fault, ground_truth, safe_to_act.
                task_files[split].write(json.dumps(task, ensure_ascii=False) + "\n")
                manifest["pairs"][pair_id]["input_hashes"][case["case_id"]] = rendered_hash
    finally:
        for fh in task_files.values():
            fh.close()

    manifest_text = json.dumps(manifest, sort_keys=True, indent=2)
    (out / "split_manifest.json").write_text(manifest_text + "\n", encoding="utf-8")
    (out / "split_manifest.sha256").write_text(sha256_text(manifest_text) + "\n", encoding="utf-8")

    counts = defaultdict(int)
    for split in assignment.values():
        counts[split] += 1
    print({"pairs": dict(counts), "manifest_sha256": sha256_text(manifest_text)})


if __name__ == "__main__":
    main()
