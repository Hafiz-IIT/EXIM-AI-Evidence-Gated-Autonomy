"""Claim-scoped, action-bound evidence verification for synthetic v4 experiments.

This is a research prototype. It does not implement production PKI, hardware
attestation, secure acquisition, calibration authorities, or atomic commit.
"""
from __future__ import annotations

import base64
from typing import Iterable, Mapping, MutableSet

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from src.provenance import canonical_bytes, canonical_sha256

CREDENTIAL_SCHEMA = "ega-source-credential-v4"
EVIDENCE_SCHEMA = "ega-claim-evidence-v4"
ACTION_SCHEMA = "ega-action-binding-v4"


def _pubkey_bytes(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def issue_source_credential(*, issuer_id: str, source_id: str, source_type: str,
                            key_id: str, public_key: Ed25519PublicKey,
                            allowed_claims: Iterable[str], acquisition_domain: str,
                            administrative_domain: str, gateway_id: str,
                            key_admin_domain: str, tenant_id: str, serial: str,
                            issued_at: int, expires_at: int,
                            issuer_private_key: Ed25519PrivateKey) -> dict:
    fields = (issuer_id, source_id, source_type, key_id, acquisition_domain,
              administrative_domain, gateway_id, key_admin_domain, tenant_id, serial)
    claims = sorted(set(allowed_claims))
    if not all(isinstance(v, str) and v for v in fields) or not claims:
        raise ValueError("source identity and allowed claims must be non-empty")
    if not isinstance(issued_at, int) or not isinstance(expires_at, int) or expires_at <= issued_at:
        raise ValueError("invalid credential validity window")
    body = {
        "schema": CREDENTIAL_SCHEMA, "issuer_id": issuer_id,
        "source_id": source_id, "source_type": source_type, "key_id": key_id,
        "public_key_b64": base64.b64encode(_pubkey_bytes(public_key)).decode("ascii"),
        "allowed_claims": claims, "acquisition_domain": acquisition_domain,
        "administrative_domain": administrative_domain, "gateway_id": gateway_id,
        "key_admin_domain": key_admin_domain, "tenant_id": tenant_id,
        "serial": serial, "issued_at": issued_at, "expires_at": expires_at,
    }
    return {"body": body, "signature_b64": base64.b64encode(
        issuer_private_key.sign(canonical_bytes(body))).decode("ascii")}


def verify_source_credential(credential: dict, *, trusted_issuer_key: Ed25519PublicKey,
                             tenant_id: str, now: int,
                             revoked_serials: frozenset[str] = frozenset()
                             ) -> tuple[bool, str, dict | None, Ed25519PublicKey | None]:
    try:
        body = credential["body"]
        if body.get("schema") != CREDENTIAL_SCHEMA:
            return False, "unsupported_credential_schema", None, None
        if body.get("tenant_id") != tenant_id:
            return False, "credential_tenant_mismatch", None, None
        if body.get("serial") in revoked_serials:
            return False, "credential_revoked", None, None
        if not isinstance(now, int) or now < body["issued_at"] or now >= body["expires_at"]:
            return False, "credential_expired_or_not_yet_valid", None, None
        signature = base64.b64decode(credential["signature_b64"], validate=True)
        trusted_issuer_key.verify(signature, canonical_bytes(body))
        public_bytes = base64.b64decode(body["public_key_b64"], validate=True)
        return True, "valid_credential", body, Ed25519PublicKey.from_public_bytes(public_bytes)
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_source_credential", None, None


def issue_claim_evidence(*, credential: dict, source_private_key: Ed25519PrivateKey,
                         claim_type: str, value, unit: str, subject_id: str,
                         action_id: str, action_payload_digest: str, document_digest: str, input_digest: str,
                         output_digest: str, transformation_id: str, tool_version: str,
                         observed_at: int, issued_at: int, expires_at: int,
                         sequence_number: int, nonce: str,
                         calibration_id: str = "", calibration_valid_until: int = 0) -> dict:
    identity = credential["body"]
    required = (claim_type, subject_id, action_id, action_payload_digest, document_digest, input_digest,
                output_digest, transformation_id, tool_version, nonce)
    if not all(isinstance(v, str) and v for v in required):
        raise ValueError("claim, scope, digest and transformation fields must be non-empty")
    if not isinstance(issued_at, int) or not isinstance(expires_at, int) or expires_at <= issued_at:
        raise ValueError("invalid evidence validity window")
    if not isinstance(observed_at, int) or not isinstance(sequence_number, int) or sequence_number < 1:
        raise ValueError("invalid observation time or sequence")
    envelope = {
        "schema": EVIDENCE_SCHEMA, "credential_digest": canonical_sha256(identity),
        "source_id": identity["source_id"], "source_type": identity["source_type"],
        "key_id": identity["key_id"], "claim_type": claim_type, "value": value,
        "unit": unit, "subject_id": subject_id, "action_id": action_id,\n        "action_payload_digest": action_payload_digest,
        "document_digest": document_digest, "input_digest": input_digest,
        "output_digest": output_digest, "transformation_id": transformation_id,
        "tool_version": tool_version, "observed_at": observed_at,
        "issued_at": issued_at, "expires_at": expires_at,
        "sequence_number": sequence_number, "nonce": nonce,
        "calibration_id": calibration_id,
        "calibration_valid_until": calibration_valid_until,
    }
    return {"envelope": envelope, "signature_b64": base64.b64encode(
        source_private_key.sign(canonical_bytes(envelope))).decode("ascii")}


def verify_claim_evidence(record: dict, credential: dict, *,
                          trusted_issuer_key: Ed25519PublicKey, tenant_id: str,
                          expected_claim: str, expected_subject_id: str,
                          expected_action_id: str, expected_action_payload_digest: str, expected_document_digest: str,
                          now: int, consumed_nonces: MutableSet[str] | None = None,
                          last_sequences: dict[str, int] | None = None,
                          revoked_serials: frozenset[str] = frozenset()
                          ) -> tuple[bool, str, dict | None]:
    try:
        valid, reason, identity, source_key = verify_source_credential(
            credential, trusted_issuer_key=trusted_issuer_key,
            tenant_id=tenant_id, now=now, revoked_serials=revoked_serials)
        if not valid:
            return False, reason, None
        env = record["envelope"]
        if env.get("schema") != EVIDENCE_SCHEMA:
            return False, "unsupported_evidence_schema", None
        if env.get("credential_digest") != canonical_sha256(identity):
            return False, "credential_binding_mismatch", None
        for field in ("source_id", "source_type", "key_id"):
            if env.get(field) != identity[field]:
                return False, "source_identity_mismatch", None
        if env.get("claim_type") != expected_claim:
            return False, "claim_type_mismatch", None
        if expected_claim not in identity["allowed_claims"]:
            return False, "source_not_competent_for_claim", None
        if env.get("subject_id") != expected_subject_id:
            return False, "subject_mismatch", None
        if env.get("action_id") != expected_action_id:
            return False, "action_scope_mismatch", None
        if env.get("document_digest") != expected_document_digest:
            return False, "document_binding_mismatch", None
        if not isinstance(now, int) or now < env["issued_at"] or now >= env["expires_at"]:
            return False, "evidence_expired_or_not_yet_valid", None
        if env["observed_at"] > now:
            return False, "future_observation", None
        if env["nonce"] in (consumed_nonces or set()):
            return False, "replay", None
        previous = (last_sequences or {}).get(identity["source_id"], 0)
        if env["sequence_number"] <= previous:
            return False, "non_monotonic_sequence", None
        if identity["source_type"] == "document_parser":
            if env["input_digest"] != expected_document_digest:
                return False, "transformation_input_mismatch", None
            expected_output = canonical_sha256({
                "claim_type": expected_claim, "value": env["value"], "unit": env["unit"],
            })
            if (env["output_digest"] != expected_output
                    or not env["transformation_id"] or not env["tool_version"]):
                return False, "transformation_output_mismatch", None
        if identity["source_type"] == "weighbridge":
            if not env.get("calibration_id") or env.get("calibration_valid_until", 0) < now:
                return False, "calibration_invalid_or_expired", None
        signature = base64.b64decode(record["signature_b64"], validate=True)
        source_key.verify(signature, canonical_bytes(env))
        if consumed_nonces is not None:
            consumed_nonces.add(env["nonce"])
        if last_sequences is not None:
            last_sequences[identity["source_id"]] = env["sequence_number"]
        return True, "valid_evidence", {**env, **{
            "acquisition_domain": identity["acquisition_domain"],
            "administrative_domain": identity["administrative_domain"],
            "gateway_id": identity["gateway_id"],
            "key_admin_domain": identity["key_admin_domain"],
        }}
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_evidence", None


def _values_agree(values: list, tolerance: float) -> bool:
    if not values:
        return False
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
        return max(float(v) for v in values) - min(float(v) for v in values) <= tolerance
    return all(v == values[0] for v in values[1:])


def evaluate_claim(records: Iterable[tuple[dict, dict]], *,
                   trusted_issuer_key: Ed25519PublicKey, tenant_id: str,
                   claim_type: str, expected_subject_id: str, expected_action_id: str,
                   expected_document_digest: str, now: int,
                   required_source_types: frozenset[str],
                   tolerance: float = 0.0) -> tuple[bool, str, list[dict]]:
    """Require competent, valid, matching, independently administered evidence."""
    verified = []
    nonces: set[str] = set()
    sequences: dict[str, int] = {}
    for record, credential in records:
        ok, reason, evidence = verify_claim_evidence(
            record, credential, trusted_issuer_key=trusted_issuer_key,
            tenant_id=tenant_id, expected_claim=claim_type,
            expected_subject_id=expected_subject_id, expected_action_id=expected_action_id,
            expected_document_digest=expected_document_digest, now=now,
            consumed_nonces=nonces, last_sequences=sequences)
        if not ok:
            return False, reason, []
        verified.append(evidence)
    types = {item["source_type"] for item in verified}
    if not required_source_types.issubset(types):
        return False, "required_source_type_missing", verified
    selected = [item for item in verified if item["source_type"] in required_source_types]
    if not _values_agree([item["value"] for item in selected], tolerance):
        return False, "claim_value_conflict", verified
    for field in ("source_id", "acquisition_domain", "administrative_domain",
                  "gateway_id", "key_admin_domain"):
        if len({item[field] for item in selected}) < len(required_source_types):
            return False, "shared_dependency:" + field, verified
    return True, "claim_supported", verified


def issue_action_binding(*, action_id: str, action_payload_digest: str, subject_id: str, document_digest: str,
                          policy_version: str, required_claims: Iterable[str],
                          evidence_digests: Iterable[str], issued_at: int, expires_at: int,
                          private_key: Ed25519PrivateKey) -> dict:
    if expires_at <= issued_at:
        raise ValueError("invalid action-binding validity window")
    payload = {
        "schema": ACTION_SCHEMA, "action_id": action_id,\n        "action_payload_digest": action_payload_digest, "subject_id": subject_id,
        "document_digest": document_digest, "policy_version": policy_version,
        "required_claims": sorted(set(required_claims)),
        "evidence_digests": sorted(set(evidence_digests)),
        "issued_at": issued_at, "expires_at": expires_at,
    }
    return {"payload": payload, "signature_b64": base64.b64encode(
        private_key.sign(canonical_bytes(payload))).decode("ascii")}


def verify_action_binding(binding: dict, *, trusted_authorizer_key: Ed25519PublicKey,
                          action_id: str, subject_id: str, document_digest: str,
                          policy_version: str, required_claims: Iterable[str],
                          evidence_digests: Iterable[str], now: int) -> tuple[bool, str]:
    try:
        payload = binding["payload"]
        if payload.get("schema") != ACTION_SCHEMA:
            return False, "unsupported_action_binding_schema"
        expected = {
            "action_id": action_id, "action_payload_digest": action_payload_digest,\n            "subject_id": subject_id,
            "document_digest": document_digest, "policy_version": policy_version,
            "required_claims": sorted(set(required_claims)),
            "evidence_digests": sorted(set(evidence_digests)),
        }
        if any(payload.get(k) != v for k, v in expected.items()):
            return False, "action_binding_mismatch"
        if not isinstance(now, int) or now < payload["issued_at"] or now >= payload["expires_at"]:
            return False, "action_binding_expired_or_not_yet_valid"
        trusted_authorizer_key.verify(
            base64.b64decode(binding["signature_b64"], validate=True),
            canonical_bytes(payload))
        return True, "valid_action_binding"
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return False, "invalid_action_binding"
