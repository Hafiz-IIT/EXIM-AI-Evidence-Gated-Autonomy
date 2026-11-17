"""Run the synthetic four-authority evidence-trust v2 threat matrix.

The experiment isolates authority-key compromise from source-side forgery and
shared-dependency failure. All keys, sources and records are synthetic.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import itertools
import json
import os
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from scripts.generate_benchmark_v04 import canonical_hash
from src.core import evidence_gate_v1
from src.evidence_trust_v2 import (
    ROLES, create_attestation, verify_attestation, evidence_graph_digest,
)
from src.provenance import canonical_sha256

BENCH = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUT = ROOT / "results" / "evidence_trust_v2"
NOW = 1_800_000_000
TENANT = "tenant-synthetic"
LIFETIME = 3600


def test_key(role: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256(("EGA-EVIDENCE-TRUST-V2-TEST-ONLY|" + role).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def load_cases():
    with BENCH.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()
                and json.loads(line)["action"]["risk_level"] == "HIGH"]


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        raise ValueError(f"Refusing to write empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def forged_fields(case):
    obs = case["observable"]
    source = next((d for d in obs["documents"].values() if d is not None), None)
    source = source or obs["machine"]["extraction"]
    return {
        "quantity": int(source["quantity"]) + 7,
        "gross_weight": round(float(source["gross_weight"]) + 11.25, 2),
        "hs": "9999",
    }


def update_provenance(obs):
    obs["provenance"]["integrity_status"] = "valid"
    obs["provenance"]["document_set_sha256"] = canonical_sha256(obs["document_instances"])


def rewrite_source_documents(case, fields):
    obs = case["observable"]
    for kind, document in obs["documents"].items():
        if document is not None:
            document.update(fields)
    for instance in obs["document_instances"]:
        instance["fields"].update(fields)
    update_provenance(obs)


def honest_interpretation_after_capture(case):
    """Model an honest parser reading the invoice as captured."""
    obs = case["observable"]
    invoice = obs["documents"].get("invoice")
    if invoice is not None:
        for field in ("quantity", "gross_weight", "hs"):
            obs["machine"]["extraction"][field] = invoice[field]
        obs["machine"]["classification"]["hs"] = invoice["hs"]


def apply_compromise_capabilities(case, compromised):
    """Apply only the capabilities assigned to the named compromised roles."""
    result = copy.deepcopy(case)
    obs = result["observable"]
    forged = forged_fields(result)

    if "capture" in compromised:
        rewrite_source_documents(result, forged)
    if "interpretation" in compromised:
        obs["machine"]["extraction"].update(forged)
        obs["machine"]["classification"]["hs"] = forged["hs"]
    elif "capture" in compromised:
        honest_interpretation_after_capture(result)

    if "witness" in compromised:
        # The witness authority operates the independent measurement channel
        # in this synthetic threat model; compromise permits a false reading.
        obs["external"]["measured_weight"] = obs["machine"]["extraction"]["gross_weight"]
    return result


def issue_role_records(case, compromised, nonce_prefix, witness_dependency=False,
                       key_admin_compromise=False):
    obs = case["observable"]
    keys = {
        role: test_key(
            "key-admin-enrolled-" + role
            if key_admin_compromise and role != "authorization" else role
        )
        for role in ROLES
    }
    # Under key-admin compromise, the trust registry is poisoned to accept
    # attacker-enrolled upstream keys; AA's own key remains uncompromised.
    public_keys = {role + "-key": key.public_key() for role, key in keys.items()}
    scope_parent = canonical_sha256({"tenant": TENANT, "case": case["case_id"]})

    raw_digest = canonical_sha256(obs["document_instances"])
    capture_payload = {
        "raw_document_digest": raw_digest,
        "source_id": "synthetic-document-source",
        "acquisition_channel": "controlled-test-fixture",
        "acquisition_domain": "document-operations",
        "administrative_domain": "capture-admin",
        "capture_session": "capture-" + case["case_id"],
    }
    capture = create_attestation(
        role="capture", key_id="capture-key", tenant_id=TENANT,
        case_id=case["case_id"], parent_digest=scope_parent,
        payload=capture_payload, private_key=keys["capture"],
        issued_at=NOW - 10, expires_at=NOW + LIFETIME,
        nonce=nonce_prefix + "-capture",
    )
    capture_digest = canonical_sha256(capture["envelope"])

    extracted = {
        key: obs["machine"]["extraction"][key]
        for key in ("quantity", "gross_weight", "hs")
    }
    interpretation_payload = {
        "fields": extracted,
        "parser": "synthetic-parser",
        "parser_version": "2.0.0",
        "input_raw_digest": raw_digest,
    }
    interpretation = create_attestation(
        role="interpretation", key_id="interpretation-key", tenant_id=TENANT,
        case_id=case["case_id"], parent_digest=capture_digest,
        payload=interpretation_payload, private_key=keys["interpretation"],
        issued_at=NOW - 9, expires_at=NOW + LIFETIME,
        nonce=nonce_prefix + "-interpretation",
    )

    if witness_dependency:
        source_doc = obs["documents"].get("invoice")
        source_doc = source_doc or next(
            (d for d in obs["documents"].values() if d is not None),
            obs["machine"]["extraction"],
        )
        witness_fields = {
            "gross_weight": source_doc["gross_weight"],
            "item_type": obs["external"]["inspection_item_type"],
        }
        witness_source_id = "synthetic-document-source"
        witness_domain = "document-operations"
        witness_admin_domain = "capture-admin"
    elif "witness" in compromised:
        witness_fields = {
            "gross_weight": obs["external"]["measured_weight"],
            "item_type": obs["external"]["inspection_item_type"],
        }
        witness_source_id = "independent-scale-and-inspection"
        witness_domain = "independent-operations"
        witness_admin_domain = "witness-admin"
    else:
        witness_fields = {
            "gross_weight": case["ground_truth"]["gross_weight"],
            "item_type": case["ground_truth"]["item_type"],
        }
        witness_source_id = "independent-scale-and-inspection"
        witness_domain = "independent-operations"
        witness_admin_domain = "witness-admin"
    witness_source = {
        "source_id": witness_source_id,
        "acquisition_domain": witness_domain,
        "administrative_domain": witness_admin_domain,
        "fields": witness_fields,
    }
    witness_source_digest = canonical_sha256(witness_source)
    witness = create_attestation(
        role="witness", key_id="witness-key", tenant_id=TENANT,
        case_id=case["case_id"], parent_digest=witness_source_digest,
        payload=witness_source, private_key=keys["witness"],
        issued_at=NOW - 8, expires_at=NOW + LIFETIME,
        nonce=nonce_prefix + "-witness",
    )
    return keys, public_keys, scope_parent, raw_digest, capture, interpretation, witness, witness_source_digest


def authorize(case, compromised, nonce_prefix, witness_dependency=False, key_admin_compromise=False):
    (keys, public_keys, scope_parent, raw_digest, capture, interpretation,
     witness, witness_source_digest) = issue_role_records(
        case, compromised, nonce_prefix, witness_dependency, key_admin_compromise
    )
    obs = case["observable"]
    checks = {}
    checks["capture"] = verify_attestation(
        capture, expected_role="capture", trusted_keys=public_keys,
        tenant_id=TENANT, case_id=case["case_id"], parent_digest=scope_parent,
        now=NOW,
    )
    checks["capture_content"] = (
        capture["envelope"]["payload"]["raw_document_digest"] == canonical_sha256(obs["document_instances"]),
        "raw_digest_match",
    )
    capture_digest = canonical_sha256(capture["envelope"])
    checks["interpretation"] = verify_attestation(
        interpretation, expected_role="interpretation", trusted_keys=public_keys,
        tenant_id=TENANT, case_id=case["case_id"], parent_digest=capture_digest,
        now=NOW,
    )
    checks["interpretation_input"] = (
        interpretation["envelope"]["payload"]["input_raw_digest"] == raw_digest,
        "input_digest_match",
    )
    checks["witness"] = verify_attestation(
        witness, expected_role="witness", trusted_keys=public_keys,
        tenant_id=TENANT, case_id=case["case_id"],
        parent_digest=witness_source_digest, now=NOW,
    )
    witness_source = witness["envelope"]["payload"]
    capture_source = capture["envelope"]["payload"]
    checks["witness_independence"] = (
        witness_source["source_id"] != capture_source["source_id"]
        and witness_source["acquisition_domain"] != capture_source["acquisition_domain"]
        and witness_source["administrative_domain"] != capture_source["administrative_domain"],
        "distinct_source_acquisition_and_admin_domains",
    )

    ia_fields = interpretation["envelope"]["payload"]["fields"]
    witness_fields = witness["envelope"]["payload"]["fields"]
    checks["independent_agreement"] = (
        abs(float(ia_fields["gross_weight"]) - float(witness_fields["gross_weight"])) < 1e-9
        and witness_fields["item_type"] == case["ground_truth"]["item_type"],
        "witness_matches_interpretation",
    )
    gate_action = evidence_gate_v1(case)
    checks["legacy_policy"] = (gate_action == "ACT", "legacy_evidence_gate_act")
    graph_valid = all(item[0] for item in checks.values())

    # AA compromise is modeled as arbitrary action authorization, not as
    # compromise of the other three signing keys.
    decision = "ACT" if "authorization" in compromised else ("ACT" if graph_valid else "ESCALATE")
    graph_digest = evidence_graph_digest(capture, interpretation, witness)
    aa_record = create_attestation(
        role="authorization", key_id="authorization-key", tenant_id=TENANT,
        case_id=case["case_id"], parent_digest=graph_digest,
        payload={"decision": decision, "policy": "ega-v2-synthetic-policy",
                 "graph_digest": graph_digest, "consequence": "high"},
        private_key=keys["authorization"], issued_at=NOW - 1,
        expires_at=NOW + 300, nonce=nonce_prefix + "-authorization",
    )
    aa_ok, aa_reason = verify_attestation(
        aa_record, expected_role="authorization", trusted_keys=public_keys,
        tenant_id=TENANT, case_id=case["case_id"], parent_digest=graph_digest,
        now=NOW,
    )
    action = aa_record["envelope"]["payload"]["decision"] if aa_ok else "ESCALATE"
    return {
        "action": action,
        "gate_action": gate_action,
        "graph_valid": graph_valid,
        "failed_checks": ";".join(name + ":" + value[1] for name, value in checks.items() if not value[0]),
        "aa_verified": aa_ok,
        "aa_reason": aa_reason,
    }


def make_source_forgery(case, shared_witness=False):
    result = copy.deepcopy(case)
    forged = forged_fields(result)
    rewrite_source_documents(result, forged)
    honest_interpretation_after_capture(result)
    if shared_witness:
        # Deliberately violates independence: witness is copied from the same
        # forged document source and its measurement is aligned to that source.
        result["observable"]["external"]["measured_weight"] = forged["gross_weight"]
    return result


def run_scenario(cases, name, compromised=(), control=None):
    rows = []
    for index, original in enumerate(cases):
        if control == "source_forgery":
            case = make_source_forgery(original, shared_witness=False)
            active_compromises = ()
        elif control == "shared_dependency":
            case = make_source_forgery(original, shared_witness=True)
            active_compromises = ()
        elif control == "key_admin_compromise":
            active_compromises = ("capture", "interpretation", "witness")
            case = apply_compromise_capabilities(original, active_compromises)
        else:
            case = apply_compromise_capabilities(original, compromised)
            active_compromises = compromised
        outcome = authorize(
            case, active_compromises, f"{name}-{index:05d}",
            witness_dependency=(control == "shared_dependency"),
            key_admin_compromise=(control == "key_admin_compromise"),
        )
        unsafe = outcome["action"] == "ACT" and not original["safe_to_act"]
        rows.append({
            "scenario": name,
            "compromised_authorities": (
                "key_admin_registry" if control == "key_admin_compromise"
                else ("+".join(compromised) if compromised else "none")
            ),
            "forged_role_claims": "+".join(active_compromises) if active_compromises else "none",
            "trust_registry_compromised": bool(control == "key_admin_compromise"),
            "case_id": original["case_id"],
            "family": original["family"],
            "safe_to_act_ground_truth": bool(original["safe_to_act"]),
            "action": outcome["action"],
            "legacy_gate_action": outcome["gate_action"],
            "graph_valid": outcome["graph_valid"],
            "aa_verified": outcome["aa_verified"],
            "failed_checks": outcome["failed_checks"],
            "unsafe_act": bool(unsafe),
            "safe_act": bool(outcome["action"] == "ACT" and original["safe_to_act"]),
        })
    return rows


def summarize(rows):
    summaries = []
    for scenario in sorted({row["scenario"] for row in rows}):
        subset = [row for row in rows if row["scenario"] == scenario]
        n = len(subset)
        acts = sum(row["action"] == "ACT" for row in subset)
        unsafe = sum(row["unsafe_act"] for row in subset)
        safe_n = sum(row["safe_to_act_ground_truth"] for row in subset)
        safe_act = sum(row["safe_act"] for row in subset)
        summaries.append({
            "scenario": scenario, "cases": n, "ACT": acts,
            "unsafe_ACT": unsafe,
            "unsafe_ACT_rate_all_cases": round(unsafe / n, 6) if n else 0,
            "unsafe_ACT_rate_conditional_on_ACT": round(unsafe / acts, 6) if acts else 0,
            "safe_cases": safe_n, "safe_ACT": safe_act,
            "safe_ACT_coverage": round(safe_act / safe_n, 6) if safe_n else 0,
            "false_block_rate": round((safe_n - safe_act) / safe_n, 6) if safe_n else 0,
            "ESCALATE": sum(row["action"] == "ESCALATE" for row in subset),
        })
    return summaries


def main():
    cases = load_cases()
    if len(cases) != 700:
        raise ValueError(f"Expected 700 HIGH-risk v0.4 cases, found {len(cases)}")
    rows = []
    matrix = []
    for size in range(1, len(ROLES) + 1):
        matrix.extend(itertools.combinations(ROLES, size))
    for compromised in matrix:
        name = "compromise_" + "_".join(compromised)
        rows.extend(run_scenario(cases, name, compromised=compromised))
    rows.extend(run_scenario(cases, "honest_baseline"))
    rows.extend(run_scenario(cases, "source_forgery_before_capture", control="source_forgery"))
    rows.extend(run_scenario(cases, "shared_dependency_witness", control="shared_dependency"))
    rows.extend(run_scenario(cases, "key_admin_compromise_trust_store_poisoning",
                             control="key_admin_compromise"))

    OUT.mkdir(parents=True, exist_ok=True)
    case_path = OUT / "evidence_trust_v2_cases.csv"
    summary_path = OUT / "evidence_trust_v2_summary.csv"
    write_csv(case_path, rows)
    summaries = summarize(rows)
    write_csv(summary_path, summaries)
    manifest = {
        "protocol": "ega-evidence-trust-architecture-v2",
        "status": "synthetic threat experiment; not production validation",
        "benchmark_version": "0.4",
        "high_risk_cases_per_scenario": len(cases),
        "authority_roles": list(ROLES),
        "compromise_combinations": [list(x) for x in matrix],
        "additional_controls": [
            "honest_baseline", "source_forgery_before_capture",
            "shared_dependency_witness", "key_admin_compromise_trust_store_poisoning"
        ],
        "scenario_count": len(summaries),
        "case_scenario_rows": len(rows),
        "test_keys": "deterministic Ed25519 keys derived from fixed role labels; test-only",
        "independent_witness_model": (
            "synthetic independent scale/inspection record sourced from ground_truth; "
            "witness-role compromise can falsify its signed fields"
        ),
        "authorization_model": (
            "honest AA enforces signatures, parent links, witness agreement and evidence_gate_v1; "
            "compromised AA can issue ACT directly"
        ),
        "source_forgery_model": (
            "forged source documents are present before honest capture; honest witness remains "
            "ground-truth-derived unless the shared-dependency control is selected"
        ),
        "limitations": [
            "Synthetic benchmark and authority model; no real external source or signer was used.",
            "The experiment does not implement KMS/HSM, authenticated enrollment, durable replay state, "
            "distributed transactions, operational revocation or secure capture.",
            "A compromised authority key is modeled as control over that role's signed claims only; "
            "the named role capabilities are explicit in the runner.",
            "Monte Carlo uncertainty is not estimated; this is a deterministic benchmark stress test.",
        ],
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "generated_files": [case_path.name, summary_path.name],
        "outputs_sha256": {
            case_path.name: hashlib.sha256(case_path.read_bytes()).hexdigest(),
            summary_path.name: hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
