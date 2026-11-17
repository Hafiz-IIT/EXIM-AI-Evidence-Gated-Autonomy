"""Synthetic v4: witness quorum with explicit dependency-root independence.

Dependency roots are registry-signed claims. They make declared common causes
machine-checkable; they do not prove that the declarations are true.
"""
from __future__ import annotations

import base64
from itertools import combinations
from typing import Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from src.provenance import canonical_bytes, canonical_sha256
from src.evidence_trust_v3 import issue_witness_assertion

CREDENTIAL_SCHEMA_V4 = "ega-witness-identity-credential-v4"
ASSERTION_SCHEMA = "ega-witness-assertion-v3"
DEPENDENCY_LAYERS = (
    "parent_control",
    "identity_provider",
    "key_management",
    "acquisition_pipeline",
    "measurement_source",
)


def _raw_public_key(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def issue_identity_credential_v4(*, issuer_id: str, witness_id: str, key_id: str,
                                 public_key: Ed25519PublicKey, source_id: str,
                                 acquisition_domain: str, administrative_domain: str,
                                 tenant_id: str, dependency_roots: dict[str, list[str]],
                                 serial: str, issued_at: int, expires_at: int,
                                 issuer_private_key: Ed25519PrivateKey) -> dict:
    """Issue a registry-signed identity credential with declared dependency roots."""
    required = (issuer_id, witness_id, key_id, source_id, acquisition_domain,
                administrative_domain, tenant_id, serial)
    if not all(isinstance(value, str) and value for value in required):
        raise ValueError("credential identity and scope fields must be non-empty")
    if not isinstance(issued_at, int) or not isinstance(expires_at, int) or expires_at <= issued_at:
        raise ValueError("invalid credential validity window")
    if not isinstance(dependency_roots, dict) or set(dependency_roots) != set(DEPENDENCY_LAYERS):
        raise ValueError("dependency_roots must declare every required dependency layer")
    normalized_roots = {}
    for layer in DEPENDENCY_LAYERS:
        values = dependency_roots[layer]
        if (not isinstance(values, list) or not values
                or not all(isinstance(value, str) and value for value in values)):
            raise ValueError(f"dependency layer {layer} must contain non-empty identifiers")
        normalized_roots[layer] = sorted(set(values))
    body = {
        "schema": CREDENTIAL_SCHEMA_V4,
        "issuer_id": issuer_id,
        "witness_id": witness_id,
        "key_id": key_id,
        "public_key_b64": base64.b64encode(_raw_public_key(public_key)).decode("ascii"),
        "source_id": source_id,
        "acquisition_domain": acquisition_domain,
        "administrative_domain": administrative_domain,
        "tenant_id": tenant_id,
        "dependency_roots": normalized_roots,
        "serial": serial,
        "issued_at": issued_at,
        "expires_at": expires_at,
    }
    return {
        "body": body,
        "signature_b64": base64.b64encode(
            issuer_private_key.sign(canonical_bytes(body))
        ).decode("ascii"),
    }


def verify_identity_credential_v4(credential: dict, *, trusted_issuer_key: Ed25519PublicKey,
                                  expected_tenant_id: str, now: int,
                                  revoked_serials: frozenset[str] = frozenset()
                                  ) -> tuple[bool, str, Ed25519PublicKey | None, dict | None]:
    try:
        body = credential["body"]
        if body.get("schema") != CREDENTIAL_SCHEMA_V4:
            return False, "unsupported_credential_schema", None, None
        if body.get("tenant_id") != expected_tenant_id:
            return False, "credential_tenant_mismatch", None, None
        if body.get("serial") in revoked_serials:
            return False, "credential_revoked", None, None
        if not isinstance(now, int) or now < body["issued_at"] or now >= body["expires_at"]:
            return False, "credential_expired_or_not_yet_valid", None, None
        roots = body.get("dependency_roots")
        if not isinstance(roots, dict) or set(roots) != set(DEPENDENCY_LAYERS):
            return False, "dependency_roots_incomplete", None, None
        for layer in DEPENDENCY_LAYERS:
            values = roots.get(layer)
            if (not isinstance(values, list) or not values
                    or values != sorted(set(values))
                    or not all(isinstance(value, str) and value for value in values)):
                return False, "dependency_roots_invalid:" + layer, None, None
        signature = base64.b64decode(credential["signature_b64"], validate=True)
        trusted_issuer_key.verify(signature, canonical_bytes(body))
        public_bytes = base64.b64decode(body["public_key_b64"], validate=True)
        return True, "valid_credential", Ed25519PublicKey.from_public_bytes(public_bytes), body
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_identity_credential", None, None


def verify_witness_assertion_v4(record: dict, credential: dict, *,
                                trusted_issuer_key: Ed25519PublicKey,
                                tenant_id: str, case_id: str, parent_digest: str,
                                now: int,
                                revoked_serials: frozenset[str] = frozenset()
                                ) -> tuple[bool, str, dict | None]:
    try:
        valid, reason, public_key, identity = verify_identity_credential_v4(
            credential, trusted_issuer_key=trusted_issuer_key,
            expected_tenant_id=tenant_id, now=now, revoked_serials=revoked_serials)
        if not valid:
            return False, reason, None
        envelope = record["envelope"]
        if envelope.get("schema") != ASSERTION_SCHEMA:
            return False, "unsupported_assertion_schema", None
        if envelope.get("credential_digest") != canonical_sha256(identity):
            return False, "credential_binding_mismatch", None
        if envelope.get("witness_id") != identity["witness_id"] or envelope.get("key_id") != identity["key_id"]:
            return False, "signer_identity_mismatch", None
        if envelope.get("tenant_id") != tenant_id or envelope.get("case_id") != case_id:
            return False, "assertion_scope_mismatch", None
        if envelope.get("parent_digest") != parent_digest:
            return False, "assertion_parent_mismatch", None
        if not isinstance(now, int) or now < envelope["issued_at"] or now >= envelope["expires_at"]:
            return False, "assertion_expired_or_not_yet_valid", None
        signature = base64.b64decode(record["signature_b64"], validate=True)
        public_key.verify(signature, canonical_bytes(envelope))
        return True, "valid", identity
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_witness_assertion", None


def _subset_independence_reason(supporters: tuple[dict, ...], *, dependency_aware: bool) -> str | None:
    independent_fields = (
        "witness_id", "key_id", "source_id",
        "acquisition_domain", "administrative_domain",
    )
    for field in independent_fields:
        if len({identity[field] for identity in supporters}) != len(supporters):
            return "shared_identity_field:" + field
    if dependency_aware:
        for layer in DEPENDENCY_LAYERS:
            roots = [set(identity["dependency_roots"][layer]) for identity in supporters]
            for left in range(len(roots)):
                for right in range(left + 1, len(roots)):
                    if roots[left] & roots[right]:
                        return "shared_dependency:" + layer
    return None


def verify_witness_quorum_v4(items: Iterable[tuple[dict, dict]], *,
                             trusted_issuer_key: Ed25519PublicKey,
                             tenant_id: str, case_id: str, parent_digest: str,
                             expected_weight: float, expected_item_type: str,
                             now: int, threshold: int = 2, total_required: int = 3,
                             dependency_aware: bool = True,
                             revoked_serials: frozenset[str] = frozenset()
                             ) -> tuple[bool, str, int]:
    """Find a matching quorum subset with pairwise-disjoint declared dependency roots."""
    if (not isinstance(threshold, int) or isinstance(threshold, bool)
            or not isinstance(total_required, int) or isinstance(total_required, bool)
            or threshold < 1 or total_required < threshold):
        return False, "invalid_quorum_configuration", 0
    supplied = list(items)
    roster_ids = set()
    for _, credential in supplied:
        try:
            witness_id = credential["body"]["witness_id"]
        except (KeyError, TypeError):
            continue
        if isinstance(witness_id, str) and witness_id:
            roster_ids.add(witness_id)
    if len(roster_ids) != total_required:
        return False, "incomplete_or_duplicate_witness_roster", 0

    accepted = []
    for record, credential in supplied:
        valid, _, identity = verify_witness_assertion_v4(
            record, credential, trusted_issuer_key=trusted_issuer_key,
            tenant_id=tenant_id, case_id=case_id, parent_digest=parent_digest,
            now=now, revoked_serials=revoked_serials)
        if valid:
            accepted.append((record["envelope"], identity))
    if len(accepted) < threshold:
        return False, "insufficient_valid_witnesses", 0

    matching_groups = {}
    for envelope, identity in accepted:
        try:
            measurement = (float(envelope["gross_weight"]), envelope["item_type"])
        except (KeyError, TypeError, ValueError):
            continue
        if (abs(measurement[0] - float(expected_weight)) < 1e-9
                and measurement[1] == expected_item_type):
            matching_groups.setdefault(measurement, []).append(identity)

    matching_count = max((len(group) for group in matching_groups.values()), default=0)
    if matching_count < threshold:
        return False, "quorum_disagreement", matching_count

    last_reason = "insufficient_identity_independence"
    for supporters in matching_groups.values():
        for subset in combinations(supporters, threshold):
            reason = _subset_independence_reason(subset, dependency_aware=dependency_aware)
            if reason is None:
                return True, "quorum_valid", threshold
            last_reason = reason
    return False, last_reason, 0
