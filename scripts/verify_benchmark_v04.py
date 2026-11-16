from collections import Counter, defaultdict
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.generate_benchmark_v04 import canonical_hash, FAMILIES


def load_jsonl(path):
    if not path.exists():
        raise SystemExit(f"Missing generated file: {path}. Run scripts/generate_benchmark_v04.py")
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main():
    bench = ROOT / "data" / "benchmark_v0.4"
    cases = load_jsonl(bench / "cases.jsonl")
    underlying = load_jsonl(bench / "underlying.jsonl")
    manifest = json.loads((bench / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["benchmark_version"] == "0.4"
    assert len(underlying) == 700 and len(cases) == 1400
    assert len({x["case_id"] for x in cases}) == 1400
    assert len({x["underlying_id"] for x in underlying}) == 700
    assert len({x["fingerprint"] for x in underlying}) == 700
    assert manifest["pair_integrity_failures"] == 0

    by_id = {x["underlying_id"]: x for x in underlying}
    groups = defaultdict(list)
    for case in cases:
        source = by_id[case["pair_id"]]
        assert case["observable"] == source["observable"]
        assert case["fingerprint"] == source["fingerprint"]
        groups[case["pair_id"]].append(case)
    for pair_id, pair in groups.items():
        assert len(pair) == 2
        assert {x["action"]["risk_level"] for x in pair} == {"LOW", "HIGH"}
        assert canonical_hash(pair[0]["observable"]) == canonical_hash(pair[1]["observable"])
        high = next(x for x in pair if x["action"]["risk_level"] == "HIGH")
        assert high["safe_to_act"] is by_id[pair_id]["high_safe_to_act"]

    family_counts = dict(Counter(x["family"] for x in cases))
    assert set(family_counts) == set(FAMILIES)
    assert all(v == 100 for v in family_counts.values())
    for item in underlying:
        obs = item["observable"]
        instances = obs["document_instances"]
        provenance = obs["provenance"]
        kinds = [x["kind"] for x in instances]
        duplicate = len(kinds) != len(set(kinds))
        digest_valid = provenance["document_set_sha256"] == canonical_hash(instances)
        if item["family"] == "C12_duplicate_document_kind":
            assert duplicate and not item["high_safe_to_act"]
        if item["family"] == "C13_corrupted_provenance":
            assert not digest_valid and not item["high_safe_to_act"]
        if item["family"] == "C10_missing_invoice":
            assert obs["documents"]["invoice"] is None and not item["high_safe_to_act"]
        if item["family"] == "C11_missing_packing_list":
            assert obs["documents"]["packing_list"] is None and not item["high_safe_to_act"]

    print("PASS: benchmark v0.4; 1,400 cases; 700 paired situations; 14 families; 100 cases per family; 0 pair failures.")


if __name__ == "__main__":
    main()
