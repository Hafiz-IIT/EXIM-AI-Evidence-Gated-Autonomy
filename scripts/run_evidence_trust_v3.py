"""Run a separate synthetic v3 witness-quorum and source-identity experiment."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from src.core import evidence_gate_v1, visible_features
from src.evidence_trust_v3 import (
    issue_identity_credential, issue_witness_assertion, verify_witness_quorum,
    is_recoverable_verifier_false_reject,
)
from src.provenance import canonical_sha256

BENCH = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUT = ROOT / "results" / "evidence_trust_v3"
NOW = 1_800_000_000
TENANT = "tenant-synthetic"
NAMES = ("witness-1", "witness-2", "witness-3")


def key(name):
    seed = hashlib.sha256(("EGA-V3-TEST-ONLY|" + name).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def load_cases():
    with BENCH.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    return [row for row in rows if row["action"]["risk_level"] == "HIGH"]


def write_csv(path, rows):
    if not rows:
        raise ValueError("refusing to write empty results")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_credentials(root_private, shared_admin=False):
    credentials, private_keys = [], []
    for index, name in enumerate(NAMES, 1):
        private = key(name)
        private_keys.append(private)
        credentials.append(issue_identity_credential(
            issuer_id="ega-synthetic-registry-root", witness_id=name,
            key_id=f"{name}-key", public_key=private.public_key(),
            source_id=f"independent-source-{index}",
            acquisition_domain=f"acquisition-domain-{index}",
            administrative_domain=("shared-admin" if shared_admin
                                   else f"administrative-domain-{index}"),
            tenant_id=TENANT, serial=f"credential-{index}", issued_at=NOW - 100,
            expires_at=NOW + 10000, issuer_private_key=root_private,
        ))
    return private_keys, credentials


def make_source_forgery(case):
    """Forge source documents before capture, then model an honest parser."""
    forged = copy.deepcopy(case)
    obs = forged["observable"]
    source = next((doc for doc in obs["documents"].values() if doc is not None),
                  obs["machine"]["extraction"])
    fields = {
        "quantity": int(source["quantity"]) + 7,
        "gross_weight": round(float(source["gross_weight"]) + 11.25, 2),
        "hs": "9999",
    }
    for document in obs["documents"].values():
        if document is not None:
            document.update(fields)
    for instance in obs["document_instances"]:
        instance["fields"].update(fields)
    obs["provenance"]["integrity_status"] = "valid"
    obs["provenance"]["document_set_sha256"] = canonical_sha256(obs["document_instances"])
    invoice = obs["documents"].get("invoice")
    if invoice is not None:
        for field in ("quantity", "gross_weight", "hs"):
            obs["machine"]["extraction"][field] = invoice[field]
        obs["machine"]["classification"]["hs"] = invoice["hs"]
    # The document set is now forged relative to the unchanged physical
    # ground truth, so the transformed case is no longer safe to authorize.
    forged["safe_to_act"] = False
    return forged


def scenario_rows(cases, scenario):
    root_private = key("registry-root")
    root_public = root_private.public_key()
    compromised = {
        "one_witness_compromised": {0},
        "two_witnesses_compromised": {0, 1},
        "all_witnesses_compromised": {0, 1, 2},
    }.get(scenario, set())
    private_keys, credentials = make_credentials(
        root_private, shared_admin=(scenario == "shared_administrative_domain"))
    if scenario == "forged_source_identity":
        credentials[0] = dict(credentials[0])
        credentials[0]["body"] = dict(credentials[0]["body"], source_id="attacker-source")
    if scenario == "registry_root_compromise":
        attacker_root = key("attacker-registry-root")
        root_public = attacker_root.public_key()
        for i in (0, 1):
            credentials[i] = issue_identity_credential(
                issuer_id="attacker-registry-root", witness_id=f"attacker-witness-{i+1}",
                key_id=f"attacker-key-{i+1}", public_key=private_keys[i].public_key(),
                source_id=f"attacker-source-{i+1}",
                acquisition_domain=f"attacker-acquisition-{i+1}",
                administrative_domain=f"attacker-admin-{i+1}", tenant_id=TENANT,
                serial=f"attacker-credential-{i+1}", issued_at=NOW - 100,
                expires_at=NOW + 10000, issuer_private_key=attacker_root,
            )
    rows = []
    for index, original_case in enumerate(cases):
        case = (make_source_forgery(original_case)
                if scenario == "source_forgery_before_capture"
                else copy.deepcopy(original_case))
        observable = case["observable"]
        interpreted = observable["machine"]["extraction"]
        expected_weight = float(interpreted["gross_weight"])
        expected_type = observable["external"]["inspection_item_type"]
        parent = canonical_sha256({"tenant": TENANT, "case": case["case_id"],
                                   "documents": observable["document_instances"]})
        records = []
        for witness_index, (private, credential) in enumerate(zip(private_keys, credentials)):
            if witness_index in compromised or (scenario == "registry_root_compromise" and witness_index in (0, 1)):
                weight = float(interpreted["gross_weight"])
                item_type = expected_type
            else:
                weight = float(case["ground_truth"]["gross_weight"])
                item_type = case["ground_truth"]["item_type"]
            record = issue_witness_assertion(
                credential=credential, witness_private_key=private, tenant_id=TENANT,
                case_id=case["case_id"], parent_digest=parent,
                gross_weight=weight, item_type=item_type,
                nonce=f"{scenario}-{index}-{witness_index}",
                issued_at=NOW - 10, expires_at=NOW + 300,
            )
            records.append((record, credential))
        quorum, reason, support = verify_witness_quorum(
            records, trusted_issuer_key=root_public, tenant_id=TENANT,
            case_id=case["case_id"], parent_digest=parent,
            expected_weight=expected_weight, expected_item_type=expected_type,
            now=NOW, threshold=2, total_required=3,
        )
        quorum_3of3, reason_3of3, support_3of3 = verify_witness_quorum(
            records, trusted_issuer_key=root_public, tenant_id=TENANT,
            case_id=case["case_id"], parent_digest=parent,
            expected_weight=expected_weight, expected_item_type=expected_type,
            now=NOW, threshold=3, total_required=3,
        )
        # The quorum is the authority for the independent measurement channel.
        # Feed its accepted measurement into the legacy policy only after a
        # valid quorum; otherwise the controller must abstain. This avoids
        # accidentally letting the untouched benchmark measurement bypass
        # the witness system being tested.
        decision_case = copy.deepcopy(case)
        recovery_applied = False
        if quorum:
            decision_case["observable"]["external"]["measured_weight"] = expected_weight
            legacy = evidence_gate_v1(decision_case)
            recovery_applied = is_recoverable_verifier_false_reject(
                visible_features(decision_case), legacy
            )
        else:
            legacy = "ESCALATE"
        action = "ACT" if quorum and (legacy == "ACT" or recovery_applied) else "ESCALATE"
        recovery_applied_3of3 = (
            quorum_3of3 and is_recoverable_verifier_false_reject(
                visible_features(decision_case), legacy
            )
        )
        action_3of3 = (
            "ACT" if quorum_3of3 and (legacy == "ACT" or recovery_applied_3of3)
            else "ESCALATE"
        )
        unsafe = action == "ACT" and not case["safe_to_act"]
        unsafe_3of3 = action_3of3 == "ACT" and not case["safe_to_act"]
        rows.append({
            "scenario": scenario, "case_id": case["case_id"], "family": case["family"],
            "safe_to_act_ground_truth": bool(case["safe_to_act"]),
            "legacy_gate_action": legacy, "recovery_applied": recovery_applied,
            "quorum_valid": quorum,
            "quorum_reason": reason, "matching_witnesses": support,
            "action": action, "unsafe_act": bool(unsafe),
            "safe_act": bool(action == "ACT" and case["safe_to_act"]),
            "quorum_3of3_valid": quorum_3of3,
            "quorum_3of3_reason": reason_3of3,
            "matching_witnesses_3of3": support_3of3,
            "recovery_applied_3of3": recovery_applied_3of3,
            "action_3of3": action_3of3,
            "unsafe_act_3of3": bool(unsafe_3of3),
            "safe_act_3of3": bool(action_3of3 == "ACT" and case["safe_to_act"]),
        })
    return rows


def main():
    cases = load_cases()
    if len(cases) != 700:
        raise ValueError(f"expected 700 HIGH-risk cases, found {len(cases)}")
    scenarios = (
        "honest_baseline", "one_witness_compromised", "two_witnesses_compromised",
        "all_witnesses_compromised", "forged_source_identity",
        "source_forgery_before_capture", "shared_administrative_domain",
        "registry_root_compromise",
    )
    rows = []
    for scenario in scenarios:
        rows.extend(scenario_rows(cases, scenario))
    summary = []
    for scenario in scenarios:
        subset = [row for row in rows if row["scenario"] == scenario]
        n = len(subset)
        acts = sum(row["action"] == "ACT" for row in subset)
        recoveries = sum(row["recovery_applied"] for row in subset)
        unsafe = sum(row["unsafe_act"] for row in subset)
        acts_3of3 = sum(row["action_3of3"] == "ACT" for row in subset)
        unsafe_3of3 = sum(row["unsafe_act_3of3"] for row in subset)
        recoveries_3of3 = sum(row["recovery_applied_3of3"] for row in subset)
        safe_n = sum(row["safe_to_act_ground_truth"] for row in subset)
        safe_acts = sum(row["safe_act"] for row in subset)
        safe_acts_3of3 = sum(row["safe_act_3of3"] for row in subset)
        summary.append({
            "scenario": scenario, "cases": n, "ACT": acts, "unsafe_ACT": unsafe,
            "verifier_false_reject_recoveries": recoveries,
            "unsafe_ACT_rate_all_cases": round(unsafe / n, 6),
            "unsafe_ACT_rate_conditional_on_ACT": round(unsafe / acts, 6) if acts else None,
            "safe_ACT_coverage": round(safe_acts / safe_n, 6) if safe_n else None,
            "false_block_rate": round((safe_n - safe_acts) / safe_n, 6) if safe_n else None,
            "ESCALATE": n - acts,
            "ACT_3of3": acts_3of3, "unsafe_ACT_3of3": unsafe_3of3,
            "verifier_false_reject_recoveries_3of3": recoveries_3of3,
            "unsafe_ACT_rate_all_cases_3of3": round(unsafe_3of3 / n, 6),
            "unsafe_ACT_rate_conditional_on_ACT_3of3": (
                round(unsafe_3of3 / acts_3of3, 6) if acts_3of3 else None
            ),
            "safe_ACT_coverage_3of3": round(safe_acts_3of3 / safe_n, 6) if safe_n else None,
            "false_block_rate_3of3": (
                round((safe_n - safe_acts_3of3) / safe_n, 6) if safe_n else 0
            ),
            "ESCALATE_3of3": n - acts_3of3,
        })
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "evidence_trust_v3_cases.csv", rows)
    write_csv(OUT / "evidence_trust_v3_summary.csv", summary)
    manifest = {
        "protocol": "ega-evidence-trust-architecture-v3",
        "status": "synthetic threat experiment; not production validation",
        "benchmark_version": "0.4", "high_risk_cases_per_scenario": len(cases),
        "scenario_count": len(scenarios), "case_scenario_rows": len(rows),
        "witness_quorum": "2-of-3 primary; 3-of-3 sensitivity",
        "threshold_sensitivity": "same cases and assertions evaluated at thresholds 2 and 3",
        "identity_binding": "registry-root-signed credential binds public key to source and domain claims",
        "scenarios": list(scenarios),
        "limitations": [
            "All keys, identities, measurements and source records are synthetic.",
            "Registry signature authenticates the issuer's credential, not real-world source truth.",
            "Distinct domain labels do not prove operational independence.",
            "No production PKI, KMS/HSM, hardware identity, durable revocation or trusted time.",
            "Deterministic benchmark counts are not real-world probabilities.",
        ],
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "outputs_sha256": {
            name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
            for name in ("evidence_trust_v3_cases.csv", "evidence_trust_v3_summary.csv")
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
