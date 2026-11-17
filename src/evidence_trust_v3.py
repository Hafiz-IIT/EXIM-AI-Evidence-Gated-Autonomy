"""Synthetic v3: quorum witnesses with registry-authenticated source identities.

All keys and identities are deterministic test fixtures. This is not production
PKI, KMS/HSM, or evidence of real-world administrative independence.
"""
from __future__ import annotations

import base64
from typing import Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from src.provenance import canonical_bytes, canonical_sha256

CREDENTIAL_SCHEMA = "ega-witness-identity-credential-v3"
ASSERTION_SCHEMA = "ega-witness-assertion-v3"


def raw_public_key(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def issue_identity_credential(*, issuer_id: str, witness_id: str, key_id: str,
                              public_key: Ed25519PublicKey, source_id: str,
                              acquisition_domain: str, administrative_domain: str,
                              tenant_id: str, serial: str, issued_at: int,
                              expires_at: int, issuer_private_key: Ed25519PrivateKey) -> dict:
    """Issue a root-signed binding between a witness identity and its public key."""
    required = (issuer_id, witness_id, key_id, source_id, acquisition_domain,
                administrative_domain, tenant_id, serial)
    if not all(isinstance(value, str) and value for value in required):
        raise ValueError("credential identity and scope fields must be non-empty")
    if not isinstance(issued_at, int) or not isinstance(expires_at, int) or expires_at <= issued_at:
        raise ValueError("invalid credential validity window")
    body = {
        "schema": CREDENTIAL_SCHEMA, "issuer_id": issuer_id,
        "witness_id": witness_id, "key_id": key_id,
        "public_key_b64": base64.b64encode(raw_public_key(public_key)).decode("ascii"),
        "source_id": source_id, "acquisition_domain": acquisition_domain,
        "administrative_domain": administrative_domain, "tenant_id": tenant_id,
        "serial": serial, "issued_at": issued_at, "expires_at": expires_at,
    }
    return {"body": body, "signature_b64": base64.b64encode(
        issuer_private_key.sign(canonical_bytes(body))).decode("ascii")}


def verify_identity_credential(credential: dict, *, trusted_issuer_key: Ed25519PublicKey,
                               expected_tenant_id: str, now: int,
                               revoked_serials: frozenset[str] = frozenset()
                               ) -> tuple[bool, str, Ed25519PublicKey | None]:
    try:
        body = credential["body"]
        if body.get("schema") != CREDENTIAL_SCHEMA:
            return False, "unsupported_credential_schema", None
        if body.get("tenant_id") != expected_tenant_id:
            return False, "credential_tenant_mismatch", None
        if body.get("serial") in revoked_serials:
            return False, "credential_revoked", None
        if not isinstance(now, int) or now < body["issued_at"] or now >= body["expires_at"]:
            return False, "credential_expired_or_not_yet_valid", None
        signature = base64.b64decode(credential["signature_b64"], validate=True)
        trusted_issuer_key.verify(signature, canonical_bytes(body))
        public_bytes = base64.b64decode(body["public_key_b64"], validate=True)
        return True, "valid_credential", Ed25519PublicKey.from_public_bytes(public_bytes)
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_identity_credential", None


def issue_witness_assertion(*, credential: dict, witness_private_key: Ed25519PrivateKey,
                            tenant_id: str, case_id: str, parent_digest: str,
                            gross_weight: float, item_type: str, nonce: str,
                            issued_at: int, expires_at: int) -> dict:
    body = credential["body"]
    if not all(isinstance(x, str) and x for x in (tenant_id, case_id, parent_digest, nonce, item_type)):
        raise ValueError("assertion scope and nonce fields must be non-empty")
    if not isinstance(issued_at, int) or not isinstance(expires_at, int) or expires_at <= issued_at:
        raise ValueError("invalid assertion validity window")
    envelope = {
        "schema": ASSERTION_SCHEMA, "credential_digest": canonical_sha256(body),
        "witness_id": body["witness_id"], "key_id": body["key_id"],
        "tenant_id": tenant_id, "case_id": case_id, "parent_digest": parent_digest,
        "gross_weight": float(gross_weight), "item_type": item_type,
        "nonce": nonce, "issued_at": issued_at, "expires_at": expires_at,
    }
    return {"envelope": envelope, "signature_b64": base64.b64encode(
        witness_private_key.sign(canonical_bytes(envelope))).decode("ascii")}


def verify_witness_assertion(record: dict, credential: dict, *,
                             trusted_issuer_key: Ed25519PublicKey,
                             tenant_id: str, case_id: str, parent_digest: str,
                             now: int, revoked_serials: frozenset[str] = frozenset()
                             ) -> tuple[bool, str, dict | None]:
    try:
        valid, reason, public_key = verify_identity_credential(
            credential, trusted_issuer_key=trusted_issuer_key,
            expected_tenant_id=tenant_id, now=now, revoked_serials=revoked_serials)
        if not valid:
            return False, reason, None
        envelope = record["envelope"]
        body = credential["body"]
        if envelope.get("schema") != ASSERTION_SCHEMA:
            return False, "unsupported_assertion_schema", None
        if envelope.get("credential_digest") != canonical_sha256(body):
            return False, "credential_binding_mismatch", None
        if envelope.get("witness_id") != body["witness_id"] or envelope.get("key_id") != body["key_id"]:
            return False, "signer_identity_mismatch", None
        if envelope.get("tenant_id") != tenant_id or envelope.get("case_id") != case_id:
            return False, "assertion_scope_mismatch", None
        if envelope.get("parent_digest") != parent_digest:
            return False, "assertion_parent_mismatch", None
        if not isinstance(now, int) or now < envelope["issued_at"] or now >= envelope["expires_at"]:
            return False, "assertion_expired_or_not_yet_valid", None
        signature = base64.b64decode(record["signature_b64"], validate=True)
        public_key.verify(signature, canonical_bytes(envelope))
        return True, "valid", body
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_witness_assertion", None


def verify_witness_quorum(items: Iterable[tuple[dict, dict]], *,
                          trusted_issuer_key: Ed25519PublicKey,
                          tenant_id: str, case_id: str, parent_digest: str,
                          expected_weight: float, expected_item_type: str,
                          now: int, threshold: int = 2, total_required: int = 3,
                          revoked_serials: frozenset[str] = frozenset()) -> tuple[bool, str, int]:
    """Require a matching threshold whose *supporters* are independently enrolled."""
    if (not isinstance(threshold, int) or isinstance(threshold, bool)
            or not isinstance(total_required, int) or isinstance(total_required, bool)
            or threshold < 1 or total_required < threshold):
        return False, "invalid_quorum_configuration", 0

    supplied = list(items)
    # The configured witness roster must be present and distinct. Invalid
    # credentials may still be tolerated up to the threshold boundary.
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
        valid, _, identity = verify_witness_assertion(
            record, credential, trusted_issuer_key=trusted_issuer_key,
            tenant_id=tenant_id, case_id=case_id, parent_digest=parent_digest,
            now=now, revoked_serials=revoked_serials)
        if valid:
            accepted.append((record["envelope"], identity))

    # A quorum is a group of assertions that agree on the complete measurement.
    # Independence must be checked within that matching group, not across all
    # valid witnesses (a dissenting third witness cannot lend independence to
    # two colluding supporters).
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
    for supporters in matching_groups.values():
        if len(supporters) < threshold:
            continue
        independent_fields = (
            "witness_id", "key_id", "source_id",
            "acquisition_domain", "administrative_domain",
        )
        failed_field = next(
            (field for field in independent_fields
             if len({identity[field] for identity in supporters}) < threshold),
            None,
        )
        if failed_field is None:
            return True, "quorum_valid", len(supporters)
        return False, "insufficient_identity_independence:" + failed_field, 0

    return False, "quorum_disagreement", matching_count
