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
NAMES = tuple(f"witness-{i}" for i in range(1, 6))


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


def make_credentials(root_private, count=3, shared_admin=False):
    credentials, private_keys = [], []
    for index, name in enumerate(NAMES[:count], 1):
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
    shared_admin = scenario == "shared_administrative_domain"
    private_keys_3, credentials_3 = make_credentials(root_private, count=3, shared_admin=shared_admin)
    private_keys_5, credentials_5 = make_credentials(root_private, count=5, shared_admin=shared_admin)

    compromised_3 = set()
    compromised_5 = set()
    if scenario == "one_witness_compromised":
        compromised_3, compromised_5 = {0}, {0}
    elif scenario in ("two_witnesses_compromised", "two_witnesses_compromised_and_one_invalid_credential"):
        compromised_3, compromised_5 = {0, 1}, {0, 1}
    elif scenario == "all_witnesses_compromised":
        compromised_3, compromised_5 = {0, 1, 2}, {0, 1, 2, 3, 4}
    elif scenario == "registry_root_compromise":
        compromised_3, compromised_5 = {0, 1}, {0, 1}

    def tamper_identity_credential(credentials, index):
        credentials[index] = dict(credentials[index])
        credentials[index]["body"] = dict(credentials[index]["body"], source_id="attacker-source")

    if scenario == "forged_source_identity":
        tamper_identity_credential(credentials_3, 0)
        tamper_identity_credential(credentials_5, 0)
    elif scenario == "two_witnesses_compromised_and_one_invalid_credential":
        tamper_identity_credential(credentials_3, 2)
        tamper_identity_credential(credentials_5, 2)

    if scenario == "registry_root_compromise":
        # The existing registry signing private key is compromised. The
        # verifier keeps the original pinned public key; the attacker uses the
        # stolen private key to enroll two attacker-controlled witness keys.
        for private_keys, credentials in (
            (private_keys_3, credentials_3), (private_keys_5, credentials_5)
        ):
            for i in (0, 1):
                credentials[i] = issue_identity_credential(
                    issuer_id="synthetic-registry", witness_id=f"attacker-witness-{i+1}",
                    key_id=f"attacker-key-{i+1}", public_key=private_keys[i].public_key(),
                    source_id=f"attacker-source-{i+1}",
                    acquisition_domain=f"attacker-acquisition-{i+1}",
                    administrative_domain=f"attacker-admin-{i+1}", tenant_id=TENANT,
                    serial=f"attacker-credential-{i+1}", issued_at=NOW - 100,
                    expires_at=NOW + 10000, issuer_private_key=root_private,
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

        def make_records(private_keys, credentials, compromised):
            records = []
            for witness_index, (private, credential) in enumerate(zip(private_keys, credentials)):
                if witness_index in compromised:
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
            return records

        records_3 = make_records(private_keys_3, credentials_3, compromised_3)
        records_5 = make_records(private_keys_5, credentials_5, compromised_5)
        quorum_2of3, reason_2of3, support_2of3 = verify_witness_quorum(
            records_3, trusted_issuer_key=root_public, tenant_id=TENANT,
            case_id=case["case_id"], parent_digest=parent,
            expected_weight=expected_weight, expected_item_type=expected_type,
            now=NOW, threshold=2, total_required=3,
        )
        quorum_3of3, reason_3of3, support_3of3 = verify_witness_quorum(
            records_3, trusted_issuer_key=root_public, tenant_id=TENANT,
            case_id=case["case_id"], parent_digest=parent,
            expected_weight=expected_weight, expected_item_type=expected_type,
            now=NOW, threshold=3, total_required=3,
        )
        quorum_3of5, reason_3of5, support_3of5 = verify_witness_quorum(
            records_5, trusted_issuer_key=root_public, tenant_id=TENANT,
            case_id=case["case_id"], parent_digest=parent,
            expected_weight=expected_weight, expected_item_type=expected_type,
            now=NOW, threshold=3, total_required=5,
        )
        # Evaluate the legacy evidence guards once, but only after at least
        # one complete witness configuration has authenticated the external
        # measurement. Each threshold policy still acts only on its own valid
        # quorum result.
        decision_case = copy.deepcopy(case)
        any_quorum = quorum_2of3 or quorum_3of3 or quorum_3of5
        if any_quorum:
            decision_case["observable"]["external"]["measured_weight"] = expected_weight
            legacy = evidence_gate_v1(decision_case)
            recovery_candidate = is_recoverable_verifier_false_reject(
                visible_features(decision_case), legacy
            )
        else:
            legacy = "ESCALATE"
            recovery_candidate = False
        recovery_2of3 = quorum_2of3 and recovery_candidate
        recovery_3of3 = quorum_3of3 and recovery_candidate
        recovery_3of5 = quorum_3of5 and recovery_candidate
        action_2of3 = "ACT" if quorum_2of3 and (legacy == "ACT" or recovery_2of3) else "ESCALATE"
        action_3of3 = "ACT" if quorum_3of3 and (legacy == "ACT" or recovery_3of3) else "ESCALATE"
        action_3of5 = "ACT" if quorum_3of5 and (legacy == "ACT" or recovery_3of5) else "ESCALATE"
        unsafe_2of3 = action_2of3 == "ACT" and not case["safe_to_act"]
        unsafe_3of3 = action_3of3 == "ACT" and not case["safe_to_act"]
        unsafe_3of5 = action_3of5 == "ACT" and not case["safe_to_act"]
        rows.append({
            "scenario": scenario, "case_id": case["case_id"], "family": case["family"],
            "safe_to_act_ground_truth": bool(case["safe_to_act"]),
            "legacy_gate_action": legacy,
            "quorum_2of3_valid": quorum_2of3, "quorum_2of3_reason": reason_2of3,
            "matching_witnesses_2of3": support_2of3,
            "recovery_applied_2of3": recovery_2of3, "action_2of3": action_2of3,
            "unsafe_act_2of3": bool(unsafe_2of3),
            "safe_act_2of3": bool(action_2of3 == "ACT" and case["safe_to_act"]),
            "quorum_3of3_valid": quorum_3of3, "quorum_3of3_reason": reason_3of3,
            "matching_witnesses_3of3": support_3of3,
            "recovery_applied_3of3": recovery_3of3, "action_3of3": action_3of3,
            "unsafe_act_3of3": bool(unsafe_3of3),
            "safe_act_3of3": bool(action_3of3 == "ACT" and case["safe_to_act"]),
            "quorum_3of5_valid": quorum_3of5, "quorum_3of5_reason": reason_3of5,
            "matching_witnesses_3of5": support_3of5,
            "recovery_applied_3of5": recovery_3of5, "action_3of5": action_3of5,
            "unsafe_act_3of5": bool(unsafe_3of5),
            "safe_act_3of5": bool(action_3of5 == "ACT" and case["safe_to_act"]),
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
        "registry_root_compromise", "two_witnesses_compromised_and_one_invalid_credential",
    )
    rows = []
    for scenario in scenarios:
        rows.extend(scenario_rows(cases, scenario))
    summary = []
    for scenario in scenarios:
        subset = [row for row in rows if row["scenario"] == scenario]
        n = len(subset)
        safe_n = sum(row["safe_to_act_ground_truth"] for row in subset)
        item = {"scenario": scenario, "cases": n}
        for policy in ("2of3", "3of3", "3of5"):
            acts = sum(row[f"action_{policy}"] == "ACT" for row in subset)
            unsafe = sum(row[f"unsafe_act_{policy}"] for row in subset)
            recoveries = sum(row[f"recovery_applied_{policy}"] for row in subset)
            safe_acts = sum(row[f"safe_act_{policy}"] for row in subset)
            item[f"ACT_{policy}"] = acts
            item[f"unsafe_ACT_{policy}"] = unsafe
            item[f"verifier_false_reject_recoveries_{policy}"] = recoveries
            item[f"unsafe_ACT_rate_all_cases_{policy}"] = round(unsafe / n, 6)
            item[f"unsafe_ACT_rate_conditional_on_ACT_{policy}"] = round(unsafe / acts, 6) if acts else None
            item[f"safe_ACT_coverage_{policy}"] = round(safe_acts / safe_n, 6) if safe_n else None
            item[f"false_block_rate_{policy}"] = round((safe_n - safe_acts) / safe_n, 6) if safe_n else None
            item[f"ESCALATE_{policy}"] = n - acts
        summary.append(item)

    # Deterministic regression expectations: (ACT, unsafe ACT) for 2-of-3,
    # 3-of-3 and 3-of-5 respectively.
    expected = {
        "honest_baseline": ((100, 0), (100, 0), (100, 0)),
        "one_witness_compromised": ((100, 0), (100, 0), (100, 0)),
        "two_witnesses_compromised": ((150, 50), (100, 0), (100, 0)),
        "all_witnesses_compromised": ((150, 50), (150, 50), (150, 50)),
        "forged_source_identity": ((100, 0), (0, 0), (100, 0)),
        "source_forgery_before_capture": ((0, 0), (0, 0), (0, 0)),
        "shared_administrative_domain": ((0, 0), (0, 0), (0, 0)),
        "registry_root_compromise": ((150, 50), (100, 0), (100, 0)),
        "two_witnesses_compromised_and_one_invalid_credential": ((150, 50), (0, 0), (100, 0)),
    }
    by_scenario = {item["scenario"]: item for item in summary}
    for scenario, policies in expected.items():
        actual = by_scenario[scenario]
        for policy, target in zip(("2of3", "3of3", "3of5"), policies):
            observed = (actual[f"ACT_{policy}"], actual[f"unsafe_ACT_{policy}"])
            if observed != target:
                raise AssertionError(
                    f"{scenario} {policy} acceptance profile changed: observed={observed}, expected={target}"
                )
    for scenario in ("honest_baseline", "one_witness_compromised", "forged_source_identity",
                     "two_witnesses_compromised", "two_witnesses_compromised_and_one_invalid_credential"):
        if by_scenario[scenario]["safe_ACT_coverage_3of5"] != 1.0:
            raise AssertionError(f"3-of-5 should retain all safe cases in {scenario}")
    if by_scenario["all_witnesses_compromised"]["unsafe_ACT_3of5"] == 0:
        raise AssertionError("3-of-5 must not be represented as safe under full-roster compromise")

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "evidence_trust_v3_cases.csv", rows)
    write_csv(OUT / "evidence_trust_v3_summary.csv", summary)
    manifest = {
        "protocol": "ega-evidence-trust-architecture-v3",
        "status": "synthetic threat experiment; not production validation",
        "benchmark_version": "0.4", "high_risk_cases_per_scenario": len(cases),
        "scenario_count": len(scenarios), "case_scenario_rows": len(rows),
        "witness_configurations": {
            "2-of-3": "three enrolled witnesses; tolerates one invalid credential but not two colluding witnesses",
            "3-of-3": "three enrolled witnesses; blocks two-witness collusion but loses availability with one invalid credential",
            "3-of-5": "five enrolled witnesses; tested against two colluding witnesses and one invalid credential",
        },
        "threshold_sensitivity": "2-of-3 and 3-of-3 use the same three-witness roster; 3-of-5 uses a separate five-witness roster on the same benchmark cases",
        "identity_binding": "registry-root-signed credential binds public key to source and domain claims",
        "scenarios": list(scenarios),
        "limitations": [
            "All keys, identities, measurements and source records are synthetic.",
            "Registry signature authenticates the issuer's credential, not real-world source truth.",
            "Distinct domain labels do not prove operational independence.",
            "No production PKI, KMS/HSM, hardware identity, durable revocation or trusted time.",
            "Deterministic benchmark counts are not real-world probabilities.",
            "The five-witness configuration increases enrollment, governance and operational overhead.",
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
