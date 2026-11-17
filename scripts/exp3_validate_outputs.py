from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

ALLOWED_ROLES = {"extractor", "classifier", "verifier_a", "verifier_b", "verifier_c", "rule_checker"}


def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"{path}:{lineno}: invalid JSON: {e}") from e


def require(obj: Dict[str, Any], key: str, kind=None):
    if key not in obj:
        raise ValueError(f"missing required field: {key}")
    if kind is not None and not isinstance(obj[key], kind):
        raise ValueError(f"field {key!r} must be {kind}, got {type(obj[key])}")
    return obj[key]


def validate_record(r: Dict[str, Any]) -> None:
    require(r, "case_id", str)
    require(r, "split", str)
    role = require(r, "role", str)
    if role not in ALLOWED_ROLES:
        raise ValueError(f"unsupported role {role!r}")

    require(r, "provider", str)
    require(r, "model", str)
    require(r, "timestamp", str)
    require(r, "input_sha256", str)
    require(r, "system_prompt_sha256", str)
    require(r, "user_prompt_sha256", str)
    require(r, "raw_response", str)
    require(r, "parse_ok", bool)
    require(r, "latency_ms", (int, float))
    require(r, "retry_count", int)

    if "temperature" in r and not isinstance(r["temperature"], (int, float, type(None))):
        raise ValueError("temperature must be numeric or null")

    if "token_usage" in r and not isinstance(r["token_usage"], dict):
        raise ValueError("token_usage must be an object")

    if "cost_usd" in r and not isinstance(r["cost_usd"], (int, float, type(None))):
        raise ValueError("cost_usd must be numeric or null")

    if r["parse_ok"]:
        parsed = require(r, "parsed", dict)
        if role == "extractor":
            for k in ("quantity", "gross_weight", "hs", "confidence", "abstain"):
                if k not in parsed:
                    raise ValueError(f"extractor parsed output missing {k}")
        elif role.startswith("verifier") or role == "rule_checker":
            for k in ("accept", "confidence", "issues", "requested_evidence"):
                if k not in parsed:
                    raise ValueError(f"verifier parsed output missing {k}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Append-only JSONL output log")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        raise SystemExit(f"missing file: {path}")

    n = 0
    keys = set()
    for r in load_jsonl(path):
        validate_record(r)
        key = (r["case_id"], r["role"], r["provider"], r["model"])
        if key in keys:
            raise ValueError(f"duplicate record key: {key}")
        keys.add(key)
        n += 1

    print({"validated_records": n, "unique_keys": len(keys)})


if __name__ == "__main__":
    main()
