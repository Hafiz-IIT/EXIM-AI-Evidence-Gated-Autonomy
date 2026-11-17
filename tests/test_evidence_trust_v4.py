import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from src.evidence_trust_v3 import issue_witness_assertion
from src.evidence_trust_v4 import (
    DEPENDENCY_LAYERS,
    issue_identity_credential_v4,
    verify_witness_quorum_v4,
)


class EvidenceTrustV4Tests(unittest.TestCase):
    def setUp(self):
        self.root = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        self.witnesses = [
            Ed25519PrivateKey.from_private_bytes(bytes([i]) * 32) for i in (1, 2, 3)
        ]

    def roots(self, index, shared_layer=None, shared_value="common-root"):
        result = {
            layer: [f"{layer}-{index}"] for layer in DEPENDENCY_LAYERS
        }
        if shared_layer:
            result[shared_layer] = [shared_value]
        return result

    def credentials(self, shared_layer=None, shared_indexes=(1, 2, 3)):
        credentials = []
        for i, key in enumerate(self.witnesses, 1):
            credentials.append(issue_identity_credential_v4(
                issuer_id="registry-root", witness_id=f"w{i}", key_id=f"k{i}",
                public_key=key.public_key(), source_id=f"source-{i}",
                acquisition_domain=f"acquisition-{i}",
                administrative_domain=f"admin-{i}", tenant_id="tenant-A",
                dependency_roots=self.roots(
                    i, shared_layer=shared_layer if i in shared_indexes else None
                ),
                serial=f"serial-{i}", issued_at=100, expires_at=300,
                issuer_private_key=self.root,
            ))
        return credentials

    def records(self, credentials, weights=(10.0, 10.0, 10.0)):
        return [
            (issue_witness_assertion(
                credential=credential, witness_private_key=key,
                tenant_id="tenant-A", case_id="case-1", parent_digest="parent",
                gross_weight=weight, item_type="machine", nonce=f"n{i}",
                issued_at=110, expires_at=200,
            ), credential)
            for i, (key, credential, weight) in enumerate(
                zip(self.witnesses, credentials, weights), 1
            )
        ]

    def verify(self, records, *, threshold=2, dependency_aware=True):
        return verify_witness_quorum_v4(
            records, trusted_issuer_key=self.root.public_key(),
            tenant_id="tenant-A", case_id="case-1", parent_digest="parent",
            expected_weight=10.0, expected_item_type="machine", now=150,
            threshold=threshold, total_required=3,
            dependency_aware=dependency_aware,
        )

    def test_independent_dependency_roots_succeed(self):
        self.assertEqual(
            self.verify(self.records(self.credentials())),
            (True, "quorum_valid", 2),
        )

    def test_shared_parent_control_is_detected_but_field_only_ablation_accepts(self):
        records = self.records(self.credentials(shared_layer="parent_control"))
        self.assertEqual(
            self.verify(records),
            (False, "shared_dependency:parent_control", 0),
        )
        self.assertEqual(
            self.verify(records, dependency_aware=False),
            (True, "quorum_valid", 2),
        )

    def test_shared_measurement_source_is_detected(self):
        records = self.records(self.credentials(shared_layer="measurement_source"))
        self.assertEqual(
            self.verify(records),
            (False, "shared_dependency:measurement_source", 0),
        )

    def test_shared_identity_provider_is_detected(self):
        records = self.records(self.credentials(shared_layer="identity_provider"))
        self.assertEqual(
            self.verify(records),
            (False, "shared_dependency:identity_provider", 0),
        )

    def test_quorum_selects_an_independent_subset_from_matching_supporters(self):
        # w1 and w2 share a parent; w3 is independent. All three measurements
        # match, so a 2-of-3 graph-aware quorum can select w1+w3 or w2+w3.
        credentials = self.credentials(
            shared_layer="parent_control", shared_indexes=(1, 2)
        )
        records = self.records(credentials)
        self.assertEqual(
            self.verify(records, threshold=2),
            (True, "quorum_valid", 2),
        )
        self.assertEqual(
            self.verify(records, threshold=3),
            (False, "shared_dependency:parent_control", 0),
        )

    def test_registry_root_compromise_can_enroll_two_attacker_witnesses(self):
        attacker_root = Ed25519PrivateKey.from_private_bytes(bytes([9]) * 32)
        credentials = self.credentials()
        for index in (0, 1):
            credentials[index] = issue_identity_credential_v4(
                issuer_id="attacker-registry-root", witness_id=f"attacker-w{index+1}",
                key_id=f"attacker-k{index+1}",
                public_key=self.witnesses[index].public_key(),
                source_id=f"attacker-source-{index+1}",
                acquisition_domain=f"attacker-acq-{index+1}",
                administrative_domain=f"attacker-admin-{index+1}",
                tenant_id="tenant-A", dependency_roots=self.roots(index+1),
                serial=f"attacker-serial-{index+1}", issued_at=100,
                expires_at=300, issuer_private_key=attacker_root,
            )
        records = self.records(credentials)
        self.assertEqual(
            verify_witness_quorum_v4(
                records, trusted_issuer_key=attacker_root.public_key(),
                tenant_id="tenant-A", case_id="case-1", parent_digest="parent",
                expected_weight=10.0, expected_item_type="machine", now=150,
                threshold=2, total_required=3,
            ),
            (True, "quorum_valid", 2),
        )
        self.assertEqual(
            verify_witness_quorum_v4(
                records, trusted_issuer_key=attacker_root.public_key(),
                tenant_id="tenant-A", case_id="case-1", parent_digest="parent",
                expected_weight=10.0, expected_item_type="machine", now=150,
                threshold=3, total_required=3,
            ),
            (False, "insufficient_valid_witnesses", 0),
        )

    def test_missing_dependency_layer_is_rejected_at_issuance(self):
        roots = self.roots(1)
        roots.pop("measurement_source")
        with self.assertRaises(ValueError):
            issue_identity_credential_v4(
                issuer_id="registry-root", witness_id="w1", key_id="k1",
                public_key=self.witnesses[0].public_key(), source_id="source-1",
                acquisition_domain="acq-1", administrative_domain="admin-1",
                tenant_id="tenant-A", dependency_roots=roots,
                serial="serial-1", issued_at=100, expires_at=300,
                issuer_private_key=self.root,
            )

    def test_dependency_root_claims_are_covered_by_registry_signature(self):
        credential = self.credentials()[0]
        credential["body"]["dependency_roots"]["parent_control"] = ["attacker-root"]
        records = self.records([credential, *self.credentials()[1:]])
        self.assertEqual(
            self.verify(records),
            (False, "invalid_identity_credential", 0),
        )


if __name__ == "__main__":
    unittest.main()
