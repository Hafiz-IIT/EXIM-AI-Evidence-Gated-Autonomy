import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from src.evidence_trust_v3 import (
    issue_identity_credential, issue_witness_assertion, verify_witness_quorum,
    verify_identity_credential,
)


class EvidenceTrustV3Tests(unittest.TestCase):
    def setUp(self):
        self.root = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        self.witnesses = [
            Ed25519PrivateKey.from_private_bytes(bytes([i]) * 32) for i in (1, 2, 3)
        ]
        self.credentials = [
            issue_identity_credential(
                issuer_id="research-root", witness_id=f"w{i}", key_id=f"k{i}",
                public_key=key.public_key(), source_id=f"source-{i}",
                acquisition_domain=f"acquisition-{i}", administrative_domain=f"admin-{i}",
                tenant_id="tenant-A", serial=f"serial-{i}", issued_at=100,
                expires_at=300, issuer_private_key=self.root,
            )
            for i, key in enumerate(self.witnesses, 1)
        ]

    def records(self, weights=(10.0, 10.0, 10.0)):
        return [
            (issue_witness_assertion(
                credential=credential, witness_private_key=key,
                tenant_id="tenant-A", case_id="case-1", parent_digest="root",
                gross_weight=weight, item_type="machine", nonce=f"n{i}",
                issued_at=110, expires_at=200,
            ), credential)
            for i, (key, credential, weight) in enumerate(
                zip(self.witnesses, self.credentials, weights), 1)
        ]

    def verify(self, items):
        return verify_witness_quorum(
            items, trusted_issuer_key=self.root.public_key(), tenant_id="tenant-A",
            case_id="case-1", parent_digest="root", expected_weight=10.0,
            expected_item_type="machine", now=150, threshold=2, total_required=3,
        )

    def test_two_of_three_independent_witnesses_succeed(self):
        self.assertEqual(self.verify(self.records()), (True, "quorum_valid", 3))

    def test_one_compromised_witness_cannot_override_two_honest_witnesses(self):
        self.assertEqual(self.verify(self.records((99.0, 10.0, 10.0))),
                         (True, "quorum_valid", 2))

    def test_two_compromised_witnesses_can_control_quorum(self):
        self.assertEqual(self.verify(self.records((99.0, 99.0, 10.0))),
                         (False, "quorum_disagreement", 1))

    def test_shared_administrative_domain_is_not_independent(self):
        credentials = list(self.credentials)
        credentials = [issue_identity_credential(\n            issuer_id="research-root", witness_id=f"w{i}", key_id=f"k{i}",\n            public_key=self.witnesses[i-1].public_key(), source_id=f"source-{i}",\n            acquisition_domain=f"acquisition-{i}", administrative_domain="admin-1",\n            tenant_id="tenant-A", serial=f"serial-{i}", issued_at=100,\n            expires_at=300, issuer_private_key=self.root,\n        ) for i in (1, 2, 3)]\n        credentials[1] = issue_identity_credential(
            issuer_id="research-root", witness_id="w2", key_id="k2",
            public_key=self.witnesses[1].public_key(), source_id="source-2",
            acquisition_domain="acquisition-2", administrative_domain="admin-1",
            tenant_id="tenant-A", serial="serial-2", issued_at=100,
            expires_at=300, issuer_private_key=self.root,
        )
        records = [
            (issue_witness_assertion(
                credential=credential, witness_private_key=key,
                tenant_id="tenant-A", case_id="case-1", parent_digest="root",
                gross_weight=10.0, item_type="machine", nonce=f"shared-{i}",
                issued_at=110, expires_at=200,
            ), credential)
            for i, (key, credential) in enumerate(zip(self.witnesses, credentials))
        ]
        self.assertEqual(self.verify(records),
                         (False, "insufficient_identity_independence:administrative_domain", 0))

    def test_forged_identity_credential_is_rejected(self):
        credential = dict(self.credentials[0])
        credential["body"] = dict(credential["body"], source_id="attacker-source")
        valid, reason, _ = verify_identity_credential(
            credential, trusted_issuer_key=self.root.public_key(),
            expected_tenant_id="tenant-A", now=150,
        )
        self.assertFalse(valid)
        self.assertEqual(reason, "invalid_identity_credential")

    def test_revoked_credential_is_rejected(self):
        record = self.records()[0]
        valid, reason, count = verify_witness_quorum(
            [record], trusted_issuer_key=self.root.public_key(), tenant_id="tenant-A",
            case_id="case-1", parent_digest="root", expected_weight=10.0,
            expected_item_type="machine", now=150, threshold=1, total_required=1,
            revoked_serials=frozenset({"serial-1"}),
        )
        self.assertFalse(valid)
        self.assertEqual(reason, "insufficient_valid_witnesses")
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
