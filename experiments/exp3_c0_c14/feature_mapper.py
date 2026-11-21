"""Deterministic extraction of explicit model fields into the EGA feature schema.

This module never infers a positive feature from silence and never chooses a gate action.
"""
from __future__ import annotations

def _strings(value,field,errors):
    if not isinstance(value,list) or any(not isinstance(x,str) for x in value):
        errors.append(f"{field}:missing_or_invalid_array")
        return None
    return value

def _boolean(value,field,errors):
    if type(value) is not bool:
        errors.append(f"{field}:missing_or_invalid_boolean")
        return None
    return value

def map_evidence_features(case:dict,proposer:dict,v1:dict|None,v2:dict|None)->dict:
    errors=[]
    if v1 is None: errors.append("v1:missing_verifier_output")
    if v2 is None: errors.append("v2:missing_verifier_output")
    p_missing=_strings(proposer.get("missing_evidence"),"proposer.missing_evidence",errors)
    p_conflicts=_strings(proposer.get("conflicts_detected"),"proposer.conflicts_detected",errors)
    p_fresh=_strings(proposer.get("freshness_concerns"),"proposer.freshness_concerns",errors)
    p_prov=_strings(proposer.get("provenance_concerns"),"proposer.provenance_concerns",errors)
    p_dep=_strings(proposer.get("dependency_concerns"),"proposer.dependency_concerns",errors)
    p_auth=_strings(proposer.get("authorization_evidence"),"proposer.authorization_evidence",errors)
    v1_missing=_strings(v1.get("critical_missing_evidence"),"v1.critical_missing_evidence",errors) if v1 is not None else None
    v1_fresh=_strings(v1.get("freshness_failures"),"v1.freshness_failures",errors) if v1 is not None else None
    v1_consequence=_strings(v1.get("consequence_mismatch"),"v1.consequence_mismatch",errors) if v1 is not None else None
    v1_reversibility=_strings(v1.get("reversibility_concerns"),"v1.reversibility_concerns",errors) if v1 is not None else None
    v1_false=_strings(v1.get("false_assumptions"),"v1.false_assumptions",errors) if v1 is not None else None
    v2_prov=_strings(v2.get("provenance_concerns"),"v2.provenance_concerns",errors) if v2 is not None else None
    v2_dep=_strings(v2.get("dependency_concerns"),"v2.dependency_concerns",errors) if v2 is not None else None
    v2_contra=_strings(v2.get("contradictions"),"v2.contradictions",errors) if v2 is not None else None
    v2_common=_strings(v2.get("possible_common_mode_failures"),"v2.possible_common_mode_failures",errors) if v2 is not None else None
    features={
      "completeness":{"missing_evidence":p_missing,"critical_missing_evidence":v1_missing},
      "consistency":{"conflicts":p_conflicts,"contradictions":v2_contra,"false_assumptions":v1_false},
      "freshness":{"proposer_concerns":p_fresh,"verifier_failures":v1_fresh},
      "provenance":{"proposer_concerns":p_prov,"verifier_concerns":v2_prov},
      "independence":{"proposer_dependencies":p_dep,"verifier_dependencies":v2_dep,"common_mode_failures":v2_common},
      "grounding":{"sufficient":_boolean(v2.get("grounding_sufficient"),"v2.grounding_sufficient",errors) if v2 is not None else None},
      "verifier_status":{
        "v1_proposal_supported":_boolean(v1.get("proposal_supported"),"v1.proposal_supported",errors) if v1 is not None else None,
        "v1_authorization_sufficient":_boolean(v1.get("authorization_sufficient"),"v1.authorization_sufficient",errors) if v1 is not None else None,
        "v2_proposal_supported":_boolean(v2.get("proposal_supported"),"v2.proposal_supported",errors) if v2 is not None else None,
        "v2_evidence_consistent":_boolean(v2.get("evidence_consistent"),"v2.evidence_consistent",errors) if v2 is not None else None,
      },
      "authorization":{"proposer_evidence":p_auth},
      "consequence":case.get("consequence"),
      "reversibility":case.get("reversibility"),
    }
    if features["consequence"] not in {"LOW","HIGH"}: errors.append("case.consequence:missing_or_invalid")
    if not isinstance(features["reversibility"],str) or not features["reversibility"].strip(): errors.append("case.reversibility:missing_or_invalid")
    return {"features":features,"mapping_errors":errors,"mapping_status":"valid" if not errors else "incomplete"}

