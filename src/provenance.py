"""Cryptographic provenance primitives for synthetic research experiments.

Production callers must obtain keys from an external KMS/HSM or equivalent
trusted key-management system. This module never creates production keys.
"""
from __future__ import annotations

import base64
import hashlib
import json
from typing import Mapping, MutableSet

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def canonical_bytes(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_sha256(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def public_key_bytes(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def create_document_root_attestation(
    *,
    signer_id: str,
    key_id: str,
    tenant_id: str,
    case_id: str,
    document_instances: list,
    normalized_documents: dict,
    private_key: Ed25519PrivateKey,
    issued_at: int,
    expires_at: int,
    nonce: str,
) -> dict:
    """Sign the raw-instance list AND normalized document map.

    The signature binds the tenant, case, key identity, validity window and
    nonce as well as both document representations. Timestamps and nonce
    uniqueness must be supplied by the caller.
    """
    if not all(isinstance(x, str) and x for x in (signer_id, key_id, tenant_id, case_id, nonce)):
        raise ValueError("signer_id, key_id, tenant_id, case_id and nonce must be non-empty strings")
    if (
        isinstance(issued_at, bool) or not isinstance(issued_at, int)
        or isinstance(expires_at, bool) or not isinstance(expires_at, int)
        or expires_at <= issued_at
    ):
        raise ValueError("expires_at must be an integer later than issued_at")
    payload = {
        "schema": "ega-document-root-attestation-v1",
        "signer_id": signer_id,
        "key_id": key_id,
        "tenant_id": tenant_id,
        "case_id": case_id,
        "document_instances_sha256": canonical_sha256(document_instances),
        "normalized_documents_sha256": canonical_sha256(normalized_documents),
        "issued_at": issued_at,
        "expires_at": expires_at,
        "nonce": nonce,
    }
    signature = private_key.sign(canonical_bytes(payload))
    return {
        "payload": payload,
        "signature_b64": base64.b64encode(signature).decode("ascii"),
    }


def verify_document_root_attestation(
    attestation: dict,
    *,
    trusted_keys: Mapping[str, Ed25519PublicKey],
    trusted_signers: Mapping[str, str],
    revoked_key_ids: set[str] | frozenset[str] = frozenset(),
    expected_tenant_id: str,
    expected_case_id: str,
    document_instances: list,
    normalized_documents: dict,
    now: int,
    consumed_nonces: MutableSet[str] | None = None,
) -> tuple[bool, str]:
    """Verify trust, scope, freshness, content binding and optional replay state.

    A nonce is consumed only after every cryptographic and semantic check
    succeeds. The caller must persist replay state atomically in production.
    """
    try:
        payload = attestation["payload"]
        key_id = payload["key_id"]
        if payload.get("schema") != "ega-document-root-attestation-v1":
            return False, "unsupported_schema"
        if key_id in revoked_key_ids:
            return False, "revoked_key"
        public_key = trusted_keys.get(key_id)
        if public_key is None:
            return False, "untrusted_key"
        signer_id = payload.get("signer_id")
        if not isinstance(signer_id, str) or not signer_id:
            return False, "invalid_attestation"
        authorized_signer = trusted_signers.get(key_id)
        if authorized_signer is None:
            return False, "untrusted_signer"
        if signer_id != authorized_signer:
            return False, "signer_identity_mismatch"
        if payload.get("tenant_id") != expected_tenant_id:
            return False, "tenant_mismatch"
        if payload.get("case_id") != expected_case_id:
            return False, "case_mismatch"
        issued_at = payload.get("issued_at")
        expires_at = payload.get("expires_at")
        if (
            isinstance(now, bool) or not isinstance(now, int)
            or isinstance(issued_at, bool) or not isinstance(issued_at, int)
            or isinstance(expires_at, bool) or not isinstance(expires_at, int)
            or now < issued_at or now >= expires_at or expires_at <= issued_at
        ):
            return False, "expired_or_not_yet_valid"
        if payload.get("document_instances_sha256") != canonical_sha256(document_instances):
            return False, "document_instances_mismatch"
        if payload.get("normalized_documents_sha256") != canonical_sha256(normalized_documents):
            return False, "normalized_documents_mismatch"
        nonce = payload["nonce"]
        if not isinstance(nonce, str) or not nonce:
            return False, "invalid_attestation"
        signature = base64.b64decode(attestation["signature_b64"], validate=True)
        public_key.verify(signature, canonical_bytes(payload))
        if consumed_nonces is not None and nonce in consumed_nonces:
            return False, "replay"
        if consumed_nonces is not None:
            consumed_nonces.add(nonce)
        return True, "valid"
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_attestation"


# Legacy component-attestation helpers retained for reconstruction v1/v2.
def deterministic_test_key(name):
    """Synthetic reproducibility key only. Never use in production."""
    seed = hashlib.sha256(("exp2-seed-42|" + name).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def sign(signer_name, payload):
    sk = deterministic_test_key(signer_name)
    sig = sk.sign(canonical_bytes(payload))
    return {
        "signer": signer_name,
        "payload": payload,
        "signature_b64": base64.b64encode(sig).decode(),
    }


def verify(attestation, trusted_names):
    signer = attestation.get("signer")
    if signer not in trusted_names:
        return False
    pk = deterministic_test_key(signer).public_key()
    try:
        pk.verify(
            base64.b64decode(attestation["signature_b64"], validate=True),
            canonical_bytes(attestation["payload"]),
        )
        return True
    except Exception:
        return False
