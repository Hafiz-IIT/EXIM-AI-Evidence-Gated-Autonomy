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
from src.provenance import canonical_sha256, create_document_root_attestation, verify_document_root_attestation
from src.core import evidence_gate_v1

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
        trusted_signers={key_id: "synthetic-document-root" for key_id in keyring},
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
    # Create a coherent, self-consistent forged document set and align the
    # extraction and measured-weight channels. This models a broader upstream
    # compromise plus possession of the document-root signing key.
    available = [d for d in obs["documents"].values() if d is not None]
    source = available[0] if available else {"quantity": 1, "gross_weight": 1.0, "hs": "0000"}
    forged = {
        "quantity": int(source["quantity"]) + 7,
        "gross_weight": round(float(source["gross_weight"]) + 11.25, 2),
        "hs": "9999",
    }
    for fields in obs["documents"].values():
        if fields is not None:
            fields.update(forged)
    for instance in obs["document_instances"]:
        instance["fields"].update(forged)
    obs["machine"]["extraction"].update(forged)
    obs["machine"]["classification"]["hs"] = forged["hs"]
    obs["external"]["measured_weight"] = forged["gross_weight"]
    obs["provenance"]["document_set_sha256"] = canonical_sha256(obs["document_instances"])
    obs["provenance"]["integrity_status"] = "valid"
    return rewritten


def gated_action(attestation_valid, case):
    # Fail closed when the document-root proof is invalid; otherwise continue
    # through the existing evidence gate. This is a study harness, not a
    # production integration.
    return evidence_gate_v1(case) if attestation_valid else "ESCALATE"


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
        rows.append({"scenario": "valid_baseline", "case_id": case["case_id"], "accepted": ok, "reason": reason, "policy_action": gated_action(ok, original), "unsafe_act": bool(gated_action(ok, original) == "ACT" and not original["safe_to_act"])})

        raw_tampered = copy.deepcopy(original)
        raw_tampered["observable"]["document_instances"][0]["fields"]["quantity"] += 1
        ok, reason = verify(base_record, raw_tampered, keyring1)
        rows.append({"scenario": "raw_instance_tamper", "case_id": case["case_id"], "accepted": ok, "reason": reason, "policy_action": gated_action(ok, raw_tampered), "unsafe_act": False})

        coherent = rewrite_documents(original)
        ok, reason = verify(base_record, coherent, keyring1)
        rows.append({"scenario": "coherent_rewrite_without_root_key", "case_id": case["case_id"], "accepted": ok, "reason": reason, "policy_action": gated_action(ok, coherent), "unsafe_act": False})

        # Threat-model upper bound: compromise of the trusted document-root private key.
        compromised_record = issue(coherent, key1, "doc-root-k1", "tenant-demo", nonce + "-compromised")
        ok, reason = verify(compromised_record, coherent, keyring1)
        rows.append({"scenario": "trusted_root_signer_compromise", "case_id": case["case_id"], "accepted": ok, "reason": reason, "policy_action": gated_action(ok, coherent), "unsafe_act": bool(gated_action(ok, coherent) == "ACT" and not original["safe_to_act"])})

        ok, reason = verify(base_record, original, keyring1, revoked={"doc-root-k1"})
        rows.append({"scenario": "revoked_old_key", "case_id": case["case_id"], "accepted": ok, "reason": reason, "policy_action": gated_action(ok, original), "unsafe_act": False})

        rotated_record = issue(original, key2, "doc-root-k2", "tenant-demo", nonce + "-rotated")
        ok, reason = verify(rotated_record, original, keyring2, revoked={"doc-root-k1"})
        rows.append({"scenario": "rotated_new_key", "case_id": case["case_id"], "accepted": ok, "reason": reason, "policy_action": gated_action(ok, original), "unsafe_act": bool(gated_action(ok, original) == "ACT" and not original["safe_to_act"])})

        ok, reason = verify(base_record, original, keyring1, tenant="tenant-other")
        rows.append({"scenario": "cross_tenant_replay", "case_id": case["case_id"], "accepted": ok, "reason": reason, "policy_action": gated_action(ok, original), "unsafe_act": False})

        consumed = set()
        first_ok, first_reason = verify(base_record, original, keyring1, consumed=consumed)
        second_ok, second_reason = verify(base_record, original, keyring1, consumed=consumed)
        rows.append({"scenario": "nonce_replay_first_use", "case_id": case["case_id"], "accepted": first_ok, "reason": first_reason, "policy_action": gated_action(first_ok, original), "unsafe_act": bool(gated_action(first_ok, original) == "ACT" and not original["safe_to_act"])})
        rows.append({"scenario": "nonce_replay_second_use", "case_id": case["case_id"], "accepted": second_ok, "reason": second_reason, "policy_action": gated_action(second_ok, original), "unsafe_act": False})

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
            "policy_ACTs": sum(r["policy_action"] == "ACT" for r in subset),
            "policy_unsafe_ACTs": sum(bool(r["unsafe_act"]) for r in subset),
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
