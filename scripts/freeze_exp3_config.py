from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


import argparse
import hashlib
import json
import time
from pathlib import Path

from experiments.exp3_real_models.harness import (
    PROMPT_DIR, canonical_json, sha256_bytes, sha256_file
)


def main():
    parser = argparse.ArgumentParser(description="Freeze Experiment 3 prompts, benchmark and model configuration before holdout.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--prepared-dir", type=Path, default=Path("results/exp3_real_models"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    models = config["models"]
    conditions = config["conditions"]
    for name, spec in models.items():
        if not spec.get("model") or "REPLACE_WITH" in spec["model"] or ".example" in spec.get("base_url", ""):
            raise SystemExit(f"model {name} still contains placeholder identity")
        for field in ("provider", "base_url", "family_id", "api_key_env"):
            if not spec.get(field):
                raise SystemExit(f"model {name} missing {field}")
    used_holdout = set()
    for condition in conditions:
        if len(condition.get("verifier_models", [])) != 2:
            raise SystemExit(f"{condition['condition_id']} must have exactly two verifier roles")
        for name in [condition["extractor_model"], *condition["verifier_models"]]:
            if name not in models:
                raise SystemExit(f"condition references unknown model {name}")
            if models[name].get("holdout_only"):
                used_holdout.add(name)
                if not condition.get("holdout_only"):
                    raise SystemExit(f"holdout-only model {name} appears in a non-holdout condition")
    for name, spec in models.items():
        if spec.get("holdout_only") and name not in used_holdout:
            raise SystemExit(f"holdout-only model {name} is not used by a holdout-only condition")
    task_manifest = json.loads((args.prepared_dir / "public" / "task_manifest.json").read_text(encoding="utf-8"))
    prompt_hashes = {
        "extract_v1.txt": sha256_file(PROMPT_DIR / "extract_v1.txt"),
        "verify_v1.txt": sha256_file(PROMPT_DIR / "verify_v1.txt"),
    }
    model_hash = sha256_bytes(canonical_json({"models": models, "conditions": conditions}))
    config["freeze"] = {
        "status": "frozen",
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "benchmark_sha256": task_manifest["benchmark_sha256"],
        "prompt_sha256": prompt_hashes,
        "model_config_sha256": model_hash,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"freeze": config["freeze"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
