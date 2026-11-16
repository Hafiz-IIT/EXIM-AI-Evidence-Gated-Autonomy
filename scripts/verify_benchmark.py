from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "data" / "benchmark"


def load_jsonl(path):
    if not path.exists():
        raise SystemExit(f"Missing generated file: {path}. Run scripts/generate_benchmark.py")
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


cases = load_jsonl(BENCH / "cases.jsonl")
underlying = load_jsonl(BENCH / "underlying.jsonl")
manifest_path = BENCH / "manifest.json"
if not manifest_path.exists():
    raise SystemExit("Missing generated manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

assert len(cases) == manifest["n_records"] == 1000
assert len(underlying) == manifest["n_unique_underlying"] == 500
assert len({case["case_id"] for case in cases}) == manifest["n_unique_case_ids"] == 1000
assert len({case["pair_id"] for case in cases}) == 500
assert len({case["fingerprint"] for case in cases}) == manifest["n_unique_fingerprints"] == 500
assert len({item["underlying_id"] for item in underlying}) == 500

underlying_by_id = {item["underlying_id"]: item for item in underlying}
assert len(underlying_by_id) == len(underlying)

for item in underlying:
    expected = digest({
        "gt": item["ground_truth"],
        "observable": item["observable"],
        "fault": item["fault"],
    })
    assert item["fingerprint"] == expected

pair_groups = defaultdict(list)
for case in cases:
    pair_groups[case["pair_id"]].append(case)
    source = underlying_by_id[case["pair_id"]]
    assert case["fingerprint"] == source["fingerprint"]
    assert case["ground_truth"] == source["ground_truth"]
    assert case["observable"] == source["observable"]
    assert case["fault"] == source["fault"]

pair_failures = 0
for pair in pair_groups.values():
    if len(pair) != 2 or {item["action"]["risk_level"] for item in pair} != {"LOW", "HIGH"}:
        pair_failures += 1
    elif digest(pair[0]["observable"]) != digest(pair[1]["observable"]):
        pair_failures += 1
    else:
        source = underlying_by_id[pair[0]["pair_id"]]
        for item in pair:
            expected_safe = True if item["action"]["risk_level"] == "LOW" else source["high_safe_to_act"]
            if item["safe_to_act"] is not expected_safe:
                pair_failures += 1

assert pair_failures == manifest["pair_integrity_failures"] == 0

family_counts = dict(Counter(case["family"] for case in cases))
assert family_counts == manifest["family_counts"]
assert set(family_counts.values()) == {100}

print(
    "PASS: 1,000 cases; 500 underlying situations; "
    "1,000 unique case IDs; 500 fingerprints; "
    "0 pair-integrity failures; 100 cases per family."
)
