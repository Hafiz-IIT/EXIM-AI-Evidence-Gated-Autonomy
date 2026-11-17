import copy
import unittest

from scripts.generate_benchmark import make as make_v03
from scripts.generate_benchmark_v04 import attach_document_lineage
from scripts.run_evidence_trust_v2 import (
    apply_compromise_capabilities,
    authorize,
    make_source_forgery,
)
from src.evidence_trust_v2 import create_attestation, verify_attestation
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


class EvidenceTrustV2Tests(unittest.TestCase):
    def setUp(self):
        self.key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        self.public = self.key.public_key()
        self.case = make_v03(4, "C4_consistent_but_wrong", 0)
        attach_document_lineage(self.case["observable"])
        self.case = {
            "case_id": "U-C4-test-HIGH",
            "family": "C4_consistent_but_wrong",
            "observable": self.case["observable"],
            "ground_truth": self.case["ground_truth"],
            "action": {"risk_level": "HIGH"},
            "safe_to_act": self.case["high_safe_to_act"],
        }

    def test_role_scoped_attestation_verifies(self):
        record = create_attestation(
            role="capture", key_id="capture-key", tenant_id="tenant-A",
            case_id="case-1", parent_digest="root-digest",
            payload={"raw_digest": "abc"}, private_key=self.key,
            issued_at=100, expires_at=200, nonce="n-1",
        )
        self.assertEqual(
            verify_attestation(
                record, expected_role="capture", trusted_keys={"capture-key": self.public},
                tenant_id="tenant-A", case_id="case-1", parent_digest="root-digest", now=150,
            ),
            (True, "valid"),
        )

    def test_wrong_role_and_parent_are_rejected(self):
        record = create_attestation(
            role="capture", key_id="capture-key", tenant_id="tenant-A",
            case_id="case-1", parent_digest="root-digest",
            payload={"raw_digest": "abc"}, private_key=self.key,
            issued_at=100, expires_at=200, nonce="n-2",
        )
        args = dict(
            trusted_keys={"capture-key": self.public}, tenant_id="tenant-A",
            case_id="case-1", now=150,
        )
        self.assertEqual(
            verify_attestation(record, expected_role="interpretation",
                               parent_digest="root-digest", **args),
            (False, "role_mismatch"),
        )
        self.assertEqual(
            verify_attestation(record, expected_role="capture",
                               parent_digest="other-root", **args),
            (False, "parent_mismatch"),
        )

    def test_expiry_revocation_and_replay_are_enforced(self):
        record = create_attestation(
            role="capture", key_id="capture-key", tenant_id="tenant-A",
            case_id="case-1", parent_digest="root-digest",
            payload={"raw_digest": "abc"}, private_key=self.key,
            issued_at=100, expires_at=200, nonce="n-3",
        )
        args = dict(
            expected_role="capture", trusted_keys={"capture-key": self.public},
            tenant_id="tenant-A", case_id="case-1", parent_digest="root-digest",
        )
        self.assertEqual(verify_attestation(record, **args, now=200), (False, "expired_or_not_yet_valid"))
        self.assertEqual(verify_attestation(record, **args, now=150, revoked_key_ids={"capture-key"}),
                         (False, "revoked_key"))
        consumed = set()
        self.assertEqual(verify_attestation(record, **args, now=150, consumed_nonces=consumed),
                         (True, "valid"))
        self.assertEqual(verify_attestation(record, **args, now=150, consumed_nonces=consumed),
                         (False, "replay"))

    def test_single_witness_authority_compromise_can_yield_unsafe_act(self):
        self.assertFalse(self.case["safe_to_act"])
        mutated = apply_compromise_capabilities(self.case, ("witness",))
        result = authorize(mutated, ("witness",), "test-witness-compromise")
        self.assertEqual(result["action"], "ACT")
        self.assertFalse(self.case["safe_to_act"])

    def test_capture_only_compromise_is_blocked_by_honest_measurement(self):
        mutated = apply_compromise_capabilities(self.case, ("capture",))
        result = authorize(mutated, ("capture",), "test-capture-compromise")
        self.assertNotEqual(result["action"], "ACT")

    def test_source_forgery_before_capture_is_blocked_by_independent_witness(self):
        forged = make_source_forgery(self.case, shared_witness=False)
        result = authorize(forged, (), "test-source-forgery")
        self.assertNotEqual(result["action"], "ACT")

    def test_shared_dependency_witness_can_mask_source_forgery(self):
        forged = make_source_forgery(self.case, shared_witness=True)
        result = authorize(
            forged, (), "test-shared-dependency", witness_dependency=True
        )
        self.assertEqual(result["action"], "ACT")

    def test_authorization_authority_compromise_can_bypass_policy(self):
        result = authorize(self.case, ("authorization",), "test-aa-compromise")
        self.assertEqual(result["action"], "ACT")


if __name__ == "__main__":
    unittest.main()
