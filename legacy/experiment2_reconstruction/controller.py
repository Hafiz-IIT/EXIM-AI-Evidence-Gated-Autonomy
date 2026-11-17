"""Clearly labeled reconstruction of the archived Experiment 2B/2D/2E controllers.

This is not the missing historical source file. It is reconstructed from the
recovered v1/provenance primitives, original benchmark, attestation records,
decision cache and archived result tables. The tests require exact agreement
with those archived outputs for the documented synthetic cases.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Callable

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from legacy.experiment2_original.src import core as legacy_core
from legacy.experiment2_original.src import provenance as legacy_provenance

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_TRUST_ROOTS_PATH = ROOT / "legacy/experiment2_original/2A_attestation/trust_roots.json"
RECONSTRUCTED_LINEAGE_ROOTS_PATH = Path(__file__).resolve().parent / "lineage_trust_roots_reconstructed.json"

ATTACKS_2B = (
    "none", "dependency_spoof", "external_masking", "timestamp_masking",
    "strip_attestations", "payload_tamper", "replay_attestation", "combined_spoof",
)
ATTACKS_2D = (
    "none", "verifier_A", "verifier_AB", "verifier_ABC",
    "external_sensor", "authorization_authority", "all_roots",
)
ATTACKS_2E = (
    "none", "verifier_A", "lineage_A", "lineage_B",
    "verifier_A_plus_lineage_A", "both_lineage", "verifier_A_plus_both",
)
POLICY_V1 = "EvidenceGate_v1"
POLICY_V2 = "EvidenceGate_v2_attested"

TRUST_ROOTS = json.loads(ORIGINAL_TRUST_ROOTS_PATH.read_text(encoding="utf-8"))
LINEAGE_ROOTS = json.loads(RECONSTRUCTED_LINEAGE_ROOTS_PATH.read_text(encoding="utf-8"))
TRUSTED_SIGNERS = set(TRUST_ROOTS) | set(LINEAGE_ROOTS)


def canonical_bytes(value: dict) -> bytes:
    return legacy_provenance.canonical_bytes(value)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _public_key_hash(signer: str) -> str | None:
    if signer not in TRUSTED_SIGNERS:
        return None
    key = legacy_provenance.deterministic_test_key(signer).public_key()
    raw = key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return sha256_bytes(raw)


def verify_signature(attestation: dict) -> bool:
    signer = attestation.get("signer")
    if signer in TRUST_ROOTS:
        expected = TRUST_ROOTS[signer]["public_key_sha256"]
    elif signer in LINEAGE_ROOTS:
        expected = LINEAGE_ROOTS[signer]["public_key_sha256"]
    else:
        return False
    return _public_key_hash(signer) == expected and legacy_provenance.verify(attestation, TRUSTED_SIGNERS)


def _expected_attestation_payloads(case: dict) -> dict:
    observable = case["observable"]
    expected = {}
    for name, document in observable["documents"].items():
        if document is not None:
            expected[("document", name)] = {
                "kind": "document",
                "name": name,
                "hash": sha256_bytes(canonical_bytes(document)),
                "dependency_root": "doc_origin_cluster",
            }
    external = observable["external"]
    auth = external["authorization"]
    expected[("external_weight", None)] = {
        "kind": "external_weight",
        "value": external["measured_weight"],
        "evaluation_day": external["evaluation_day"],
        "dependency_root": "external_sensor_root",
    }
    expected[("authorization", None)] = {
        "kind": "authorization",
        "present": auth["present"],
        "issue_day": auth["issue_day"],
        "expiry_day": auth["expiry_day"],
        "evaluation_day": external["evaluation_day"],
        "dependency_root": "authorization_root",
    }
    for verifier in observable["machine"]["verifiers"]:
        expected[("verifier", verifier["verifier_id"])] = {
            "kind": "verifier",
            "verifier_id": verifier["verifier_id"],
            "accept": verifier["accept"],
            "dependency_group": verifier["dependency_group"],
            "type": verifier["type"],
        }
    return expected


def verify_attestations(case: dict, *, ignore_verifier_dependency: bool = False) -> bool:
    expected = _expected_attestation_payloads(case)
    seen = set()
    for attestation in case["observable"].get("attestations", []):
        payload = attestation.get("payload", {})
        kind = payload.get("kind")
        key = (
            kind,
            payload.get("name") if kind == "document"
            else payload.get("verifier_id") if kind == "verifier"
            else None,
        )
        if key not in expected or key in seen or not verify_signature(attestation):
            return False
        target = expected[key]
        if kind == "verifier" and ignore_verifier_dependency:
            fields = ("kind", "verifier_id", "accept", "type")
            if any(payload.get(field) != target.get(field) for field in fields):
                return False
        elif payload != target:
            return False
        seen.add(key)
    return seen == set(expected)


def verify_dual_lineage(case: dict) -> bool:
    observable = case["observable"]
    verifiers = observable["machine"]["verifiers"]
    attestations = observable.get("lineage_attestations", [])
    if len(attestations) != 2 * len(verifiers):
        return False
    for verifier in verifiers:
        entries = [
            item for item in attestations
            if item.get("payload", {}).get("verifier_id") == verifier["verifier_id"]
        ]
        if len(entries) != 2 or {item.get("signer") for item in entries} != {"lineage_A", "lineage_B"}:
            return False
        groups = set()
        for item in entries:
            if not verify_signature(item):
                return False
            payload = item.get("payload", {})
            if payload.get("kind") != "lineage" or payload.get("verifier_id") != verifier["verifier_id"]:
                return False
            groups.add(payload.get("dependency_group"))
        if len(groups) != 1 or next(iter(groups)) != verifier["dependency_group"]:
            return False
    return True


def evidence_gate_v2_attested(case: dict) -> str:
    # Missing critical evidence is requested before cryptographic validation.
    if case["observable"].get("missing"):
        return "REQUEST_EVIDENCE"
    if not verify_attestations(case, ignore_verifier_dependency=False):
        return "ESCALATE"
    return legacy_core.evidence_gate_v1(case)


def evidence_gate_v3_dual_lineage(case: dict) -> str:
    if case["observable"].get("missing"):
        return "REQUEST_EVIDENCE"
    # Reconstruction assumption: the v3 gate verifies the verifier's signed
    # decision but treats the dependency group as a separately attested claim.
    # It does not bind that group back to the verifier signature's group field.
    if not verify_attestations(case, ignore_verifier_dependency=True):
        return "ESCALATE"
    if not verify_dual_lineage(case):
        return "ESCALATE"
    return legacy_core.evidence_gate_v1(case)


def generate_attested_cases(cases: list[dict]) -> tuple[list[dict], list[dict]]:
    high = [case for case in cases if case["action"]["risk_level"] == "HIGH"]
    attested_v2, attested_v3 = [], []
    for original in high:
        case = copy.deepcopy(original)
        # The archived 0.3 benchmark predates the later-added convenience
        # field. Strip it to reproduce the exact historical schema.
        case.pop("safe_to_act", None)
        observable = case["observable"]
        attestations = []
        for name, document in observable["documents"].items():
            if document is None:
                continue
            payload = {
                "kind": "document", "name": name,
                "hash": sha256_bytes(canonical_bytes(document)),
                "dependency_root": "doc_origin_cluster",
            }
            attestations.append(legacy_provenance.sign("document_origin", payload))
        external = observable["external"]
        attestations.append(legacy_provenance.sign("external_sensor", {
            "kind": "external_weight", "value": external["measured_weight"],
            "evaluation_day": external["evaluation_day"],
            "dependency_root": "external_sensor_root",
        }))
        auth = external["authorization"]
        attestations.append(legacy_provenance.sign("authorization_authority", {
            "kind": "authorization", "present": auth["present"],
            "issue_day": auth["issue_day"], "expiry_day": auth["expiry_day"],
            "evaluation_day": external["evaluation_day"],
            "dependency_root": "authorization_root",
        }))
        lineage_attestations = []
        for index, verifier in enumerate(observable["machine"]["verifiers"]):
            signer = ("verifier_A", "verifier_B", "verifier_C")[index]
            verifier_payload = {
                "kind": "verifier", "verifier_id": verifier["verifier_id"],
                "accept": verifier["accept"], "dependency_group": verifier["dependency_group"],
                "type": verifier["type"],
            }
            attestations.append(legacy_provenance.sign(signer, verifier_payload))
            for lineage_signer in ("lineage_A", "lineage_B"):
                lineage_attestations.append(legacy_provenance.sign(lineage_signer, {
                    "kind": "lineage", "verifier_id": verifier["verifier_id"],
                    "dependency_group": verifier["dependency_group"],
                }))
        observable["attestations"] = attestations
        attested_v2.append(copy.deepcopy(case))
        observable["lineage_attestations"] = lineage_attestations
        attested_v3.append(case)
    return attested_v2, attested_v3


def _resign(attestation: dict) -> dict:
    return legacy_provenance.sign(attestation["signer"], attestation["payload"])


def _attack_dependency_spoof(case: dict) -> dict:
    changed = copy.deepcopy(case)
    verifier = changed["observable"]["machine"]["verifiers"][0]
    verifier["dependency_group"] = "spoofed-" + verifier["verifier_id"]
    return changed


def _attack_external_masking(case: dict) -> dict:
    changed = copy.deepcopy(case)
    external = changed["observable"]["external"]
    documents = [doc for doc in changed["observable"]["documents"].values() if doc is not None]
    if documents and abs(float(external["measured_weight"]) - float(documents[0]["gross_weight"])) > 1e-9:
        external["measured_weight"] = documents[0]["gross_weight"]
    return changed


def _attack_timestamp_masking(case: dict) -> dict:
    changed = copy.deepcopy(case)
    external = changed["observable"]["external"]
    external["authorization"]["expiry_day"] = external["evaluation_day"] + 100
    return changed


def _attack_strip_attestations(case: dict) -> dict:
    changed = copy.deepcopy(case)
    changed["observable"]["attestations"] = []
    return changed


def _attack_payload_tamper(case: dict) -> dict:
    changed = copy.deepcopy(case)
    changed["observable"]["attestations"][0]["payload"]["hash"] = "0" * 64
    return changed


def _attack_replay_attestation(case: dict, index: int, all_cases: list[dict]) -> dict:
    changed = copy.deepcopy(case)
    changed["observable"]["attestations"][0] = copy.deepcopy(
        all_cases[(index + 1) % len(all_cases)]["observable"]["attestations"][0]
    )
    return changed


def apply_2b_attack(case: dict, attack: str, index: int, all_cases: list[dict]) -> dict:
    if attack == "none":
        return copy.deepcopy(case)
    if attack == "dependency_spoof":
        return _attack_dependency_spoof(case)
    if attack == "external_masking":
        return _attack_external_masking(case)
    if attack == "timestamp_masking":
        return _attack_timestamp_masking(case)
    if attack == "strip_attestations":
        return _attack_strip_attestations(case)
    if attack == "payload_tamper":
        return _attack_payload_tamper(case)
    if attack == "replay_attestation":
        return _attack_replay_attestation(case, index, all_cases)
    if attack == "combined_spoof":
        return _attack_timestamp_masking(_attack_external_masking(_attack_dependency_spoof(case)))
    raise ValueError(f"unknown Experiment 2B attack: {attack}")


def _compromise_verifiers(case: dict, count: int = 1) -> dict:
    changed = copy.deepcopy(case)
    verifiers = changed["observable"]["machine"]["verifiers"]
    for verifier in verifiers[:count]:
        verifier["dependency_group"] = "spoofed-" + verifier["verifier_id"]
        for index, attestation in enumerate(changed["observable"]["attestations"]):
            payload = attestation.get("payload", {})
            if payload.get("kind") == "verifier" and payload.get("verifier_id") == verifier["verifier_id"]:
                payload["dependency_group"] = verifier["dependency_group"]
                changed["observable"]["attestations"][index] = _resign(attestation)
                break
    return changed


def _compromise_external_sensor(case: dict) -> dict:
    changed = copy.deepcopy(case)
    documents = [doc for doc in changed["observable"]["documents"].values() if doc is not None]
    external = changed["observable"]["external"]
    external["measured_weight"] = documents[0]["gross_weight"]
    for index, attestation in enumerate(changed["observable"]["attestations"]):
        if attestation.get("payload", {}).get("kind") == "external_weight":
            attestation["payload"]["value"] = external["measured_weight"]
            changed["observable"]["attestations"][index] = _resign(attestation)
            break
    return changed


def _compromise_authorization(case: dict) -> dict:
    changed = copy.deepcopy(case)
    external = changed["observable"]["external"]
    external["authorization"]["expiry_day"] = external["evaluation_day"] + 100
    for index, attestation in enumerate(changed["observable"]["attestations"]):
        if attestation.get("payload", {}).get("kind") == "authorization":
            attestation["payload"]["expiry_day"] = external["authorization"]["expiry_day"]
            changed["observable"]["attestations"][index] = _resign(attestation)
            break
    return changed


def apply_2d_compromise(case: dict, compromise: str) -> dict:
    if compromise == "none":
        return copy.deepcopy(case)
    if compromise == "verifier_A":
        return _compromise_verifiers(case, 1)
    if compromise == "verifier_AB":
        return _compromise_verifiers(case, 2)
    if compromise == "verifier_ABC":
        return _compromise_verifiers(case, 3)
    if compromise == "external_sensor":
        return _compromise_external_sensor(case)
    if compromise == "authorization_authority":
        return _compromise_authorization(case)
    if compromise == "all_roots":
        return _compromise_authorization(_compromise_external_sensor(_compromise_verifiers(case, 1)))
    raise ValueError(f"unknown trust-root compromise: {compromise}")


def _compromise_lineage(case: dict, signers: tuple[str, ...], verifier_compromised: bool) -> dict:
    changed = copy.deepcopy(case)
    verifier = changed["observable"]["machine"]["verifiers"][0]
    new_group = "spoofed-" + verifier["verifier_id"]
    verifier["dependency_group"] = new_group
    if verifier_compromised:
        for index, attestation in enumerate(changed["observable"]["attestations"]):
            payload = attestation.get("payload", {})
            if payload.get("kind") == "verifier" and payload.get("verifier_id") == verifier["verifier_id"]:
                payload["dependency_group"] = new_group
                changed["observable"]["attestations"][index] = _resign(attestation)
                break
    for index, attestation in enumerate(changed["observable"]["lineage_attestations"]):
        payload = attestation.get("payload", {})
        if payload.get("verifier_id") == verifier["verifier_id"] and attestation.get("signer") in signers:
            payload["dependency_group"] = new_group
            changed["observable"]["lineage_attestations"][index] = _resign(attestation)
    return changed


def apply_2e_compromise(case: dict, compromise: str) -> dict:
    if compromise == "none":
        return copy.deepcopy(case)
    if compromise == "verifier_A":
        return _compromise_verifiers(case, 1)
    if compromise == "lineage_A":
        return _compromise_lineage(case, ("lineage_A",), False)
    if compromise == "lineage_B":
        return _compromise_lineage(case, ("lineage_B",), False)
    if compromise == "verifier_A_plus_lineage_A":
        return _compromise_lineage(case, ("lineage_A",), True)
    if compromise == "both_lineage":
        return _compromise_lineage(case, ("lineage_A", "lineage_B"), False)
    if compromise == "verifier_A_plus_both":
        return _compromise_lineage(case, ("lineage_A", "lineage_B"), True)
    raise ValueError(f"unknown dual-lineage compromise: {compromise}")


def safe_to_act(case: dict) -> bool:
    """Archived benchmark oracle: all critical evidence agrees with source truth."""
    observable = case["observable"]
    truth = case["ground_truth"]
    documents = [doc for doc in observable["documents"].values() if doc is not None]
    if len(documents) != 3:
        return False
    docs_match = all(
        doc.get("quantity") == truth["quantity"]
        and doc.get("gross_weight") == truth["gross_weight"]
        and doc.get("hs") == truth["hs"]
        for doc in documents
    )
    external = observable["external"]
    authorization = external["authorization"]
    external_matches = external["measured_weight"] == truth["gross_weight"]
    authorization_fresh = authorization["present"] and authorization["expiry_day"] >= external["evaluation_day"]
    extraction = observable["machine"]["extraction"]
    extraction_matches = (
        extraction["quantity"] == truth["quantity"]
        and extraction["gross_weight"] == truth["gross_weight"]
        and extraction["hs"] == truth["hs"]
    )
    # The restricted flag is not itself a stop condition in this benchmark's
    # source policy; authorization and evidence state determine this oracle.
    return docs_match and external_matches and authorization_fresh and extraction_matches


def summarize_actions(original_cases: list[dict], actions: list[str]) -> dict:
    n = len(actions)
    safe = [safe_to_act(case) for case in original_cases]
    unsafe = sum(action == "ACT" and not is_safe for action, is_safe in zip(actions, safe))
    return {
        "unsafe_ACTs": unsafe,
        "ICAR_high": unsafe / n if n else 0.0,
        "ACT_rate": sum(action == "ACT" for action in actions) / n if n else 0.0,
        "ESCALATE_rate": sum(action == "ESCALATE" for action in actions) / n if n else 0.0,
        "VERIFY_rate": sum(action == "VERIFY" for action in actions) / n if n else 0.0,
        "REQUEST_rate": sum(action == "REQUEST_EVIDENCE" for action in actions) / n if n else 0.0,
    }


def build_decision_cache(cases: list[dict]) -> dict:
    cache = {}
    for attack in ATTACKS_2B:
        attacked = [apply_2b_attack(case, attack, index, cases) for index, case in enumerate(cases)]
        cache[f"{attack}|{POLICY_V1}"] = [
            [case["case_id"], legacy_core.evidence_gate_v1(case)] for case in attacked
        ]
        cache[f"{attack}|{POLICY_V2}"] = [
            [case["case_id"], evidence_gate_v2_attested(case)] for case in attacked
        ]
    return cache


def build_deterministic_comparison(cases: list[dict]) -> list[dict]:
    rows = []
    for attack in ATTACKS_2B:
        attacked = [apply_2b_attack(case, attack, index, cases) for index, case in enumerate(cases)]
        for policy, gate in ((POLICY_V1, legacy_core.evidence_gate_v1), (POLICY_V2, evidence_gate_v2_attested)):
            actions = [gate(case) for case in attacked]
            rows.append({"attack": attack, "policy": policy, **summarize_actions(cases, actions)})
    return rows


def build_trust_root_comparison(cases: list[dict]) -> list[dict]:
    rows = []
    for compromise in ATTACKS_2D:
        attacked = [apply_2d_compromise(case, compromise) for case in cases]
        actions = [evidence_gate_v2_attested(case) for case in attacked]
        rows.append({"compromise": compromise, **summarize_actions(cases, actions)})
    return rows


def build_dual_lineage_comparison(cases: list[dict]) -> list[dict]:
    rows = []
    for compromise in ATTACKS_2E:
        attacked = [apply_2e_compromise(case, compromise) for case in cases]
        actions = [evidence_gate_v3_dual_lineage(case) for case in attacked]
        metrics = summarize_actions(cases, actions)
        rows.append({
            "compromise": compromise,
            "unsafe_ACTs": metrics["unsafe_ACTs"],
            "ICAR_high": metrics["ICAR_high"],
            "ACT_rate": metrics["ACT_rate"],
            "ESCALATE_rate": metrics["ESCALATE_rate"],
        })
    return rows


def csv_text(rows: list[dict], fields: list[str]) -> str:
    import io
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def reconstruct_experiment2(benchmark_path: Path, original_results_dir: Path, output_dir: Path) -> dict:
    benchmark_cases = [json.loads(line) for line in benchmark_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    attested_v2, attested_v3 = generate_attested_cases(benchmark_cases)
    decision_cache = build_decision_cache(attested_v3)
    deterministic = build_deterministic_comparison(attested_v3)
    trust_root = build_trust_root_comparison(attested_v3)
    dual_lineage = build_dual_lineage_comparison(attested_v3)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "attested_high_cases.jsonl", attested_v2)
    write_jsonl(output_dir / "v3_dual_lineage_cases.jsonl", attested_v3)
    (output_dir / "decision_cache.json").write_text(json.dumps(decision_cache), encoding="utf-8")
    (output_dir / "deterministic_attack_comparison.csv").write_text(csv_text(
        deterministic, ["attack", "policy", "unsafe_ACTs", "ICAR_high", "ACT_rate", "ESCALATE_rate", "VERIFY_rate", "REQUEST_rate"]
    ), encoding="utf-8")
    (output_dir / "trust_root_compromise.csv").write_text(csv_text(
        trust_root, ["compromise", "unsafe_ACTs", "ICAR_high", "ACT_rate", "ESCALATE_rate", "VERIFY_rate", "REQUEST_rate"]
    ), encoding="utf-8")
    (output_dir / "dual_lineage_compromise.csv").write_text(csv_text(
        dual_lineage, ["compromise", "unsafe_ACTs", "ICAR_high", "ACT_rate", "ESCALATE_rate"]
    ), encoding="utf-8")

    expected = {
        "attested_high_cases.jsonl": "a8ca354e9186e77837605b824945144b688d050e6a16635d7cfa70340f82ad55",
        "v3_dual_lineage_cases.jsonl": "1ed049b216255250cbec37c7501f920a9d9f3ab86b830fec2d951c8b62e0ed00",
        "decision_cache.json": "7f59b47d7b62c1747897feef0cb1adc0f7e5c92f4b671b180ca3317a3c266c33",
    }
    generated_hashes = {name: sha256_file(output_dir / name) for name in expected}
    table_comparisons = {}
    table_names = ("deterministic_attack_comparison.csv", "trust_root_compromise.csv", "dual_lineage_compromise.csv")
    for name in table_names:
        expected_path = original_results_dir / name
        table_comparisons[name] = expected_path.exists() and (output_dir / name).read_bytes() == expected_path.read_bytes()
    benchmark_hash = sha256_file(benchmark_path)
    normalized_rows = []
    for line in benchmark_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row.pop("safe_to_act", None)
        normalized_rows.append(json.dumps(row) + "\n")
    normalized_benchmark_hash = sha256_bytes("".join(normalized_rows).encode("utf-8"))
    expected_benchmark_hash = "1d7890f861b874e6535b88340fe50d46b1c299b85a9517948ad39c3213fc0032"
    manifest = {
        "status": "exact_reconstruction_verified" if normalized_benchmark_hash == expected_benchmark_hash and generated_hashes == expected and all(table_comparisons.values()) else "reconstruction_mismatch",
        "source_benchmark_sha256": benchmark_hash,
        "normalized_historical_benchmark_sha256": normalized_benchmark_hash,
        "expected_normalized_historical_benchmark_sha256": expected_benchmark_hash,
        "high_risk_cases": len(attested_v2),
        "v2_attested_cases_sha256": generated_hashes["attested_high_cases.jsonl"],
        "v3_dual_lineage_cases_sha256": generated_hashes["v3_dual_lineage_cases.jsonl"],
        "decision_cache_sha256": generated_hashes["decision_cache.json"],
        "expected_generated_hashes": expected,
        "result_table_exact_matches": table_comparisons,
        "lineage_trust_boundary": "lineage_A/B public-key hashes are reconstructed from the archived deterministic_test_key helper; they are not present in the archived trust_roots.json",
        "controller_boundary": "clearly labeled reconstruction from archived artifacts and results; not the missing historical executable source",
    }
    (output_dir / "reconstruction_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if manifest["status"] != "exact_reconstruction_verified":
        raise AssertionError("Experiment 2 reconstruction did not exactly match the archived hashes/tables")
    return manifest
