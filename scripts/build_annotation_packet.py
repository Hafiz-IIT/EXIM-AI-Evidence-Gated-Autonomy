"""Create a blinded, stratified human-annotation packet from benchmark v0.4."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUTPUT = ROOT / "results" / "annotation_validation"
SEED = 20261123
ANNOTATION_FIELDS = (
    "evidence_sufficiency",
    "source_integrity",
    "document_freshness",
    "cross_document_consistency",
    "recommended_disposition",
    "confidence_1_5",
    "rationale",
)
PACKET_FIELDS = (
    "annotation_id",
    "action_name",
    "action_risk_level",
    "action_reversibility",
    "action_external_effect",
    "observable_json",
    "annotator_id",
    *ANNOTATION_FIELDS,
)
KEY_FIELDS = (
    "annotation_id", "case_id", "pair_id", "family", "severity",
    "gold_safe_to_act", "fault_json", "fingerprint",
)


def load_cases(path=SOURCE):
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run scripts/generate_benchmark_v04.py first."
        )
    with path.open(encoding="utf-8") as handle:
        cases = [json.loads(line) for line in handle if line.strip()]
    if not cases:
        raise ValueError("Benchmark contains no cases")
    return cases


def annotation_id(case_id, seed):
    digest = hashlib.sha256(f"{seed}|{case_id}".encode("utf-8")).hexdigest()[:12]
    return f"ANN-{digest.upper()}"


def build_packet(cases, per_family=10, seed=SEED):
    if per_family < 1:
        raise ValueError("per_family must be positive")
    groups = defaultdict(lambda: defaultdict(list))
    for case in cases:
        groups[case["family"]][case["pair_id"]].append(case)

    rng = random.Random(seed)
    packet_rows = []
    key_rows = []
    for family in sorted(groups):
        pair_ids = sorted(groups[family])
        if len(pair_ids) < per_family:
            raise ValueError(f"Family {family} has only {len(pair_ids)} pairs")
        for pair_id in rng.sample(pair_ids, per_family):
            pair = groups[family][pair_id]
            if len(pair) != 2:
                raise ValueError(f"Pair {pair_id} does not contain exactly two risk variants")
            for case in pair:
                ann_id = annotation_id(case["case_id"], seed)
                action = case["action"]
                packet_rows.append({
                    "annotation_id": ann_id,
                    "action_name": action["name"],
                    "action_risk_level": action["risk_level"],
                    "action_reversibility": action["reversibility"],
                    "action_external_effect": action["external_effect"],
                    "observable_json": json.dumps(
                        case["observable"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
                    ),
                    "annotator_id": "",
                    **{field: "" for field in ANNOTATION_FIELDS},
                })
                key_rows.append({
                    "annotation_id": ann_id,
                    "case_id": case["case_id"],
                    "pair_id": pair_id,
                    "family": family,
                    "severity": case["severity"],
                    "gold_safe_to_act": str(bool(case["safe_to_act"])).lower(),
                    "fault_json": json.dumps(case["fault"], sort_keys=True),
                    "fingerprint": case["fingerprint"],
                })
    rng.shuffle(packet_rows)
    rng.shuffle(key_rows)
    return packet_rows, key_rows


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=10)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    cases = load_cases()
    packet, key = build_packet(cases, args.per_family, args.seed)
    private_dir = OUTPUT / "private"
    shareable_dir = OUTPUT / "shareable"
    packet_path = shareable_dir / "annotation_packet.csv"
    key_path = private_dir / "annotation_key.csv"
    write_csv(packet_path, packet, PACKET_FIELDS)
    write_csv(key_path, key, KEY_FIELDS)

    def sha256(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    manifest = {
        "protocol": "blinded-stratified-human-annotation-v1",
        "source_benchmark": "v0.4",
        "source_cases": len(cases),
        "seed": args.seed,
        "sampled_pairs_per_family": args.per_family,
        "sampled_rows": len(packet),
        "family_count": len({row["family"] for row in key}),
        "annotator_packet_sha256": sha256(packet_path),
        "private_key_sha256": sha256(key_path),
        "blinding": {
            "packet_excludes": [
                "case_id", "pair_id", "family", "severity", "fault",
                "ground_truth", "safe_to_act", "fingerprint",
            ],
            "key_file_must_not_be_shared_with_annotators": True,
        },
        "status": "annotation infrastructure only; no human labels or agreement results generated",
    }
    (shareable_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
