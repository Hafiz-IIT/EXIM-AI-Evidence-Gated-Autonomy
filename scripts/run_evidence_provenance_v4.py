"""Run claim-scoped provenance and action-binding experiments on benchmark v0.4."""
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
from src.evidence_provenance_v4 import (
    issue_source_credential, issue_claim_evidence, evaluate_claim,
    issue_action_binding, verify_action_binding,
)
from src.evidence_trust_v3 import is_recoverable_verifier_false_reject
from src.provenance import canonical_sha256

BENCH = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUT = ROOT / "results" / "evidence_provenance_v4"
NOW = 1_800_000_000
TENANT = "tenant-ega-synthetic"
POLICY = "ega-exim-claim-policy-v4.1"
CLAIMS = ("gross_weight", "quantity", "hs_code")
SCENARIOS = (
    "honest_baseline",
    "source_forgery_before_capture",
    "replay_attack",
    "stale_evidence",
    "cross_subject_substitution",
    "cross_claim_substitution",
    "parser_lineage_tampering",
    "invalid_calibration",
    "shared_admin_gateway",
    "credential_tampering",
    "action_substitution",
    "single_weighbridge_compromise",
    "single_tariff_registry_compromise",
    "tariff_compromise_with_independent_false_accept",
    "all_sources_compromised",
    "registry_root_compromise",
)


def key(name):
    seed = hashlib.sha256(("EGA-V4-TEST-ONLY|" + name).encode()).digest()
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


def make_sources(scenario):
    root = key("attacker-root" if scenario == "registry_root_compromise" else "registry-root")
    specs = {
        "document_parser": {
            "claims": ["gross_weight", "quantity", "hs_code"],
            "admin": "documents-admin", "gateway": "documents-gateway",
            "acquisition": "document-acquisition", "key_admin": "documents-key-admin",
        },
        "weighbridge": {
            "claims": ["gross_weight"],
            "admin": "scale-admin", "gateway": "scale-gateway",
            "acquisition": "scale-acquisition", "key_admin": "scale-key-admin",
        },
        "rfid_counter": {
            "claims": ["quantity"],
            "admin": "rfid-admin", "gateway": "rfid-gateway",
            "acquisition": "rfid-acquisition", "key_admin": "rfid-key-admin",
        },
        "tariff_registry": {
            "claims": ["hs_code"],
            "admin": "tariff-admin", "gateway": "tariff-gateway",
            "acquisition": "tariff-acquisition", "key_admin": "tariff-key-admin",
        },
    }
    keys = {name: key(name + ("-attacker" if scenario == "all_sources_compromised"
                              or (scenario == "single_weighbridge_compromise" and name == "weighbridge")
                              or (scenario in {"single_tariff_registry_compromise", "tariff_compromise_with_independent_false_accept"} and name == "tariff_registry")
                              or scenario == "registry_root_compromise" else ""))
            for name in specs}
    if scenario == "shared_admin_gateway":
        specs["weighbridge"]["admin"] = specs["document_parser"]["admin"]
        specs["weighbridge"]["gateway"] = specs["document_parser"]["gateway"]
    credentials = {}
    for name, spec in specs.items():
        credentials[name] = issue_source_credential(
            issuer_id="synthetic-evidence-registry", source_id="source-" + name,
            source_type=name, key_id="key-" + name, public_key=keys[name].public_key(),
            allowed_claims=spec["claims"], acquisition_domain=spec["acquisition"],
            administrative_domain=spec["admin"], gateway_id=spec["gateway"],
            key_admin_domain=spec["key_admin"], tenant_id=TENANT,
            serial="serial-" + name, issued_at=NOW - 100, expires_at=NOW + 10000,
            issuer_private_key=root,
        )
    if scenario == "credential_tampering":
        credentials["weighbridge"]["body"]["source_id"] = "attacker-replaced-source"
    authorizer = key("action-authorizer")
    return root, keys, credentials, authorizer


def make_record(source_type, claim, value, case, scenario, root, keys, credentials):
    credential = credentials[source_type]
    subject_id = case["case_id"]
    action_id = "submit:" + case["case_id"]
    document_digest = canonical_sha256(case["observable"]["document_instances"])
    action_payload_digest = canonical_sha256(case["action"])
    unit = {"gross_weight": "kg", "quantity": "items", "hs_code": "HS"}[claim]
    input_digest = document_digest
    observed_at, issued_at, expires_at = NOW - 10, NOW - 10, NOW + 100
    calibration_id, calibration_until = "", 0
    if source_type == "weighbridge":
        calibration_id, calibration_until = "scale-calibration-1", NOW + 1000
    if scenario == "stale_evidence" and source_type == "weighbridge":
        observed_at, issued_at, expires_at = NOW - 20, NOW - 10, NOW - 1
    if scenario == "cross_subject_substitution" and source_type == "rfid_counter":
        subject_id = "different-shipment"
    if scenario == "parser_lineage_tampering" and source_type == "document_parser":
        input_digest = "wrong-input-digest"
    if scenario == "invalid_calibration" and source_type == "weighbridge":
        calibration_until = NOW - 1
    if scenario == "credential_tampering" and source_type == "weighbridge":
        # Credential body was changed after the issuer signed it.
        pass
    if scenario == "action_substitution":
        # Evidence remains bound to the originally approved action. The consumer
        # will attempt to redeem it for a different action below.
        pass
    output_digest = canonical_sha256({
        "claim_type": claim, "value": value, "unit": unit,
    })
    return issue_claim_evidence(
        credential=credential, source_private_key=keys[source_type],
        claim_type=claim, value=value, unit=unit,
        subject_id=subject_id, action_id=action_id,
        action_payload_digest=action_payload_digest,
        document_digest=document_digest, input_digest=input_digest,
        output_digest=output_digest, transformation_id="transform-" + source_type,
        tool_version="synthetic-" + source_type + "-1.0",
        observed_at=observed_at, issued_at=issued_at, expires_at=expires_at,
        sequence_number=({"gross_weight": 1, "quantity": 2, "hs_code": 3}[claim] if source_type == "document_parser" else 1),
        nonce=f"{case['case_id']}:{scenario}:{source_type}:{claim}",
        calibration_id=calibration_id, calibration_valid_until=calibration_until,
    )


def run_one(case, scenario):
    root, keys, credentials, authorizer = make_sources(scenario)
    obs = case["observable"]
    parsed = obs["machine"]["extraction"]
    parsed_hs = obs["machine"]["classification"]["hs"]
    doc_digest = canonical_sha256(obs["document_instances"])
    action_payload_digest = canonical_sha256(case["action"])
    subject_id = case["case_id"]
    action_id = "submit:" + case["case_id"]
    case_for_gate = copy.deepcopy(case)
    if scenario == "tariff_compromise_with_independent_false_accept":
        # Model two independent but jointly false-accepting verifiers so the
        # existing dependency-diversity guard does not itself block the case.
        for index, verifier in enumerate(case_for_gate["observable"]["machine"]["verifiers"]):
            verifier["dependency_group"] = f"independent-false-accept-{index}"

    if scenario in {"single_weighbridge_compromise", "all_sources_compromised",
                    "registry_root_compromise"}:
        case_for_gate["observable"]["external"]["measured_weight"] = parsed["gross_weight"]

    weight_value = obs["external"]["measured_weight"]
    quantity_value = case["ground_truth"]["quantity"]
    hs_value = case["ground_truth"]["hs"]
    if scenario in {"single_weighbridge_compromise", "all_sources_compromised",
                    "registry_root_compromise"}:
        weight_value = parsed["gross_weight"]
    if scenario in {"single_tariff_registry_compromise", "tariff_compromise_with_independent_false_accept", "all_sources_compromised",
                    "registry_root_compromise"}:
        hs_value = parsed_hs
    if scenario in {"all_sources_compromised", "registry_root_compromise"}:
        quantity_value = parsed["quantity"]

    evidence = {
        "gross_weight": [
            (make_record("document_parser", "gross_weight", parsed["gross_weight"],
                         case, scenario, root, keys, credentials), credentials["document_parser"]),
            (make_record("weighbridge", "gross_weight", weight_value,
                         case, scenario, root, keys, credentials), credentials["weighbridge"]),
        ],
        "quantity": [
            (make_record("document_parser", "quantity", parsed["quantity"],
                         case, scenario, root, keys, credentials), credentials["document_parser"]),
            (make_record("rfid_counter", "quantity", quantity_value,
                         case, scenario, root, keys, credentials), credentials["rfid_counter"]),
        ],
        "hs_code": [
            (make_record("document_parser", "hs_code", parsed_hs,
                         case, scenario, root, keys, credentials), credentials["document_parser"]),
            (make_record("tariff_registry", "hs_code", hs_value,
                         case, scenario, root, keys, credentials), credentials["tariff_registry"]),
        ],
    }
    if scenario == "replay_attack":
        # A duplicated signed sensor assertion in one action batch must be rejected.
        evidence["gross_weight"].append(evidence["gross_weight"][1])
    if scenario == "cross_claim_substitution":
        evidence["hs_code"][1] = (
            make_record("weighbridge", "hs_code", parsed_hs,
                        case, scenario, root, keys, credentials),
            credentials["weighbridge"],
        )

    claim_results = {}
    verified_evidence = []
    consumed_nonces = set()
    last_sequences = {}
    for claim in CLAIMS:
        required = {
            "gross_weight": frozenset({"document_parser", "weighbridge"}),
            "quantity": frozenset({"document_parser", "rfid_counter"}),
            "hs_code": frozenset({"document_parser", "tariff_registry"}),
        }[claim]
        ok, reason, accepted = evaluate_claim(
            evidence[claim], trusted_issuer_key=root.public_key(), tenant_id=TENANT,
            claim_type=claim, expected_subject_id=subject_id,
            expected_action_id=action_id, expected_action_payload_digest=action_payload_digest,
            expected_document_digest=doc_digest,
            now=NOW, required_source_types=required,
            expected_unit={"gross_weight": "kg", "quantity": "items", "hs_code": "HS"}[claim],
            tolerance=0.01 if claim == "gross_weight" else 0.0,
            consumed_nonces=consumed_nonces, last_sequences=last_sequences,
        )
        claim_results[claim] = (ok, reason)
        verified_evidence.extend(accepted)

    all_claims_ok = all(value[0] for value in claim_results.values())
    evidence_digests = [
        canonical_sha256(record["envelope"])
        for claim_records in evidence.values() for record, _ in claim_records
    ]
    binding = issue_action_binding(
        action_id=action_id, action_payload_digest=action_payload_digest,
        subject_id=subject_id, document_digest=doc_digest,
        policy_version=POLICY, required_claims=CLAIMS, evidence_digests=evidence_digests,
        issued_at=NOW - 10, expires_at=NOW + 100, private_key=authorizer,
    )
    redeem_action = action_id
    redeem_payload = dict(case["action"])
    if scenario == "action_substitution":
        redeem_payload["name"] = "substituted-action"
    binding_ok, binding_reason = verify_action_binding(
        binding, trusted_authorizer_key=authorizer.public_key(),
        action_id=redeem_action, action_payload_digest=canonical_sha256(redeem_payload),
        subject_id=subject_id, document_digest=doc_digest,
        policy_version=POLICY, required_claims=CLAIMS,
        evidence_digests=evidence_digests, now=NOW,
    )

    legacy_action = evidence_gate_v1(case_for_gate)
    features = visible_features(case_for_gate)
    recovery = is_recoverable_verifier_false_reject(features, legacy_action)
    final_action = "ESCALATE"
    if all_claims_ok and binding_ok and (
        legacy_action == "ACT" or recovery
    ):
        final_action = "ACT"

    reasons = [f"{claim}:{reason}" for claim, (_, reason) in claim_results.items() if reason != "claim_supported"]
    if not binding_ok:
        reasons.append("action_binding:" + binding_reason)
    if not all_claims_ok and not reasons:
        reasons.append("claim_obligation_not_met")
    return {
        "scenario": scenario, "case_id": case["case_id"], "family": case["family"],
        "safe_to_act_ground_truth": bool(case["safe_to_act"]),
        "legacy_gate_action": legacy_action, "bounded_recovery_eligible": recovery,
        "gross_weight_status": claim_results["gross_weight"][1],
        "quantity_status": claim_results["quantity"][1],
        "hs_code_status": claim_results["hs_code"][1],
        "action_binding_status": binding_reason,
        "action": final_action,
        "unsafe_act": final_action == "ACT" and not bool(case["safe_to_act"]),
        "safe_act": final_action == "ACT" and bool(case["safe_to_act"]),
        "rejection_reasons": ";".join(reasons),
    }


def summarize(rows):
    out = []
    for scenario in SCENARIOS:
        group = [r for r in rows if r["scenario"] == scenario]
        safe = sum(r["safe_to_act_ground_truth"] for r in group)
        unsafe = len(group) - safe
        act = sum(r["action"] == "ACT" for r in group)
        unsafe_act = sum(r["unsafe_act"] for r in group)
        safe_act = sum(r["safe_act"] for r in group)
        out.append({
            "scenario": scenario, "cases": len(group), "ACT": act,
            "unsafe_ACT": unsafe_act, "safe_ACT": safe_act,
            "unsafe_ACT_rate_all_cases": unsafe_act / len(group),
            "unsafe_ACT_rate_conditional_on_ACT": unsafe_act / act if act else None,
            "safe_ACT_coverage": safe_act / safe if safe else None,
            "false_block_rate": (safe - safe_act) / safe if safe else None,
            "ESCALATE": len(group) - act,
        })
    return out


def main():
    cases = load_cases()
    if len(cases) != 700:
        raise AssertionError(f"expected 700 HIGH-risk cases, found {len(cases)}")
    rows = [run_one(case, scenario) for scenario in SCENARIOS for case in cases]
    summary = summarize(rows)
    by = {row["scenario"]: row for row in summary}
    if by["honest_baseline"]["unsafe_ACT"] != 0 or by["honest_baseline"]["safe_ACT_coverage"] != 1.0:
        raise AssertionError("honest baseline must have zero unsafe ACT and full safe-case coverage")
    for scenario in (
        "replay_attack", "stale_evidence", "cross_subject_substitution", "cross_claim_substitution",
        "parser_lineage_tampering", "invalid_calibration", "shared_admin_gateway",
        "credential_tampering", "action_substitution",
    ):
        if by[scenario]["ACT"] != 0:
            raise AssertionError(f"{scenario} must fail closed for all cases")
    if by["source_forgery_before_capture"]["unsafe_ACT"] != 0:
        raise AssertionError("honest physical evidence must block pre-capture source forgery")
    for scenario in (
        "single_weighbridge_compromise", "tariff_compromise_with_independent_false_accept",
        "all_sources_compromised", "registry_root_compromise",
    ):
        if by[scenario]["unsafe_ACT"] <= 0:
            raise AssertionError(f"{scenario} must expose a residual false-authorization path")
    if by["single_tariff_registry_compromise"]["unsafe_ACT"] != 0:
        raise AssertionError("the existing correlated-verifier guard should block isolated tariff-source compromise in C8")
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "evidence_provenance_v4_cases.csv", rows)
    write_csv(OUT / "evidence_provenance_v4_summary.csv", summary)
    hashes = {
        name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
        for name in ("evidence_provenance_v4_cases.csv", "evidence_provenance_v4_summary.csv")
    }
    manifest = {
        "protocol": "ega-evidence-provenance-v4",
        "status": "synthetic adversarial evidence-to-action experiment; not production validation",
        "benchmark_version": "0.4", "high_risk_cases_per_scenario": len(cases),
        "scenario_count": len(SCENARIOS), "case_scenario_rows": len(rows),
        "scenarios": list(SCENARIOS), "source_commit": os.getenv("GITHUB_SHA", "local"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "python_version": platform.python_version(), "outputs_sha256": hashes,
        "limitations": [
            "All identities, source credentials, evidence values and attacks are synthetic.",
            "Signatures authenticate enrolled keys and signed bytes, not semantic truth.",
            "Calibration and administrative-domain status are asserted test fields, not hardware-backed evidence.",
            "A compromised source can sign false but correctly scoped evidence.",
            "The trust root remains an explicit trust assumption.",
            "Deterministic counts are not real-world probabilities.",
        ],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "manifest": manifest}, indent=2))


if __name__ == "__main__":
    main()
