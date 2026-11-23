"""Experimental signed action-catalog and executor-binding boundary.

HMAC is used only to make the trust boundary testable with the standard library.
It is not a production PKI, KMS, key-rotation, or identity solution.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Mapping


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _mac(payload: Mapping, key: bytes) -> str:
    if not isinstance(key, bytes) or len(key) < 16:
        raise ValueError("signing key must contain at least 16 bytes")
    return hmac.new(key, _canonical(payload), hashlib.sha256).hexdigest()


def sign_catalog(version: str, actions: Mapping, key: bytes) -> dict:
    if not isinstance(version, str) or not version:
        raise ValueError("catalog version is required")
    if not isinstance(actions, Mapping) or not actions:
        raise ValueError("catalog actions are required")
    payload = {"version": version, "actions": dict(actions)}
    return {"payload": payload, "signature": _mac(payload, key)}


def verify_catalog(manifest: object, key: bytes, expected_version: str) -> bool:
    if not isinstance(manifest, Mapping):
        return False
    payload = manifest.get("payload")
    signature = manifest.get("signature")
    if not isinstance(payload, Mapping) or not isinstance(signature, str):
        return False
    if payload.get("version") != expected_version:
        return False
    try:
        expected = _mac(payload, key)
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(signature, expected)


def authorize_action(
    proposed_action: object,
    *,
    trusted_action_id: str,
    manifest: object,
    key: bytes,
    expected_catalog_version: str,
) -> dict | None:
    if not verify_catalog(manifest, key, expected_catalog_version):
        return None
    if not isinstance(proposed_action, Mapping) or not isinstance(trusted_action_id, str):
        return None
    payload = manifest["payload"]
    action = payload["actions"].get(trusted_action_id)
    if not isinstance(action, Mapping):
        return None
    if proposed_action.get("name") != trusted_action_id:
        return None
    fields = ("risk_level", "reversibility", "external_effect")
    if any(not isinstance(action.get(field), str) or not action[field] for field in fields):
        return None
    if any(proposed_action.get(field) != action[field] for field in fields):
        return None
    authorization = {
        "action_id": trusted_action_id,
        "catalog_version": expected_catalog_version,
        "consequences": {field: action[field] for field in fields},
    }
    return {"payload": authorization, "signature": _mac(authorization, key)}


def verify_execution_binding(
    authorization: object,
    *,
    invoked_action_id: str,
    current_catalog_version: str,
    key: bytes,
) -> bool:
    if not isinstance(authorization, Mapping):
        return False
    payload = authorization.get("payload")
    signature = authorization.get("signature")
    if not isinstance(payload, Mapping) or not isinstance(signature, str):
        return False
    if payload.get("action_id") != invoked_action_id:
        return False
    if payload.get("catalog_version") != current_catalog_version:
        return False
    try:
        expected = _mac(payload, key)
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(signature, expected)
