"""Dependency-ancestry-aware witness verification for the v5 synthetic study."""
from __future__ import annotations

import base64
from itertools import combinations
from typing import Iterable, MutableSet

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from src.provenance import canonical_bytes, canonical_sha256
from src.evidence_provenance_v4 import (
    issue_source_credential, verify_source_credential,
    issue_claim_evidence, verify_claim_evidence,
)

GRAPH_SCHEMA = "ega-dependency-graph-v5"


def issue_dependency_graph(*, graph_id: str, version: str, tenant_id: str,
                           nodes: dict[str, Iterable[str]], issued_at: int,
                           expires_at: int, signer_private_key: Ed25519PrivateKey) -> dict:
    if expires_at <= issued_at or not graph_id or not version or not tenant_id:
        raise ValueError("invalid graph identity or validity interval")
    normalized = {node: sorted(set(parents)) for node, parents in sorted(nodes.items())}
    body = {
        "schema": GRAPH_SCHEMA, "graph_id": graph_id, "version": version,
        "tenant_id": tenant_id, "nodes": normalized,
        "graph_digest": canonical_sha256(normalized),
        "issued_at": issued_at, "expires_at": expires_at,
    }
    return {
        "body": body,
        "signature_b64": base64.b64encode(signer_private_key.sign(canonical_bytes(body))).decode("ascii"),
    }


def resolve_ancestors(nodes: dict[str, list[str]], leaf: str) -> frozenset[str]:
    """Return transitive ancestors; reject missing nodes and dependency cycles."""
    if leaf not in nodes:
        raise ValueError("dependency_leaf_missing")
    visiting: set[str] = set()
    memo: dict[str, set[str]] = {}

    def walk(node: str) -> set[str]:
        if node in visiting:
            raise ValueError("dependency_cycle")
        if node in memo:
            return memo[node]
        if node not in nodes or not isinstance(nodes[node], list):
            raise ValueError("dependency_node_missing_or_malformed")
        visiting.add(node)
        result: set[str] = set()
        for parent in nodes[node]:
            if parent not in nodes:
                raise ValueError("dependency_parent_unresolved")
            result.add(parent)
            result.update(walk(parent))
        visiting.remove(node)
        memo[node] = result
        return result

    return frozenset(walk(leaf))


def verify_dependency_graph(graph_record: dict, *, trusted_registry_key: Ed25519PublicKey,
                            tenant_id: str, now: int) -> tuple[bool, str, dict | None]:
    try:
        body = graph_record["body"]
        if body.get("schema") != GRAPH_SCHEMA:
            return False, "unsupported_dependency_graph_schema", None
        if body.get("tenant_id") != tenant_id:
            return False, "dependency_graph_tenant_mismatch", None
        if not isinstance(now, int) or now < body["issued_at"] or now >= body["expires_at"]:
            return False, "dependency_graph_expired_or_not_yet_valid", None
        nodes = body["nodes"]
        if not isinstance(nodes, dict) or not nodes:
            return False, "dependency_graph_empty_or_malformed", None
        if body.get("graph_digest") != canonical_sha256(nodes):
            return False, "dependency_graph_digest_mismatch", None
        signature = base64.b64decode(graph_record["signature_b64"], validate=True)
        trusted_registry_key.verify(signature, canonical_bytes(body))
        for leaf in nodes:
            resolve_ancestors(nodes, leaf)
        return True, "valid_dependency_graph", body
    except ValueError as exc:
        reason = str(exc)
        if reason in {"dependency_cycle", "dependency_parent_unresolved",
                      "dependency_leaf_missing", "dependency_node_missing_or_malformed"}:
            return False, reason, None
        return False, "invalid_dependency_graph", None
    except (KeyError, TypeError, InvalidSignature):
        return False, "invalid_dependency_graph_signature_or_schema", None


def issue_graph_bound_source_credential(*, graph_digest: str, dependency_leaf_node: str,
                                        dependency_manifest_complete: bool = True,
                                        issuer_private_key: Ed25519PrivateKey, **credential_args) -> dict:
    """Issue a normal v4 source credential extended with signed graph binding."""
    credential = issue_source_credential(
        issuer_private_key=issuer_private_key, **credential_args)
    body = credential["body"]
    body["dependency_graph_digest"] = graph_digest
    body["dependency_leaf_node"] = dependency_leaf_node
    body["dependency_manifest_complete"] = bool(dependency_manifest_complete)
    credential["signature_b64"] = base64.b64encode(
        issuer_private_key.sign(canonical_bytes(body))).decode("ascii")
    return credential


def evaluate_quorum(records: Iterable[tuple[dict, dict]], *, policy: str, threshold: int,
                    trusted_registry_key: Ed25519PublicKey, tenant_id: str,
                    graph_record: dict | None, claim_type: str, expected_value,
                    expected_unit: str, expected_subject_id: str, expected_action_id: str,
                    expected_action_payload_digest: str, expected_document_digest: str,
                    now: int, tolerance: float = 0.0,
                    consumed_nonces: MutableSet[str] | None = None,
                    last_sequences: dict[str, int] | None = None
                    ) -> tuple[bool, str, list[dict]]:
    """Evaluate a matching witness subset under key, field, or graph independence."""
    if policy not in {"key_unique", "field_distinct", "graph_aware"}:
        return False, "unknown_independence_policy", []
    supplied = list(records)
    if threshold < 1 or threshold > len(supplied):
        return False, "invalid_quorum_threshold", []

    graph_body = None
    if policy == "graph_aware":
        if graph_record is None:
            return False, "dependency_graph_missing", []
        graph_ok, graph_reason, graph_body = verify_dependency_graph(
            graph_record, trusted_registry_key=trusted_registry_key,
            tenant_id=tenant_id, now=now)
        if not graph_ok:
            return False, graph_reason, []

    verified = []
    nonces = consumed_nonces if consumed_nonces is not None else set()
    sequences = last_sequences if last_sequences is not None else {}
    for record, credential in supplied:
        ok, reason, identity, _ = verify_source_credential(
            credential, trusted_issuer_key=trusted_registry_key,
            tenant_id=tenant_id, now=now)
        if not ok:
            return False, reason, []
        ancestors = frozenset()
        if policy == "graph_aware":
            if not identity.get("dependency_manifest_complete", False):
                return False, "dependency_manifest_incomplete", []
            if identity.get("dependency_graph_digest") != graph_body["graph_digest"]:
                return False, "dependency_graph_binding_mismatch", []
            leaf = identity.get("dependency_leaf_node")
            try:
                ancestors = resolve_ancestors(graph_body["nodes"], leaf)
            except (ValueError, TypeError):
                return False, "dependency_ancestry_unresolvable", []
        ok, reason, evidence = verify_claim_evidence(
            record, credential, trusted_issuer_key=trusted_registry_key,
            tenant_id=tenant_id, expected_claim=claim_type,
            expected_subject_id=expected_subject_id, expected_action_id=expected_action_id,
            expected_action_payload_digest=expected_action_payload_digest,
            expected_document_digest=expected_document_digest, expected_unit=expected_unit,
            now=now, consumed_nonces=nonces, last_sequences=sequences)
        if not ok:
            return False, reason, []
        evidence["dependency_leaf_node"] = identity.get("dependency_leaf_node")
        evidence["dependency_ancestors"] = sorted(ancestors)
        verified.append(evidence)

    def agrees(value):
        if isinstance(expected_value, (int, float)) and not isinstance(expected_value, bool):
            return isinstance(value, (int, float)) and not isinstance(value, bool) and abs(float(value) - float(expected_value)) <= tolerance
        return value == expected_value

    matching = [item for item in verified
                if item["claim_type"] == claim_type and item["unit"] == expected_unit
                and agrees(item["value"])]
    if len(matching) < threshold:
        return False, "quorum_disagreement", verified

    key_fields = ("source_id", "key_id")
    field_fields = ("source_id", "key_id", "acquisition_domain",
                    "administrative_domain", "gateway_id", "key_admin_domain")
    fields = key_fields if policy == "key_unique" else field_fields
    had_directly_independent_subset = False
    shared_ancestor = None
    for subset in combinations(matching, threshold):
        if not all(len({item[field] for item in subset}) == threshold for field in fields):
            continue
        had_directly_independent_subset = True
        if policy != "graph_aware":
            return True, "quorum_valid", list(subset)
        for left, right in combinations(subset, 2):
            shared = set(left["dependency_ancestors"]) & set(right["dependency_ancestors"])
            if shared:
                shared_ancestor = sorted(shared)[0]
                break
        else:
            return True, "quorum_valid", list(subset)

    if policy == "graph_aware" and had_directly_independent_subset and shared_ancestor:
        return False, "shared_dependency_graph:" + shared_ancestor, verified
    return False, "insufficient_identity_independence", verified
