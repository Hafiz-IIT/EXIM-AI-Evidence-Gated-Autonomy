import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from src.evidence_provenance_v4 import (
    issue_source_credential, issue_claim_evidence, verify_claim_evidence,
    evaluate_claim, issue_action_binding, verify_action_binding,
)
from src.provenance import canonical_sha256


class EvidenceProvenanceV4Tests(unittest.TestCase):
    def setUp(self):
        self.root = Ed25519PrivateKey.generate()
        self.authorizer = Ed25519PrivateKey.generate()
        self.tenant = "tenant-1"
        self.subject = "shipment-123"
        self.action = "file-declaration-123"
        self.doc_digest = canonical_sha256({"invoice": "synthetic-doc-v1"})
        self.action_payload_digest = canonical_sha256({"operation": "submit_declaration", "subject": self.subject})
        self.now = 200
        self.sources = {
            "document_parser": {
                "claims": ["gross_weight", "quantity", "hs_code"],
                "admin": "doc-admin", "gateway": "doc-gateway",
                "acq": "doc-acquisition", "keyadmin": "doc-key-admin",
            },
            "weighbridge": {
                "claims": ["gross_weight"],
                "admin": "port-admin", "gateway": "scale-gateway",
                "acq": "scale-acquisition", "keyadmin": "scale-key-admin",
            },
            "rfid_counter": {
                "claims": ["quantity"],
                "admin": "gate-admin", "gateway": "rfid-gateway",
                "acq": "rfid-acquisition", "keyadmin": "rfid-key-admin",
            },
            "tariff_registry": {
                "claims": ["hs_code"],
                "admin": "registry-admin", "gateway": "tariff-gateway",
                "acq": "tariff-acquisition", "keyadmin": "tariff-key-admin",
            },
        }
        self.keys = {name: Ed25519PrivateKey.generate() for name in self.sources}
        self.credentials = {}
        for name, spec in self.sources.items():
            self.credentials[name] = issue_source_credential(
                issuer_id="synthetic-root", source_id=f"source-{name}",
                source_type=name, key_id=f"key-{name}",
                public_key=self.keys[name].public_key(),
                allowed_claims=spec["claims"],
                acquisition_domain=spec["acq"],
                administrative_domain=spec["admin"],
                gateway_id=spec["gateway"],
                key_admin_domain=spec["keyadmin"],
                tenant_id=self.tenant, serial=f"serial-{name}",
                issued_at=100, expires_at=400,
                issuer_private_key=self.root,
            )

    def evidence(self, source_type, claim, value, **overrides):
        credential = self.credentials[source_type]
        digest = overrides.pop("document_digest", self.doc_digest)
        fields = dict(
            claim_type=claim, value=value, unit="kg" if claim == "gross_weight" else "count" if claim == "quantity" else "code",
            subject_id=self.subject, action_id=self.action,
            action_payload_digest=self.action_payload_digest,
            document_digest=digest, input_digest=digest,
            output_digest=canonical_sha256({"claim_type": claim, "value": value,
                                            "unit": "kg" if claim == "gross_weight" else "count" if claim == "quantity" else "code"}),
            transformation_id="transform-1", tool_version="parser-1.0",
            observed_at=190, issued_at=190, expires_at=300,
            sequence_number=1, nonce=f"nonce-{source_type}",
            calibration_id="cal-1" if source_type == "weighbridge" else "",
            calibration_valid_until=350 if source_type == "weighbridge" else 0,
        )
        fields.update(overrides)
        record = issue_claim_evidence(
            credential=credential, source_private_key=self.keys[source_type], **fields)
        return record, credential

    def verify(self, pair, claim, **kwargs):
        record, credential = pair
        return verify_claim_evidence(
            record, credential, trusted_issuer_key=self.root.public_key(),
            tenant_id=self.tenant, expected_claim=claim,
            expected_subject_id=self.subject, expected_action_id=self.action,
            expected_document_digest=self.doc_digest, now=self.now, **kwargs)

    def test_gross_weight_requires_document_parser_and_calibrated_scale(self):
        ok, reason, _ = evaluate_claim(
            [self.evidence("document_parser", "gross_weight", 42.0),
             self.evidence("weighbridge", "gross_weight", 42.0)],
            trusted_issuer_key=self.root.public_key(), tenant_id=self.tenant,
            claim_type="gross_weight", expected_subject_id=self.subject,
            expected_action_id=self.action, expected_document_digest=self.doc_digest,
            now=self.now, required_source_types=frozenset({"document_parser", "weighbridge"}),
            tolerance=0.01,
        )
        self.assertEqual((ok, reason), (True, "claim_supported"))

    def test_quantity_and_hs_require_claim_competent_sources(self):
        for claim, parser_value, external_type in (
            ("quantity", 20, "rfid_counter"),
            ("hs_code", "8542", "tariff_registry"),
        ):
            ok, reason, _ = evaluate_claim(
                [self.evidence("document_parser", claim, parser_value),
                 self.evidence(external_type, claim, parser_value)],
                trusted_issuer_key=self.root.public_key(), tenant_id=self.tenant,
                claim_type=claim, expected_subject_id=self.subject,
                expected_action_id=self.action, expected_document_digest=self.doc_digest,
                now=self.now, required_source_types=frozenset({"document_parser", external_type}),
            )
            self.assertEqual((ok, reason), (True, "claim_supported"))

    def test_weighbridge_cannot_be_reused_as_hs_evidence(self):
        pair = self.evidence("weighbridge", "hs_code", "8542")
        ok, reason, _ = self.verify(pair, "hs_code")
        self.assertFalse(ok)
        self.assertEqual(reason, "source_not_competent_for_claim")

    def test_cross_shipment_evidence_is_rejected(self):
        pair = self.evidence("weighbridge", "gross_weight", 42.0, subject_id="shipment-other")
        ok, reason, _ = self.verify(pair, "gross_weight")
        self.assertFalse(ok)
        self.assertEqual(reason, "subject_mismatch")

    def test_evidence_must_be_bound_to_exact_action(self):
        pair = self.evidence("weighbridge", "gross_weight", 42.0, action_id="different-action")
        ok, reason, _ = self.verify(pair, "gross_weight")
        self.assertFalse(ok)
        self.assertEqual(reason, "action_scope_mismatch")

    def test_stale_evidence_is_rejected(self):
        pair = self.evidence("weighbridge", "gross_weight", 42.0, expires_at=199)
        ok, reason, _ = self.verify(pair, "gross_weight")
        self.assertFalse(ok)
        self.assertEqual(reason, "evidence_expired_or_not_yet_valid")

    def test_parser_must_bind_input_and_output_digests(self):
        pair = self.evidence("document_parser", "quantity", 20, input_digest="wrong-input")
        ok, reason, _ = self.verify(pair, "quantity")
        self.assertFalse(ok)
        self.assertEqual(reason, "transformation_input_mismatch")

    def test_expired_scale_calibration_is_rejected(self):
        pair = self.evidence("weighbridge", "gross_weight", 42.0, calibration_valid_until=199)
        ok, reason, _ = self.verify(pair, "gross_weight")
        self.assertFalse(ok)
        self.assertEqual(reason, "calibration_invalid_or_expired")

    def test_conflicting_claim_values_escalate(self):
        ok, reason, _ = evaluate_claim(
            [self.evidence("document_parser", "gross_weight", 44.0),
             self.evidence("weighbridge", "gross_weight", 42.0)],
            trusted_issuer_key=self.root.public_key(), tenant_id=self.tenant,
            claim_type="gross_weight", expected_subject_id=self.subject,
            expected_action_id=self.action, expected_document_digest=self.doc_digest,
            now=self.now, required_source_types=frozenset({"document_parser", "weighbridge"}),
            tolerance=0.01,
        )
        self.assertEqual((ok, reason), (False, "claim_value_conflict"))

    def test_shared_admin_or_gateway_does_not_count_as_independent(self):
        spec = self.sources["weighbridge"]
        credential = issue_source_credential(
            issuer_id="synthetic-root", source_id="source-weighbridge",
            source_type="weighbridge", key_id="key-weighbridge",
            public_key=self.keys["weighbridge"].public_key(),
            allowed_claims=["gross_weight"], acquisition_domain=spec["acq"],
            administrative_domain="doc-admin", gateway_id="doc-gateway",
            key_admin_domain=spec["keyadmin"], tenant_id=self.tenant,
            serial="serial-weighbridge-shared", issued_at=100, expires_at=400,
            issuer_private_key=self.root,
        )
        record = issue_claim_evidence(
            credential=credential, source_private_key=self.keys["weighbridge"],
            claim_type="gross_weight", value=42.0, unit="kg",
            subject_id=self.subject, action_id=self.action,
            document_digest=self.doc_digest, input_digest=self.doc_digest,
            output_digest=canonical_sha256({"claim_type":"gross_weight","value":42.0,"unit":"kg"}),
            transformation_id="sensor-event", tool_version="firmware-1",
            observed_at=190, issued_at=190, expires_at=300,
            sequence_number=1, nonce="shared-admin-nonce",
            calibration_id="cal-1", calibration_valid_until=350,
        )
        ok, reason, _ = evaluate_claim(
            [self.evidence("document_parser", "gross_weight", 42.0),
             (record, credential)],
            trusted_issuer_key=self.root.public_key(), tenant_id=self.tenant,
            claim_type="gross_weight", expected_subject_id=self.subject,
            expected_action_id=self.action, expected_document_digest=self.doc_digest,
            now=self.now, required_source_types=frozenset({"document_parser", "weighbridge"}),
            tolerance=0.01,
        )
        self.assertEqual((ok, reason), (False, "shared_dependency:administrative_domain"))

    def test_replay_and_non_monotonic_sequence_are_rejected(self):
        pair = self.evidence("weighbridge", "gross_weight", 42.0)
        nonces, sequences = set(), {}
        kwargs = dict(
            trusted_issuer_key=self.root.public_key(), tenant_id=self.tenant,
            expected_claim="gross_weight", expected_subject_id=self.subject,
            expected_action_id=self.action, expected_document_digest=self.doc_digest,
            now=self.now, consumed_nonces=nonces, last_sequences=sequences,
        )
        self.assertTrue(verify_claim_evidence(pair[0], pair[1], **kwargs)[0])
        self.assertEqual(verify_claim_evidence(pair[0], pair[1], **kwargs)[1], "replay")

    def test_action_binding_prevents_evidence_or_action_substitution(self):
        evidence_pairs = [
            self.evidence("document_parser", "gross_weight", 42.0),
            self.evidence("weighbridge", "gross_weight", 42.0),
        ]
        digests = [canonical_sha256(record["envelope"]) for record, _ in evidence_pairs]
        binding = issue_action_binding(
            action_id=self.action, action_payload_digest=self.action_payload_digest, subject_id=self.subject, document_digest=self.doc_digest,
            policy_version="v4-policy-1", required_claims=["gross_weight"],
            evidence_digests=digests, issued_at=190, expires_at=300,
            private_key=self.authorizer,
        )
        valid = verify_action_binding(
            binding, trusted_authorizer_key=self.authorizer.public_key(),
            action_id=self.action, action_payload_digest=self.action_payload_digest, subject_id=self.subject,
            document_digest=self.doc_digest, policy_version="v4-policy-1",
            required_claims=["gross_weight"], evidence_digests=digests, now=self.now,
        )
        self.assertEqual(valid, (True, "valid_action_binding"))
        changed = verify_action_binding(
            binding, trusted_authorizer_key=self.authorizer.public_key(),
            action_id="different-action", action_payload_digest=self.action_payload_digest, subject_id=self.subject,
            document_digest=self.doc_digest, policy_version="v4-policy-1",
            required_claims=["gross_weight"], evidence_digests=digests, now=self.now,
        )
        self.assertEqual(changed, (False, "action_binding_mismatch"))

    def test_forged_source_credential_is_rejected(self):
        pair = self.evidence("weighbridge", "gross_weight", 42.0)
        credential = dict(pair[1])
        credential["body"] = dict(credential["body"], source_id="attacker-source")
        ok, reason, _ = self.verify((pair[0], credential), "gross_weight")
        self.assertFalse(ok)
        self.assertEqual(reason, "invalid_source_credential")


if __name__ == "__main__":
    unittest.main()
