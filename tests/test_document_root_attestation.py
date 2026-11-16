import copy
import hashlib
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from src.provenance import (
    create_document_root_attestation,
    verify_document_root_attestation,
)


def test_key(label):
    seed = hashlib.sha256(("DOCUMENT-ROOT-TEST-ONLY|" + label).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def sample_documents():
    instances = [
        {"document_id": "inv-1", "kind": "invoice", "fields": {"quantity": 20, "hs": "8542"}},
        {"document_id": "pl-1", "kind": "packing_list", "fields": {"quantity": 20, "gross_weight": 32.4}},
        {"document_id": "dec-1", "kind": "declaration", "fields": {"quantity": 20, "hs": "8542"}},
    ]
    normalized = {
        "invoice": {"quantity": 20, "hs": "8542"},
        "packing_list": {"quantity": 20, "gross_weight": 32.4},
        "declaration": {"quantity": 20, "hs": "8542"},
    }
    return instances, normalized


def attest(instances, normalized, key=None, key_id="doc-root-k1", tenant="tenant-A", case="case-1", nonce="nonce-1"):
    private = key or test_key(key_id)
    return create_document_root_attestation(
        signer_id="document-root-authority",
        key_id=key_id,
        tenant_id=tenant,
        case_id=case,
        document_instances=instances,
        normalized_documents=normalized,
        private_key=private,
        issued_at=100,
        expires_at=200,
        nonce=nonce,
    )


def verify(record, instances, normalized, keys=None, revoked=(), tenant="tenant-A", case="case-1", now=150, consumed=None):
    return verify_document_root_attestation(
        record,
        trusted_keys=keys or {"doc-root-k1": test_key("doc-root-k1").public_key()},
        revoked_key_ids=set(revoked),
        expected_tenant_id=tenant,
        expected_case_id=case,
        document_instances=instances,
        normalized_documents=normalized,
        now=now,
        consumed_nonces=consumed,
    )


class DocumentRootAttestationTests(unittest.TestCase):
    def setUp(self):
        self.instances, self.normalized = sample_documents()
        self.record = attest(self.instances, self.normalized)

    def test_valid_attestation_binds_both_document_representations(self):
        ok, reason = verify(self.record, self.instances, self.normalized)
        self.assertTrue(ok)
        self.assertEqual(reason, "valid")

    def test_raw_document_instance_tampering_is_rejected(self):
        changed = copy.deepcopy(self.instances)
        changed[0]["fields"]["quantity"] = 999
        self.assertEqual(verify(self.record, changed, self.normalized), (False, "document_instances_mismatch"))

    def test_normalized_document_tampering_is_rejected(self):
        changed = copy.deepcopy(self.normalized)
        changed["invoice"]["quantity"] = 999
        self.assertEqual(verify(self.record, self.instances, changed), (False, "normalized_documents_mismatch"))

    def test_coherent_rewrite_cannot_be_resigned_without_trusted_private_key(self):
        rewritten_instances = copy.deepcopy(self.instances)
        rewritten_normalized = copy.deepcopy(self.normalized)
        for item in rewritten_instances:
            item["fields"]["quantity"] = 999
        for item in rewritten_normalized.values():
            item["quantity"] = 999
        self.assertEqual(
            verify(self.record, rewritten_instances, rewritten_normalized),
            (False, "document_instances_mismatch"),
        )

    def test_attestation_is_bound_to_tenant_and_case(self):
        self.assertEqual(verify(self.record, self.instances, self.normalized, tenant="tenant-B"), (False, "tenant_mismatch"))
        self.assertEqual(verify(self.record, self.instances, self.normalized, case="case-2"), (False, "case_mismatch"))

    def test_expired_and_not_yet_valid_attestations_are_rejected(self):
        self.assertEqual(verify(self.record, self.instances, self.normalized, now=200), (False, "expired_or_not_yet_valid"))
        self.assertEqual(verify(self.record, self.instances, self.normalized, now=99), (False, "expired_or_not_yet_valid"))

    def test_revoked_key_is_rejected(self):
        self.assertEqual(verify(self.record, self.instances, self.normalized, revoked={"doc-root-k1"}), (False, "revoked_key"))

    def test_key_rotation_accepts_new_key_and_rejects_revoked_old_key(self):
        new_key = test_key("doc-root-k2")
        new_record = attest(self.instances, self.normalized, key=new_key, key_id="doc-root-k2", nonce="nonce-rotated")
        keys = {"doc-root-k2": new_key.public_key()}
        self.assertEqual(verify(new_record, self.instances, self.normalized, keys=keys), (True, "valid"))
        self.assertEqual(
            verify(self.record, self.instances, self.normalized, keys=keys, revoked={"doc-root-k1"}),
            (False, "revoked_key"),
        )

    def test_cross_tenant_replay_is_rejected(self):
        self.assertEqual(verify(self.record, self.instances, self.normalized, tenant="tenant-B"), (False, "tenant_mismatch"))

    def test_nonce_replay_is_rejected_after_first_success(self):
        consumed = set()
        self.assertEqual(verify(self.record, self.instances, self.normalized, consumed=consumed), (True, "valid"))
        self.assertEqual(verify(self.record, self.instances, self.normalized, consumed=consumed), (False, "replay"))

    def test_invalid_signature_is_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["signature_b64"] = "AAAA"
        self.assertEqual(verify(altered, self.instances, self.normalized), (False, "invalid_attestation"))


if __name__ == "__main__":
    unittest.main()
