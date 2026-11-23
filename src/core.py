import hashlib
import json
import math
from collections.abc import Mapping


def _canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def visible_features(r):
    o = r["observable"]
    inv = o["documents"]["invoice"]
    pack = o["documents"]["packing_list"]
    dec = o["documents"]["declaration"]
    present = [d for d in (inv, pack, dec) if d is not None]

    def agree(field):
        vals = [d[field] for d in present]
        return bool(vals) and len(set(vals)) == 1

    auth = o["external"]["authorization"]
    ex = o["machine"]["extraction"]
    vs = o["machine"]["verifiers"]
    ext = o["external"]["measured_weight"]
    instances = o.get("document_instances")
    duplicate_document_kind = False
    if instances is not None:
        kinds = [item["kind"] for item in instances]
        duplicate_document_kind = len(kinds) != len(set(kinds))
    provenance = o.get("provenance")
    provenance_valid = True  # v0.3 records predate the explicit lineage envelope.
    if provenance is not None:
        provenance_valid = (
            provenance.get("integrity_status") == "valid"
            and provenance.get("document_set_sha256") == _canonical_hash(instances or [])
        )

    return {
        "confidence": ex["confidence"],
        "complete": all(d is not None for d in (inv, pack, dec)),
        "doc_agree": all(agree(x) for x in ("quantity", "gross_weight", "hs")),
        "auth_present": auth["present"],
        "fresh": auth["present"] and auth["expiry_day"] >= o["external"]["evaluation_day"],
        "external_conflict": any(abs(d["gross_weight"] - ext) > 1e-9 for d in present),
        "ex_matches_invoice": inv is not None
        and ex["quantity"] == inv["quantity"]
        and abs(ex["gross_weight"] - inv["gross_weight"]) < 1e-9
        and ex["hs"] == inv["hs"],
        "v_rejects": sum(not bool(v["accept"]) for v in vs),
        "n_verifiers": len(vs),
        "indep_verifiers": len({v["dependency_group"] for v in vs}),
        "duplicate_document_kind": duplicate_document_kind,
        "provenance_valid": provenance_valid,
        "risk": r["action"]["risk_level"],
    }


def evidence_gate_v1(r):
    f = visible_features(r)
    if f["risk"] == "LOW":
        return "ACT"
    if f["duplicate_document_kind"] or not f["provenance_valid"]:
        return "ESCALATE"
    if not f["complete"] or not f["auth_present"] or not f["fresh"]:
        return "REQUEST_EVIDENCE"
    if not f["doc_agree"]:
        return "VERIFY"
    if f["external_conflict"]:
        return "ESCALATE"
    if not f["ex_matches_invoice"]:
        return "VERIFY"
    if f["v_rejects"] > 0 or f["indep_verifiers"] < 2:
        return "ESCALATE"
    return "ACT"


def always_act(r):
    return "ACT"


def confidence_gate(r, threshold=0.90):
    return "ACT" if visible_features(r)["confidence"] >= threshold else "DEFER"


def document_agreement(r):
    f = visible_features(r)
    return "ACT" if f["complete"] and f["doc_agree"] else "DEFER"


def always_verify(r):
    return "VERIFY"


def selective_abstention(r, threshold=0.90):
    f = visible_features(r)
    return "ACT" if f["confidence"] >= threshold and f["v_rejects"] == 0 else "DEFER"


def weak_strong(r, hi=0.94, lo=0.75):
    f = visible_features(r)
    weak = f["doc_agree"] and (f["n_verifiers"] - f["v_rejects"]) >= math.ceil(f["n_verifiers"] / 2)
    if f["confidence"] >= hi and weak:
        return "ACT"
    if f["confidence"] < lo:
        return "DEFER"
    return "VERIFY"


def risk_gate(r, threshold=0.90):
    f = visible_features(r)
    return "VERIFY" if f["risk"] == "HIGH" else ("ACT" if f["confidence"] >= threshold else "DEFER")


def evidence_gate_v2(r, *, trusted_action_id, trusted_action_catalog):
    """Authorize only an action whose consequence metadata matches trusted context.

    trusted_action_id must come from an authorization context independent of the
    agent-proposed action. The catalog must be maintained outside the model.
    This function checks metadata binding; it does not itself authenticate the
    caller or enforce the eventual tool invocation.
    """
    if not isinstance(r, Mapping):
        return "ESCALATE"
    if not isinstance(trusted_action_id, str) or not trusted_action_id:
        return "ESCALATE"
    if not isinstance(trusted_action_catalog, Mapping):
        return "ESCALATE"
    action = r.get("action")
    if not isinstance(action, Mapping):
        return "ESCALATE"
    if action.get("name") != trusted_action_id:
        return "ESCALATE"
    trusted = trusted_action_catalog.get(trusted_action_id)
    if not isinstance(trusted, Mapping):
        return "ESCALATE"
    required = ("risk_level", "reversibility", "external_effect")
    if any(not isinstance(trusted.get(key), str) or not trusted.get(key) for key in required):
        return "ESCALATE"
    if any(action.get(key) != trusted[key] for key in required):
        return "ESCALATE"
    if trusted["risk_level"] not in {"LOW", "HIGH"}:
        return "ESCALATE"

    normalized = dict(r)
    normalized["action"] = dict(action)
    normalized["action"]["risk_level"] = trusted["risk_level"]
    return evidence_gate_v1(normalized)
