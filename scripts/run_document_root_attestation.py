"""Synthetic document-root attestation threat experiments on benchmark v0.4.

All private keys are deterministic test keys. This is a protocol experiment,
not a production key-management deployment.
"""
from __future__ import annotations

import csv
import copy
import hashlib
import json
import os
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from src.provenance import create_document_root_attestation, verify_document_root_attestation

BENCH = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUT = ROOT / "results" / "document_root_attestation"
NOW = 1_800_000_000


def test_key(label: str) -> Ed25519PrivateKey:
    """Deterministic experiment key; never use outside reproducible tests."""
    seed = hashlib.sha256(("EGA-DOCUMENT-ROOT-EXPERIMENT-v1|" + label).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def load_cases():
    with BENCH.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        raise ValueError(f"Refusing to write empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def issue(case, key, key_id, tenant_id, nonce):
    obs = case["observable"]
    return create_document_root_attestation(
        signer_id="synthetic-document-root",
        key_id=key_id,
        tenant_id=tenant_id,
        case_id=case["case_id"],
        document_instances=obs["document_instances"],
        normalized_documents=obs["documents"],
        private_key=key,
        issued_at=NOW - 10,
        expires_at=NOW + 3600,
        nonce=nonce,
    )


def verify(record, case, keyring, revoked=(), tenant=None, consumed=None):
    obs = case["observable"]
    return verify_document_root_attestation(
        record,
        trusted_keys=keyring,
        revoked_key_ids=set(revoked),
        expected_tenant_id=tenant or "tenant-demo",
        expected_case_id=case["case_id"],
        document_instances=obs["document_instances"],
        normalized_documents=obs["documents"],
        now=NOW,
        consumed_nonces=consumed,
    )


def rewrite_documents(case):
    rewritten = copy.deepcopy(case)
    obs = rewritten["observable"]
    # Coherently rewrite both raw instances and normalized map.
    for instance in obs["document_instances"]:
        fields = instance["fields"]
        if "quantity" in fields:
            fields["quantity"] = fields["quantity"] + 7
        if "gross_weight" in fields:
            fields["gross_weight"] = round(fields["gross_weight"] + 11.25, 2)
        if "hs" in fields:
            fields["hs"] = "9999"
    for fields in obs["documents"].values():
        if fields is None:
            continue
        if "quantity" in fields:
            fields["quantity"] = fields["quantity"] + 7
        if "gross_weight" in fields:
            fields["gross_weight"] = round(fields["gross_weight"] + 11.25, 2)
        if "hs" in fields:
            fields["hs"] = "9999"
    return rewritten


def main():
    cases = [c for c in load_cases() if c["action"]["risk_level"] == "HIGH"]
    key1 = test_key("root-k1")
    key2 = test_key("root-k2")
    keyring1 = {"doc-root-k1": key1.public_key()}
    keyring2 = {"doc-root-k2": key2.public_key()}
    rows = []

    for index, case in enumerate(cases):
        nonce = f"nonce-{index:05d}"
        original = copy.deepcopy(case)
        base_record = issue(original, key1, "doc-root-k1", "tenant-demo", nonce)

        ok, reason = verify(base_record, original, keyring1)
        rows.append({"scenario": "valid_baseline", "case_id": case["case_id"], "accepted": ok, "reason": reason})

        raw_tampered = copy.deepcopy(original)
        raw_tampered["observable"]["document_instances"][0]["fields"]["quantity"] += 1
        ok, reason = verify(base_record, raw_tampered, keyring1)
        rows.append({"scenario": "raw_instance_tamper", "case_id": case["case_id"], "accepted": ok, "reason": reason})

        coherent = rewrite_documents(original)
        ok, reason = verify(base_record, coherent, keyring1)
        rows.append({"scenario": "coherent_rewrite_without_root_key", "case_id": case["case_id"], "accepted": ok, "reason": reason})

        # Threat-model upper bound: compromise of the trusted document-root private key.
        compromised_record = issue(coherent, key1, "doc-root-k1", "tenant-demo", nonce + "-compromised")
        ok, reason = verify(compromised_record, coherent, keyring1)
        rows.append({"scenario": "trusted_root_signer_compromise", "case_id": case["case_id"], "accepted": ok, "reason": reason})

        ok, reason = verify(base_record, original, keyring1, revoked={"doc-root-k1"})
        rows.append({"scenario": "revoked_old_key", "case_id": case["case_id"], "accepted": ok, "reason": reason})

        rotated_record = issue(original, key2, "doc-root-k2", "tenant-demo", nonce + "-rotated")
        ok, reason = verify(rotated_record, original, keyring2, revoked={"doc-root-k1"})
        rows.append({"scenario": "rotated_new_key", "case_id": case["case_id"], "accepted": ok, "reason": reason})

        ok, reason = verify(base_record, original, keyring1, tenant="tenant-other")
        rows.append({"scenario": "cross_tenant_replay", "case_id": case["case_id"], "accepted": ok, "reason": reason})

        consumed = set()
        first_ok, first_reason = verify(base_record, original, keyring1, consumed=consumed)
        second_ok, second_reason = verify(base_record, original, keyring1, consumed=consumed)
        rows.append({"scenario": "nonce_replay_first_use", "case_id": case["case_id"], "accepted": first_ok, "reason": first_reason})
        rows.append({"scenario": "nonce_replay_second_use", "case_id": case["case_id"], "accepted": second_ok, "reason": second_reason})

    scenarios = sorted({r["scenario"] for r in rows})
    summary = []
    for scenario in scenarios:
        subset = [r for r in rows if r["scenario"] == scenario]
        accepted = sum(bool(r["accepted"]) for r in subset)
        reasons = {}
        for row in subset:
            reasons[row["reason"]] = reasons.get(row["reason"], 0) + 1
        summary.append({
            "scenario": scenario,
            "cases": len(subset),
            "accepted": accepted,
            "rejected": len(subset) - accepted,
            "acceptance_rate": round(accepted / len(subset), 8),
            "rejection_reasons": json.dumps(reasons, sort_keys=True),
        })

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "document_root_attestation_cases.csv", rows)
    write_csv(OUT / "document_root_attestation_summary.csv", summary)
    files = sorted(OUT.glob("*.csv"))
    manifest = {
        "protocol": "document-root-attestation-threat-experiment-v1",
        "benchmark_version": "0.4",
        "high_risk_cases": len(cases),
        "scenarios": scenarios,
        "test_key_derivation": "SHA-256 deterministic test-only keys; not production keys",
        "tenant_binding": True,
        "case_binding": True,
        "raw_document_instances_bound": True,
        "normalized_document_map_bound": True,
        "key_rotation_and_revocation_tested": True,
        "replay_detection_tested": True,
        "trusted_root_compromise_tested": True,
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "generated_files": [p.name for p in files],
        "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "note": "Synthetic cryptographic protocol test. Replay-state persistence, KMS/HSM operation, signer identity enrollment and operational key custody are not implemented.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
