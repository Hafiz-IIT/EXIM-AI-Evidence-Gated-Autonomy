import unittest

from scripts.run_evidence_trust_v3 import make_source_forgery
from src.provenance import canonical_sha256

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from src.evidence_trust_v3 import (
    issue_identity_credential, issue_witness_assertion, verify_witness_quorum,
    verify_identity_credential, is_recoverable_verifier_false_reject,
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

    def records(self, weights=(10.0, 10.0, 10.0), credentials=None):
        credentials = credentials or self.credentials
        return [
            (issue_witness_assertion(
                credential=credential, witness_private_key=key,
                tenant_id="tenant-A", case_id="case-1", parent_digest="root",
                gross_weight=weight, item_type="machine", nonce=f"n{i}",
                issued_at=110, expires_at=200,
            ), credential)
            for i, (key, credential, weight) in enumerate(
                zip(self.witnesses, credentials, weights), 1)
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

    def test_two_compromised_witnesses_cannot_match_honest_target(self):
        self.assertEqual(self.verify(self.records((99.0, 99.0, 10.0))),
                         (False, "quorum_disagreement", 1))

    def test_three_of_three_requires_every_witness_to_match(self):
        result = verify_witness_quorum(
            self.records((10.0, 10.0, 99.0)),
            trusted_issuer_key=self.root.public_key(), tenant_id="tenant-A",
            case_id="case-1", parent_digest="root", expected_weight=10.0,
            expected_item_type="machine", now=150, threshold=3, total_required=3,
        )
        self.assertEqual(result, (False, "quorum_disagreement", 2))

    def test_three_of_three_succeeds_when_all_independent_witnesses_match(self):
        result = verify_witness_quorum(
            self.records(),
            trusted_issuer_key=self.root.public_key(), tenant_id="tenant-A",
            case_id="case-1", parent_digest="root", expected_weight=10.0,
            expected_item_type="machine", now=150, threshold=3, total_required=3,
        )
        self.assertEqual(result, (True, "quorum_valid", 3))

    def test_two_of_three_tolerates_one_invalid_credential_but_three_of_three_does_not(self):
        credentials = list(self.credentials)
        credentials[0] = dict(credentials[0])
        credentials[0]["body"] = dict(credentials[0]["body"], source_id="forged-source")
        records = self.records(credentials=credentials)
        self.assertEqual(self.verify(records), (True, "quorum_valid", 2))
        strict = verify_witness_quorum(
            records, trusted_issuer_key=self.root.public_key(), tenant_id="tenant-A",
            case_id="case-1", parent_digest="root", expected_weight=10.0,
            expected_item_type="machine", now=150, threshold=3, total_required=3,
        )
        self.assertEqual(strict, (False, "insufficient_valid_witnesses", 0))

    def test_three_of_three_does_not_defeat_full_roster_compromise(self):
        result = verify_witness_quorum(
            self.records((99.0, 99.0, 99.0)),
            trusted_issuer_key=self.root.public_key(), tenant_id="tenant-A",
            case_id="case-1", parent_digest="root", expected_weight=99.0,
            expected_item_type="machine", now=150, threshold=3, total_required=3,
        )
        self.assertEqual(result, (True, "quorum_valid", 3))

    def test_all_witnesses_must_have_distinct_admin_domains(self):
        credentials = []
        for i, key in enumerate(self.witnesses, 1):
            credentials.append(issue_identity_credential(
                issuer_id="research-root", witness_id=f"w{i}", key_id=f"k{i}",
                public_key=key.public_key(), source_id=f"source-{i}",
                acquisition_domain=f"acquisition-{i}", administrative_domain="shared-admin",
                tenant_id="tenant-A", serial=f"serial-{i}", issued_at=100,
                expires_at=300, issuer_private_key=self.root,
            ))
        self.assertEqual(
            self.verify(self.records(credentials=credentials)),
            (False, "insufficient_identity_independence:administrative_domain", 0),
        )

    def test_matching_quorum_must_itself_be_independent(self):
        credentials = [
            issue_identity_credential(
                issuer_id="research-root", witness_id=f"w{i}", key_id=f"k{i}",
                public_key=key.public_key(), source_id=f"source-{i}",
                acquisition_domain=f"acquisition-{i}",
                administrative_domain=("shared-admin" if i in (1, 2) else "admin-3"),
                tenant_id="tenant-A", serial=f"serial-{i}", issued_at=100,
                expires_at=300, issuer_private_key=self.root,
            )
            for i, key in enumerate(self.witnesses, 1)
        ]
        # Two matching assertions share an administrator; the independent
        # third witness dissents and must not make the colluding pair look independent.
        self.assertEqual(
            self.verify(self.records((10.0, 10.0, 99.0), credentials=credentials)),
            (False, "insufficient_identity_independence:administrative_domain", 0),
        )

    def test_quorum_requires_the_configured_distinct_witness_roster(self):
        self.assertEqual(
            self.verify(self.records()[:2]),
            (False, "incomplete_or_duplicate_witness_roster", 0),
        )

    def test_independent_quorum_can_recover_isolated_verifier_false_reject(self):
        features = {
            "risk": "HIGH", "duplicate_document_kind": False,
            "provenance_valid": True, "complete": True,
            "auth_present": True, "fresh": True, "doc_agree": True,
            "external_conflict": False, "ex_matches_invoice": True,
            "n_verifiers": 2, "indep_verifiers": 2, "v_rejects": 2,
        }
        self.assertTrue(is_recoverable_verifier_false_reject(features, "ESCALATE"))

    def test_verifier_recovery_does_not_override_other_safety_gates(self):
        safe_features = {
            "risk": "HIGH", "duplicate_document_kind": False,
            "provenance_valid": True, "complete": True,
            "auth_present": True, "fresh": True, "doc_agree": True,
            "external_conflict": False, "ex_matches_invoice": True,
            "n_verifiers": 2, "indep_verifiers": 2, "v_rejects": 2,
        }
        for blocked_field, blocked_value in (
            ("provenance_valid", False), ("complete", False),
            ("auth_present", False), ("fresh", False),
            ("doc_agree", False), ("external_conflict", True),
            ("ex_matches_invoice", False), ("duplicate_document_kind", True),
            ("indep_verifiers", 1),
        ):
            with self.subTest(blocked_field=blocked_field):
                candidate = dict(safe_features, **{blocked_field: blocked_value})
                self.assertFalse(is_recoverable_verifier_false_reject(candidate, "ESCALATE"))
        self.assertFalse(is_recoverable_verifier_false_reject(safe_features, "ACT"))
        self.assertFalse(is_recoverable_verifier_false_reject(
            dict(safe_features, v_rejects=0), "ESCALATE"))

    def test_pre_capture_source_forgery_invalidates_safe_to_act_label(self):
        case = {
            "safe_to_act": True,
            "observable": {
                "documents": {
                    "invoice": {"quantity": 10, "gross_weight": 20.0, "hs": "1234"},
                    "packing_list": None,
                    "declaration": None,
                },
                "document_instances": [{
                    "kind": "invoice",
                    "fields": {"quantity": 10, "gross_weight": 20.0, "hs": "1234"},
                }],
                "provenance": {"integrity_status": "valid", "document_set_sha256": ""},
                "machine": {
                    "extraction": {"quantity": 10, "gross_weight": 20.0, "hs": "1234"},
                    "classification": {"hs": "1234"},
                },
            },
        }
        forged = make_source_forgery(case)
        self.assertFalse(forged["safe_to_act"])
        self.assertTrue(case["safe_to_act"])
        self.assertEqual(
            forged["observable"]["provenance"]["document_set_sha256"],
            canonical_sha256(forged["observable"]["document_instances"]),
        )

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

    def test_invalid_quorum_configuration_is_rejected(self):
        result = verify_witness_quorum(
            self.records(), trusted_issuer_key=self.root.public_key(), tenant_id="tenant-A",
            case_id="case-1", parent_digest="root", expected_weight=10.0,
            expected_item_type="machine", now=150, threshold=4, total_required=3,
        )
        self.assertEqual(result, (False, "invalid_quorum_configuration", 0))


if __name__ == "__main__":
    unittest.main()
