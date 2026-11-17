"""Compare key, direct-field and dependency-graph witness policies on benchmark v0.4."""
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
from src.evidence_provenance_v4 import issue_claim_evidence
from src.evidence_trust_v3 import is_recoverable_verifier_false_reject
from src.dependency_graph_v5 import (
    issue_dependency_graph, issue_graph_bound_source_credential, evaluate_quorum,
)
from src.provenance import canonical_sha256

BENCH = ROOT / "data" / "benchmark_v0.4" / "cases.jsonl"
OUT = ROOT / "results" / "dependency_graph_v5"
NOW = 1_800_000_000
TENANT = "ega-v5-synthetic-tenant"
POLICIES = {
    "K2_key_unique": ("key_unique", 2),
    "F2_field_distinct": ("field_distinct", 2),
    "F3_field_distinct": ("field_distinct", 3),
    "G2_graph_aware": ("graph_aware", 2),
}
SCENARIOS = (
    "honest_baseline",
    "one_witness_compromised",
    "two_witnesses_compromised",
    "all_witnesses_compromised",
    "direct_shared_admin",
    "hidden_shared_parent",
    "hidden_shared_idp",
    "hidden_shared_kms",
    "hidden_shared_firmware",
    "hidden_shared_upstream",
    "incomplete_dependency_manifest",
    "graph_structure_attack",
    "graph_integrity_attack",
    "registry_root_compromise",
)


def key(name):
    seed = hashlib.sha256(("EGA-V5-TEST-ONLY|" + name).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def load_cases():
    with BENCH.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    return [row for row in rows if row["action"]["risk_level"] == "HIGH"]


def write_csv(path, rows):
    if not rows:
        raise ValueError("refusing to write empty output")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def compromised_witnesses(scenario):
    return {
        "honest_baseline": set(),
        "one_witness_compromised": {"w1"},
        "two_witnesses_compromised": {"w1", "w2"},
        "all_witnesses_compromised": {"w1", "w2", "w3"},
        "direct_shared_admin": {"w1", "w2"},
        "hidden_shared_parent": {"w1", "w2"},
        "hidden_shared_idp": {"w1", "w2"},
        "hidden_shared_kms": {"w1", "w2"},
        "hidden_shared_firmware": {"w1", "w2"},
        "hidden_shared_upstream": {"w1", "w2"},
        "incomplete_dependency_manifest": {"w1", "w2"},
        "graph_structure_attack": {"w1", "w2"},
        "graph_integrity_attack": {"w1", "w2"},
        "registry_root_compromise": {"w1", "w2"},
    }[scenario]


def make_graph(scenario, root):
    nodes = {}
    kinds = ("admin", "idp", "kms", "firmware", "acquisition", "physical", "upstream")
    for name in ("w1", "w2", "w3"):
        nodes[f"source:witness-{name}"] = [f"{kind}:{name}" for kind in kinds]
        for kind in kinds:
            nodes[f"{kind}:{name}"] = []

    shared_kind = {
        "hidden_shared_parent": ("admin", "parent:common-control"),
        "hidden_shared_idp": ("idp", "idp:shared-tenant"),
        "hidden_shared_kms": ("kms", "kms:shared-vault"),
        "hidden_shared_firmware": ("firmware", "firmware:shared-build"),
        "hidden_shared_upstream": ("upstream", "feed:shared-aggregator"),
    }.get(scenario)
    if shared_kind:
        kind, ancestor = shared_kind
        for name in ("w1", "w2"):
            nodes[f"{kind}:{name}"] = [ancestor]
        nodes[ancestor] = []

    if scenario == "registry_root_compromise":
        # The real topology has w1 and w2 under a common parent. The compromised
        # registry signs a forged manifest that omits that true shared ancestor.
        # The signed graph therefore looks disjoint even though the real sources are not.
        pass

    if scenario == "graph_structure_attack":
        nodes["admin:w1"] = ["missing:dependency-parent"]

    graph = issue_dependency_graph(
        graph_id="ega-v5-dependency-graph", version="1", tenant_id=TENANT,
        nodes=nodes, issued_at=NOW - 100, expires_at=NOW + 10000,
        signer_private_key=root,
    )
    if scenario == "graph_integrity_attack":
        graph = {"body": dict(graph["body"]), "signature_b64": graph["signature_b64"]}
        graph["body"]["graph_id"] = "tampered-graph-id"
    return graph


def make_sources(scenario, graph):
    root = key("attacker-registry-root" if scenario == "registry_root_compromise" else "registry-root")
    compromised = compromised_witnesses(scenario)
    keys = {
        name: key(name + ("-attacker" if name in compromised else ""))
        for name in ("w1", "w2", "w3")
    }
    creds = {}
    for name in ("w1", "w2", "w3"):
        direct_admin = "shared-admin" if scenario == "direct_shared_admin" and name in {"w1", "w2"} else f"admin-{name}"
        creds[name] = issue_graph_bound_source_credential(
            graph_digest=graph["body"]["graph_digest"],
            dependency_leaf_node=f"source:witness-{name}",
            dependency_manifest_complete=not (
                scenario == "incomplete_dependency_manifest" and name == "w1"
            ),
            issuer_id="synthetic-v5-registry", source_id=f"witness-{name}",
            source_type="weighbridge", key_id=f"key-{name}",
            public_key=keys[name].public_key(), allowed_claims=["gross_weight"],
            acquisition_domain=f"acquisition-{name}",
            administrative_domain=direct_admin,
            gateway_id=f"gateway-{name}", key_admin_domain=f"key-admin-{name}",
            tenant_id=TENANT, serial=f"serial-{scenario}-{name}",
            issued_at=NOW - 100, expires_at=NOW + 10000,
            issuer_private_key=root,
        )
    return root, keys, creds, compromised


def make_records(case, scenario, root, keys, creds, compromised):
    expected_weight = case["observable"]["machine"]["extraction"]["gross_weight"]
    ground_truth_weight = case["ground_truth"]["gross_weight"]
    document_digest = canonical_sha256(case["observable"]["document_instances"])
    action_id = "submit:" + case["case_id"]
    action_payload_digest = canonical_sha256(case["action"])
    records = []
    for name in ("w1", "w2", "w3"):
        value = expected_weight if name in compromised else ground_truth_weight
        unit = "kg"
        record = issue_claim_evidence(
            credential=creds[name], source_private_key=keys[name],
            claim_type="gross_weight", value=value, unit=unit,
            subject_id=case["case_id"], action_id=action_id,
            action_payload_digest=action_payload_digest,
            document_digest=document_digest, input_digest=document_digest,
            output_digest=canonical_sha256({
                "claim_type": "gross_weight", "value": value, "unit": unit,
            }),
            transformation_id="witness-measurement-" + name,
            tool_version="synthetic-scale-witness-1.0",
            observed_at=NOW - 10, issued_at=NOW - 10, expires_at=NOW + 100,
            sequence_number=1,
            nonce=f"{case['case_id']}:{scenario}:{name}",
            calibration_id="calibration-" + name,
            calibration_valid_until=NOW + 1000,
        )
        records.append((record, creds[name]))
    return records, expected_weight, document_digest, action_id, action_payload_digest


def evaluate_one(case, scenario, policy_name, policy, threshold):
    graph_root = key("attacker-registry-root" if scenario == "registry_root_compromise" else "registry-root")
    graph = make_graph(scenario, graph_root)
    root, keys, creds, compromised = make_sources(scenario, graph)
    records, expected_weight, document_digest, action_id, action_payload_digest = make_records(
        case, scenario, root, keys, creds, compromised)
    quorum_ok, quorum_reason, supporters = evaluate_quorum(
        records, policy=policy, threshold=threshold,
        trusted_registry_key=root.public_key(), tenant_id=TENANT,
        graph_record=graph, claim_type="gross_weight", expected_value=expected_weight,
        expected_unit="kg", expected_subject_id=case["case_id"],
        expected_action_id=action_id,
        expected_action_payload_digest=action_payload_digest,
        expected_document_digest=document_digest, now=NOW,
        tolerance=0.01,
    )

    case_for_gate = copy.deepcopy(case)
    if quorum_ok:
        # Controller consumes only the measurement admitted by the selected quorum.
        case_for_gate["observable"]["external"]["measured_weight"] = expected_weight
        legacy_action = evidence_gate_v1(case_for_gate)
        features = visible_features(case_for_gate)
        recovery = is_recoverable_verifier_false_reject(features, legacy_action)
        action = "ACT" if legacy_action == "ACT" or recovery else "ESCALATE"
    else:
        legacy_action, recovery, action = "ESCALATE", False, "ESCALATE"

    safe = bool(case["safe_to_act"])
    return {
        "scenario": scenario, "policy": policy_name, "case_id": case["case_id"],
        "family": case["family"], "safe_to_act_ground_truth": safe,
        "ground_truth_common_dependency": scenario in {
            "direct_shared_admin", "hidden_shared_parent", "hidden_shared_idp",
            "hidden_shared_kms", "hidden_shared_firmware", "hidden_shared_upstream",
            "registry_root_compromise",
        },
        "registry_graph_omits_true_common_parent": scenario == "registry_root_compromise",
        "quorum_valid": quorum_ok, "quorum_reason": quorum_reason,
        "matching_supporters": len(supporters),
        "legacy_gate_action": legacy_action, "bounded_recovery_eligible": recovery,
        "action": action, "unsafe_act": action == "ACT" and not safe,
        "safe_act": action == "ACT" and safe,
    }


def summarize(rows):
    out = []
    for scenario in SCENARIOS:
        for policy in POLICIES:
            group = [r for r in rows if r["scenario"] == scenario and r["policy"] == policy]
            safe_count = sum(r["safe_to_act_ground_truth"] for r in group)
            act_count = sum(r["action"] == "ACT" for r in group)
            unsafe = sum(r["unsafe_act"] for r in group)
            safe_act = sum(r["safe_act"] for r in group)
            out.append({
                "scenario": scenario, "policy": policy, "cases": len(group),
                "ACT": act_count, "unsafe_ACT": unsafe, "safe_ACT": safe_act,
                "unsafe_ACT_rate_all_cases": unsafe / len(group),
                "unsafe_ACT_rate_conditional_on_ACT": unsafe / act_count if act_count else None,
                "safe_ACT_coverage": safe_act / safe_count if safe_count else None,
                "false_block_rate": (safe_count - safe_act) / safe_count if safe_count else None,
                "ESCALATE": len(group) - act_count,
            })
    return out


def main():
    cases = load_cases()
    if len(cases) != 700:
        raise AssertionError(f"expected 700 HIGH-risk cases, found {len(cases)}")
    rows = [
        evaluate_one(case, scenario, policy_name, policy, threshold)
        for scenario in SCENARIOS for policy_name, (policy, threshold) in POLICIES.items()
        for case in cases
    ]
    summary = summarize(rows)
    by = {(r["scenario"], r["policy"]): r for r in summary}

    def metric(scenario, policy, field):
        return by[(scenario, policy)][field]

    for policy in POLICIES:
        if metric("honest_baseline", policy, "unsafe_ACT") != 0:
            raise AssertionError(f"{policy} unsafe in honest baseline")
        if metric("honest_baseline", policy, "safe_ACT_coverage") != 1.0:
            raise AssertionError(f"{policy} failed to cover all safe baseline cases")
    if metric("two_witnesses_compromised", "F2_field_distinct", "unsafe_ACT") <= 0:
        raise AssertionError("F2 should expose two-witness collusion")
    if metric("two_witnesses_compromised", "F3_field_distinct", "unsafe_ACT") != 0:
        raise AssertionError("F3 should block two-witness collusion when the third witness is honest")
    if metric("two_witnesses_compromised", "G2_graph_aware", "unsafe_ACT") <= 0:
        raise AssertionError("graph-aware policy should not hide independent two-witness collusion")
    for scenario in ("hidden_shared_parent", "hidden_shared_idp", "hidden_shared_kms",
                     "hidden_shared_firmware", "hidden_shared_upstream"):
        if metric(scenario, "F2_field_distinct", "unsafe_ACT") <= 0:
            raise AssertionError(f"flat-field policy did not expose {scenario}")
        if metric(scenario, "G2_graph_aware", "unsafe_ACT") != 0:
            raise AssertionError(f"graph-aware policy failed to block {scenario}")
    if metric("direct_shared_admin", "K2_key_unique", "unsafe_ACT") <= 0:
        raise AssertionError("key-only policy should fail under direct shared administration")
    if metric("direct_shared_admin", "F2_field_distinct", "unsafe_ACT") != 0:
        raise AssertionError("field-distinct policy should block direct shared administration")
    if metric("incomplete_dependency_manifest", "G2_graph_aware", "unsafe_ACT") != 0:
        raise AssertionError("graph-aware policy should fail closed on incomplete dependency manifests")
    if metric("graph_structure_attack", "G2_graph_aware", "unsafe_ACT") != 0:
        raise AssertionError("graph-aware policy should fail closed on unresolved graph nodes")
    if metric("graph_integrity_attack", "G2_graph_aware", "unsafe_ACT") != 0:
        raise AssertionError("graph-aware policy should fail closed on graph signature tampering")
    if metric("registry_root_compromise", "F2_field_distinct", "unsafe_ACT") <= 0:
        raise AssertionError("two colluding witnesses should pass the field-distinct policy under root compromise")
    if metric("registry_root_compromise", "F3_field_distinct", "unsafe_ACT") != 0:
        raise AssertionError("strict 3-of-3 should reject two colluding witnesses when the third remains honest")
    if metric("registry_root_compromise", "G2_graph_aware", "unsafe_ACT") <= 0:
        raise AssertionError("compromised registry root should expose graph-trust residual")

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "dependency_graph_v5_cases.csv", rows)
    write_csv(OUT / "dependency_graph_v5_summary.csv", summary)
    hashes = {
        name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
        for name in ("dependency_graph_v5_cases.csv", "dependency_graph_v5_summary.csv")
    }
    manifest = {
        "protocol": "ega-dependency-graph-v5",
        "status": "synthetic graph-aware witness-independence comparison; not production validation",
        "benchmark_version": "0.4", "high_risk_cases_per_scenario": len(cases),
        "scenario_count": len(SCENARIOS), "policy_count": len(POLICIES),
        "case_policy_scenario_rows": len(rows), "scenarios": list(SCENARIOS),
        "policies": {name: {"policy": value[0], "threshold": value[1]} for name, value in POLICIES.items()},
        "source_commit": os.getenv("GITHUB_SHA", "local"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "python_version": platform.python_version(), "outputs_sha256": hashes,
        "limitations": [
            "All identities, dependency graphs, source values and attacks are synthetic.",
            "A signed dependency graph authenticates registry assertions, not their real-world completeness.",
            "Distinct dependency nodes do not prove independent ownership, operation, hardware or data.",
            "Registry-root compromise can falsify source credentials and dependency ancestry.",
            "The experiment does not implement production PKI, KMS/HSM, hardware attestation or atomic commit.",
            "Counts are deterministic synthetic outcomes, not real-world probabilities.",
        ],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "manifest": manifest}, indent=2))


if __name__ == "__main__":
    main()
