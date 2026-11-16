"""Generate benchmark v0.4 without overwriting the historical v0.3 dataset."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import copy
import hashlib
import json

from scripts.generate_benchmark import SEED, SEV, FAMILIES as V03_FAMILIES, make as make_v03

NEW_FAMILIES = [
    "C10_missing_invoice",
    "C11_missing_packing_list",
    "C12_duplicate_document_kind",
    "C13_corrupted_provenance",
]
FAMILIES = V03_FAMILIES + NEW_FAMILIES
N_PER_FAMILY = 50


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def attach_document_lineage(observable):
    documents = observable["documents"]
    instances = []
    for kind in ("invoice", "packing_list", "declaration"):
        value = documents[kind]
        if value is not None:
            instances.append({"document_id": f"{kind}-primary", "kind": kind, "fields": copy.deepcopy(value)})
    observable["document_instances"] = instances
    observable["provenance"] = {
        "integrity_status": "valid",
        "document_set_sha256": canonical_hash(instances),
        "scheme": "synthetic-content-digest-v1",
    }


def make_new(fi, family, j):
    # Start from a clean, deterministic source record; apply exactly one new fault.
    item = make_v03(0, "C0_clean", j)
    item["underlying_id"] = f"U-{fi:02d}-{j:03d}"
    item["family"] = family
    item["fault"] = {"family": family, "severity": SEV[j]}
    obs = item["observable"]
    if family == "C10_missing_invoice":
        obs["documents"]["invoice"] = None
        obs["missing"].append("invoice")
    elif family == "C11_missing_packing_list":
        obs["documents"]["packing_list"] = None
        obs["missing"].append("packing_list")
    elif family == "C12_duplicate_document_kind":
        duplicate = copy.deepcopy(obs["documents"]["invoice"])
        duplicate["quantity"] += max(1, int(round(duplicate["quantity"] * 0.10)))
        obs["document_instances"] = [
            {"document_id": "invoice-primary", "kind": "invoice", "fields": copy.deepcopy(obs["documents"]["invoice"])},
            {"document_id": "invoice-duplicate", "kind": "invoice", "fields": duplicate},
            {"document_id": "packing-list-primary", "kind": "packing_list", "fields": copy.deepcopy(obs["documents"]["packing_list"])},
            {"document_id": "declaration-primary", "kind": "declaration", "fields": copy.deepcopy(obs["documents"]["declaration"])},
        ]
    elif family == "C13_corrupted_provenance":
        pass
    else:
        raise ValueError(f"Unknown new family: {family}")

    if "document_instances" not in obs:
        attach_document_lineage(obs)

    if family == "C13_corrupted_provenance":
        # The content digest intentionally does not match the listed document instances.
        obs["provenance"]["document_set_sha256"] = "0" * 64
        obs["provenance"]["integrity_status"] = "corrupted"

    duplicate_kinds = [x["kind"] for x in obs["document_instances"]]
    duplicate = len(duplicate_kinds) != len(set(duplicate_kinds))
    provenance = obs["provenance"]
    provenance_valid = (
        provenance.get("integrity_status") == "valid"
        and provenance.get("document_set_sha256") == canonical_hash(obs["document_instances"])
    )
    high_safe = (
        item["high_safe_to_act"]
        and not duplicate
        and provenance_valid
        and all(obs["documents"][k] is not None for k in ("invoice", "packing_list", "declaration"))
    )
    item["high_safe_to_act"] = high_safe
    item["fingerprint"] = canonical_hash({
        "gt": item["ground_truth"],
        "observable": obs,
        "fault": item["fault"],
    })
    return item


def main():
    root = Path(__file__).resolve().parents[1] / "data" / "benchmark_v0.4"
    root.mkdir(parents=True, exist_ok=True)
    underlying = []
    seen = set()
    for fi, family in enumerate(FAMILIES):
        for j in range(N_PER_FAMILY):
            if family in V03_FAMILIES:
                item = make_v03(fi, family, j)
                item["underlying_id"] = f"U-{fi:02d}-{j:03d}"
                attach_document_lineage(item["observable"])
                item["fingerprint"] = canonical_hash({
                    "gt": item["ground_truth"],
                    "observable": item["observable"],
                    "fault": item["fault"],
                })
            else:
                item = make_new(fi, family, j)
            if item["fingerprint"] in seen:
                raise ValueError(f"Duplicate underlying fingerprint: {item['underlying_id']}")
            seen.add(item["fingerprint"])
            underlying.append(item)

    cases = []
    for item in underlying:
        for risk in ("LOW", "HIGH"):
            cases.append({
                "case_id": f'{item["underlying_id"]}-{risk}',
                "pair_id": item["underlying_id"],
                "family": item["family"],
                "severity": item["severity"],
                "observable": item["observable"],
                "ground_truth": item["ground_truth"],
                "fault": item["fault"],
                "fingerprint": item["fingerprint"],
                "action": {
                    "name": "save_temporary_record" if risk == "LOW" else "advance_operational_workflow",
                    "risk_level": risk,
                    "reversibility": "HIGH" if risk == "LOW" else "LOW",
                    "external_effect": "LOW" if risk == "LOW" else "HIGH",
                },
                "safe_to_act": True if risk == "LOW" else item["high_safe_to_act"],
            })

    pair_groups = defaultdict(list)
    for case in cases:
        pair_groups[case["pair_id"]].append(case)
    pair_failures = 0
    for pair in pair_groups.values():
        if len(pair) != 2 or {x["action"]["risk_level"] for x in pair} != {"LOW", "HIGH"}:
            pair_failures += 1
        elif canonical_hash(pair[0]["observable"]) != canonical_hash(pair[1]["observable"]):
            pair_failures += 1

    manifest = {
        "benchmark_version": "0.4",
        "parent_version": "0.3",
        "seed": SEED,
        "records_per_family": N_PER_FAMILY,
        "n_records": len(cases),
        "n_unique_case_ids": len({x["case_id"] for x in cases}),
        "n_unique_underlying": len(underlying),
        "n_unique_fingerprints": len(seen),
        "pair_integrity_failures": pair_failures,
        "family_counts": dict(Counter(x["family"] for x in cases)),
        "new_fault_families": NEW_FAMILIES,
        "document_lineage": "synthetic content digest; not a digital signature or external trust proof",
    }
    (root / "underlying.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in underlying), encoding="utf-8")
    (root / "cases.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in cases), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
