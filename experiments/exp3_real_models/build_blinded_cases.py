from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def stable_hash(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_task(case: dict) -> dict:
    obs = case["observable"]
    task = {
        "case_id": case["case_id"],
        "pair_id": case["pair_id"],
        "action": case["action"],
        "documents": obs["documents"],
        "external_evidence": obs["external"],
        "missing": obs.get("missing", []),
    }
    task["task_hash"] = stable_hash(task)
    return task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        default="data/benchmark/cases.jsonl",
        help="Frozen benchmark cases JSONL",
    )
    parser.add_argument(
        "--out",
        default="data/exp3/blinded_cases.jsonl",
        help="Ground-truth-free model-facing cases",
    )
    args = parser.parse_args()

    src = Path(args.cases)
    dst = Path(args.out)
    dst.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with dst.open("w", encoding="utf-8") as f:
        for case in load_jsonl(src):
            task = build_task(case)
            assert "ground_truth" not in task
            assert "fault" not in task
            assert "safe_to_act" not in task
            f.write(json.dumps(task, sort_keys=True) + "\n")
            n += 1

    print(json.dumps({"written": n, "path": str(dst)}, indent=2))


if __name__ == "__main__":
    main()
