"""Run the dependency-root-aware v4 witness-independence experiment."""
from __future__ import annotations

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
from src.core import evidence_gate_v1, visible_features
from src.evidence_trust_v3 import (
    issue_witness_assertion,
    is_recoverable_verifier_false_reject,
)
from src.evidence_trust_v4 import (
    DEPENDENCY_LAYERS,
    issue_identity_credential_v4,
    verify_witness_quorum_v4,
)
from src.provenance import canonical_sha256
from scripts.run_evidence_trust_v3 import load_cases, write_csv, make_source_forgery

OUT = ROOT / "results" / "evidence_trust_v4_dependency_graph"
NOW = 1_800_000_000
TENANT = "tenant-synthetic"
NAMES = ("witness-1", "witness-2", "witness-3")

SCENARIOS = (
    "honest_baseline",
    "one_witness_compromised",
    "two_witnesses_compromised",
    "all_witnesses_compromised",
    "forged_source_identity",
    "source_forgery_before_capture",
    "shared_administrative_domain",
    "registry_root_compromise",
    "shared_parent_control",
    "shared_identity_provider",
    "shared_measurement_source",
    "shared_acquisition_pipeline",
    "two_compromised_shared_parent",
)


def key(name):
    seed = hashlib.sha256(("EGA-V4-TEST-ONLY|" + name).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def dependency_roots(index, scenario):
    roots = {layer: [f"{layer}-{index}"] for layer in DEPENDENCY_LAYERS}
    shared_scenarios = {
        "shared_parent_control": "parent_control",
        "shared_identity_provider": "identity_provider",
        "shared_measurement_source": "measurement_source",
        "shared_acquisition_pipeline": "acquisition_pipeline",
        "shared_administrative_domain": None,
    }
    if scenario in shared_scenarios and shared_scenarios[scenario]:
        layer = shared_scenarios[scenario]
        roots[layer] = [f"shared-{layer}-root"]
    if scenario == "two_compromised_shared_parent" and index in (1, 2):
        roots["parent_control"] = ["shared-compromised-parent"]
    return roots


def make_credentials(root_private, scenario):
    credentials, private_keys = [], []
    compromised = {
        "one_witness_compromised": {0},
        "two_witnesses_compromised": {0, 1},
        "all_witnesses_compromised": {0, 1, 2},
        "two_compromised_shared_parent": {0, 1},
        "registry_root_compromise": {0, 1},
    }.get(scenario, set())
    for index, name in enumerate(NAMES, 1):
        private = key(name)
        private_keys.append(private)
        credentials.append(issue_identity_credential_v4(
            issuer_id="ega-v4-synthetic-registry-root",
            witness_id=name, key_id=f"{name}-key",
            public_key=private.public_key(), source_id=f"independent-source-{index}",
            acquisition_domain=f"acquisition-domain-{index}",
            administrative_domain=(
                "shared-admin" if scenario == "shared_administrative_domain"
                else f"administrative-domain-{index}"
            ),
            tenant_id=TENANT,
            dependency_roots=dependency_roots(index, scenario),
            serial=f"credential-{index}", issued_at=NOW - 100,
            expires_at=NOW + 10000, issuer_private_key=root_private,
        ))
    root_public = root_private.public_key()
    if scenario == "forged_source_identity":
        credentials[0] = dict(credentials[0])
        credentials[0]["body"] = dict(
            credentials[0]["body"], source_id="attacker-source"
        )
    if scenario == "registry_root_compromise":
        attacker_root = key("attacker-registry-root")
        root_public = attacker_root.public_key()
        for index in (0, 1):
            credentials[index] = issue_identity_credential_v4(
                issuer_id="attacker-registry-root",
                witness_id=f"attacker-witness-{index+1}",
                key_id=f"attacker-key-{index+1}",
                public_key=private_keys[index].public_key(),
                source_id=f"attacker-source-{index+1}",
                acquisition_domain=f"attacker-acquisition-{index+1}",
                administrative_domain=f"attacker-admin-{index+1}",
                tenant_id=TENANT,
                dependency_roots=dependency_roots(index + 1, scenario),
                serial=f"attacker-credential-{index+1}",
                issued_at=NOW - 100, expires_at=NOW + 10000,
                issuer_private_key=attacker_root,
            )
    return private_keys, credentials, root_public, compromised


def action_for_policy(case, decision_case, legacy_action, quorum_valid):
    recovery = False
    if quorum_valid:
        recovery = is_recoverable_verifier_false_reject(
            visible_features(decision_case), legacy_action
        )
    action = (
        "ACT" if quorum_valid and (legacy_action == "ACT" or recovery)
        else "ESCALATE"
    )
    return action, recovery


def scenario_rows(cases, scenario):
    root_private = key("registry-root")
    private_keys, credentials, root_public, compromised = make_credentials(
        root_private, scenario
    )
    rows = []
    for index, original_case in enumerate(cases):
        case = (
            make_source_forgery(original_case)
            if scenario == "source_forgery_before_capture"
            else copy.deepcopy(original_case)
        )
        observable = case["observable"]
        interpreted = observable["machine"]["extraction"]
        expected_weight = float(interpreted["gross_weight"])
        expected_type = observable["external"]["inspection_item_type"]
        parent = canonical_sha256({
            "tenant": TENANT, "case": case["case_id"],
            "documents": observable["document_instances"],
        })
        records = []
        for witness_index, (private, credential) in enumerate(
            zip(private_keys, credentials)
        ):
            if witness_index in compromised:
                weight = expected_weight
                item_type = expected_type
            else:
                weight = float(case["ground_truth"]["gross_weight"])
                item_type = case["ground_truth"]["item_type"]
            record = issue_witness_assertion(
                credential=credential, witness_private_key=private,
                tenant_id=TENANT, case_id=case["case_id"],
                parent_digest=parent, gross_weight=weight,
                item_type=item_type,
                nonce=f"{scenario}-{index}-{witness_index}",
                issued_at=NOW - 10, expires_at=NOW + 300,
            )
            records.append((record, credential))

        quorum_field, reason_field, support_field = verify_witness_quorum_v4(
            records, trusted_issuer_key=root_public, tenant_id=TENANT,
            case_id=case["case_id"], parent_digest=parent,
            expected_weight=expected_weight, expected_item_type=expected_type,
            now=NOW, threshold=2, total_required=3, dependency_aware=False,
        )
        quorum_graph, reason_graph, support_graph = verify_witness_quorum_v4(
            records, trusted_issuer_key=root_public, tenant_id=TENANT,
            case_id=case["case_id"], parent_digest=parent,
            expected_weight=expected_weight, expected_item_type=expected_type,
            now=NOW, threshold=2, total_required=3, dependency_aware=True,
        )
        quorum_graph_3, reason_graph_3, support_graph_3 = verify_witness_quorum_v4(
            records, trusted_issuer_key=root_public, tenant_id=TENANT,
            case_id=case["case_id"], parent_digest=parent,
            expected_weight=expected_weight, expected_item_type=expected_type,
            now=NOW, threshold=3, total_required=3, dependency_aware=True,
        )

        any_quorum = quorum_field or quorum_graph or quorum_graph_3
        decision_case = copy.deepcopy(case)
        if any_quorum:
            decision_case["observable"]["external"]["measured_weight"] = expected_weight
            legacy = evidence_gate_v1(decision_case)
        else:
            legacy = "ESCALATE"

        action_field, recovery_field = action_for_policy(
            case, decision_case, legacy, quorum_field
        )
        action_graph, recovery_graph = action_for_policy(
            case, decision_case, legacy, quorum_graph
        )
        action_graph_3, recovery_graph_3 = action_for_policy(
            case, decision_case, legacy, quorum_graph_3
        )
        row = {
            "scenario": scenario,
            "case_id": case["case_id"],
            "family": case["family"],
            "safe_to_act_ground_truth": bool(case["safe_to_act"]),
            "legacy_gate_action": legacy,
            "field_only_quorum_valid": quorum_field,
            "field_only_quorum_reason": reason_field,
            "field_only_matching_witnesses": support_field,
            "field_only_action": action_field,
            "field_only_recovery": recovery_field,
            "field_only_unsafe_act": bool(action_field == "ACT" and not case["safe_to_act"]),
            "field_only_safe_act": bool(action_field == "ACT" and case["safe_to_act"]),
            "graph_2of3_quorum_valid": quorum_graph,
            "graph_2of3_quorum_reason": reason_graph,
            "graph_2of3_matching_witnesses": support_graph,
            "graph_2of3_action": action_graph,
            "graph_2of3_recovery": recovery_graph,
            "graph_2of3_unsafe_act": bool(action_graph == "ACT" and not case["safe_to_act"]),
            "graph_2of3_safe_act": bool(action_graph == "ACT" and case["safe_to_act"]),
            "graph_3of3_quorum_valid": quorum_graph_3,
            "graph_3of3_quorum_reason": reason_graph_3,
            "graph_3of3_matching_witnesses": support_graph_3,
            "graph_3of3_action": action_graph_3,
            "graph_3of3_recovery": recovery_graph_3,
            "graph_3of3_unsafe_act": bool(action_graph_3 == "ACT" and not case["safe_to_act"]),
            "graph_3of3_safe_act": bool(action_graph_3 == "ACT" and case["safe_to_act"]),
        }
        rows.append(row)
    return rows


def summarize(rows):
    summary = []
    for scenario in SCENARIOS:
        subset = [row for row in rows if row["scenario"] == scenario]
        n = len(subset)
        safe_n = sum(row["safe_to_act_ground_truth"] for row in subset)
        entry = {"scenario": scenario, "cases": n, "safe_cases": safe_n}
        for prefix in ("field_only", "graph_2of3", "graph_3of3"):
            action_key = prefix + "_action"
            unsafe_key = prefix + "_unsafe_act"
            safe_key = prefix + "_safe_act"
            recovery_key = prefix + "_recovery"
            acts = sum(row[action_key] == "ACT" for row in subset)
            unsafe = sum(row[unsafe_key] for row in subset)
            safe_acts = sum(row[safe_key] for row in subset)
            entry.update({
                prefix + "_ACT": acts,
                prefix + "_unsafe_ACT": unsafe,
                prefix + "_recoveries": sum(row[recovery_key] for row in subset),
                prefix + "_unsafe_rate_all_cases": round(unsafe / n, 6) if n else None,
                prefix + "_unsafe_rate_given_ACT": round(unsafe / acts, 6) if acts else None,
                prefix + "_safe_action_coverage": round(safe_acts / safe_n, 6) if safe_n else None,
                prefix + "_false_block_rate": round((safe_n - safe_acts) / safe_n, 6) if safe_n else None,
            })
        summary.append(entry)
    return summary


def main():
    cases = load_cases()
    rows = []
    for scenario in SCENARIOS:
        rows.extend(scenario_rows(cases, scenario))
    summary = summarize(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "evidence_trust_v4_cases.csv", rows)
    write_csv(OUT / "evidence_trust_v4_summary.csv", summary)
    manifest = {
        "protocol": "ega-evidence-trust-architecture-v4-dependency-roots",
        "status": "synthetic threat experiment; not production validation",
        "benchmark_version": "0.4",
        "high_risk_cases_per_scenario": len(cases),
        "scenario_count": len(SCENARIOS),
        "case_scenario_rows": len(rows),
        "policies": [
            "field-only 2-of-3 ablation",
            "dependency-root-aware 2-of-3",
            "dependency-root-aware 3-of-3 sensitivity",
        ],
        "dependency_layers": list(DEPENDENCY_LAYERS),
        "scenarios": list(SCENARIOS),
        "limitations": [
            "All keys, identities, measurements, dependency roots and source records are synthetic.",
            "Dependency roots are registry-signed claims, not independently proven organizational or technical facts.",
            "Unknown or omitted dependency layers fail credential validation.",
            "Graph-aware quorum detects only declared shared roots; hidden or false declarations remain possible.",
            "All-witness collusion and registry-root compromise remain trust-model limitations.",
            "Deterministic benchmark counts are not real-world probabilities.",
        ],
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
        "outputs_sha256": {
            name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
            for name in ("evidence_trust_v4_cases.csv", "evidence_trust_v4_summary.csv")
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
