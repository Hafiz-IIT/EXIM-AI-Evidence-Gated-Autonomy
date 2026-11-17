"""Synthetic four-authority evidence attestations for EGA architecture v2.

This module models role-separated Ed25519 attestations. Deterministic experiment
keys are supplied by callers; this is not production key management.
"""
from __future__ import annotations

import base64
from typing import Mapping, MutableSet

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from src.provenance import canonical_bytes, canonical_sha256

ROLES = ("capture", "interpretation", "witness", "authorization")
SCHEMA = "ega-evidence-trust-v2"


def create_attestation(*, role: str, key_id: str, tenant_id: str, case_id: str,
                       parent_digest: str, payload: dict,
                       private_key: Ed25519PrivateKey, issued_at: int,
                       expires_at: int, nonce: str) -> dict:
    """Create one role-scoped signed envelope with an explicit parent reference."""
    if role not in ROLES:
        raise ValueError("unknown authority role")
    if not all(isinstance(x, str) and x for x in
               (key_id, tenant_id, case_id, parent_digest, nonce)):
        raise ValueError("key, scope, parent digest and nonce must be non-empty")
    if not isinstance(issued_at, int) or not isinstance(expires_at, int) or expires_at <= issued_at:
        raise ValueError("invalid attestation validity window")
    envelope = {
        "schema": SCHEMA, "role": role, "key_id": key_id,
        "tenant_id": tenant_id, "case_id": case_id,
        "parent_digest": parent_digest, "payload": payload,
        "issued_at": issued_at, "expires_at": expires_at, "nonce": nonce,
    }
    signature = private_key.sign(canonical_bytes(envelope))
    return {"envelope": envelope, "signature_b64": base64.b64encode(signature).decode("ascii")}


def verify_attestation(record: dict, *, expected_role: str,
                       trusted_keys: Mapping[str, Ed25519PublicKey],
                       tenant_id: str, case_id: str, parent_digest: str,
                       now: int, revoked_key_ids=frozenset(),
                       consumed_nonces: MutableSet[str] | None = None) -> tuple[bool, str]:
    """Verify signature, role, scope, parent, validity, revocation and replay."""
    try:
        envelope = record["envelope"]
        key_id = envelope["key_id"]
        if envelope.get("schema") != SCHEMA:
            return False, "unsupported_schema"
        if envelope.get("role") != expected_role:
            return False, "role_mismatch"
        if key_id in revoked_key_ids:
            return False, "revoked_key"
        key = trusted_keys.get(key_id)
        if key is None:
            return False, "untrusted_key"
        if envelope.get("tenant_id") != tenant_id:
            return False, "tenant_mismatch"
        if envelope.get("case_id") != case_id:
            return False, "case_mismatch"
        if envelope.get("parent_digest") != parent_digest:
            return False, "parent_mismatch"
        if not isinstance(now, int) or now < envelope["issued_at"] or now >= envelope["expires_at"]:
            return False, "expired_or_not_yet_valid"
        nonce = envelope["nonce"]
        if consumed_nonces is not None and nonce in consumed_nonces:
            return False, "replay"
        signature = base64.b64decode(record["signature_b64"], validate=True)
        key.verify(signature, canonical_bytes(envelope))
        if consumed_nonces is not None:
            consumed_nonces.add(nonce)
        return True, "valid"
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_attestation"


def evidence_graph_digest(capture: dict, interpretation: dict, witness: dict) -> str:
    """Stable digest binding the three upstream attestations for AA."""
    return canonical_sha256({
        "capture": capture["envelope"],
        "interpretation": interpretation["envelope"],
        "witness": witness["envelope"],
    })
