import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from src.dependency_graph_v5 import (
    issue_dependency_graph, verify_dependency_graph, resolve_ancestors,
    issue_graph_bound_source_credential, evaluate_quorum,
)
from src.evidence_provenance_v4 import issue_claim_evidence
from src.provenance import canonical_sha256


class DependencyGraphV5Tests(unittest.TestCase):
    def setUp(self):
        self.root = Ed25519PrivateKey.generate()
        self.tenant = "tenant-v5"
        self.now = 200
        self.subject = "shipment-v5"
        self.action = "submit-v5"
        self.action_digest = canonical_sha256({"operation": "submit", "amount": 42})
        self.doc_digest = canonical_sha256({"invoice": "synthetic-v5"})
        self.names = ("w1", "w2", "w3")
        self.keys = {name: Ed25519PrivateKey.generate() for name in self.names}
        self.graph = self.make_graph()
        self.credentials = self.make_credentials(self.root, self.graph, self.names)

    def make_graph(self, shared=None, root=None, nodes_override=None):
        if nodes_override is not None:
            nodes = nodes_override
        else:
            nodes = {}
            for name in self.names:
                nodes[f"source:source-{name}"] = [
                    f"admin:{name}", f"idp:{name}", f"kms:{name}", f"firmware:{name}",
                    f"acquisition:{name}", f"physical:{name}",
                ]
                for kind in ("admin", "idp", "kms", "firmware", "acquisition", "physical"):
                    nodes[f"{kind}:{name}"] = []
            if shared:
                for name in shared["members"]:
                    nodes[f"{shared['kind']}:{name}"] = [shared["ancestor"]]
                nodes[shared["ancestor"]] = []
        return issue_dependency_graph(
            graph_id="graph-v5", version="1", tenant_id=self.tenant,
            nodes=nodes, issued_at=100, expires_at=400,
            signer_private_key=root or self.root,
        )

    def make_credentials(self, root, graph, names, *, incomplete=(), shared_direct=()):
        digest = graph["body"]["graph_digest"]
        creds = {}
        for name in names:
            direct_admin = "shared-admin" if name in shared_direct else f"admin-{name}"
            creds[name] = issue_graph_bound_source_credential(
                graph_digest=digest, dependency_leaf_node=f"source:source-{name}",
                dependency_manifest_complete=name not in incomplete,
                issuer_id="synthetic-registry", source_id=f"source-{name}",
                source_type="weighbridge", key_id=f"key-{name}",
                public_key=self.keys[name].public_key(), allowed_claims=["gross_weight"],
                acquisition_domain=f"acq-{name}",
                administrative_domain=direct_admin,
                gateway_id=f"gateway-{name}", key_admin_domain=f"kms-admin-{name}",
                tenant_id=self.tenant, serial=f"serial-{name}",
                issued_at=100, expires_at=400, issuer_private_key=root,
            )
        return creds

    def record(self, name, value, credential=None, key=None, nonce=None):
        credential = credential or self.credentials[name]
        key = key or self.keys[name]
        unit = "kg"
        return issue_claim_evidence(
            credential=credential, source_private_key=key,
            claim_type="gross_weight", value=value, unit=unit,
            subject_id=self.subject, action_id=self.action,
            action_payload_digest=self.action_digest,
            document_digest=self.doc_digest, input_digest=self.doc_digest,
            output_digest=canonical_sha256({"claim_type": "gross_weight", "value": value, "unit": unit}),
            transformation_id=f"transform-{name}", tool_version="v5-test",
            observed_at=190, issued_at=190, expires_at=300,
            sequence_number=1, nonce=nonce or f"nonce-{name}",
            calibration_id="cal-1", calibration_valid_until=350,
        )

    def evaluate(self, records, policy, threshold=2, graph=None, root=None):
        return evaluate_quorum(
            records, policy=policy, threshold=threshold,
            trusted_registry_key=(root or self.root).public_key(),
            tenant_id=self.tenant, graph_record=graph or self.graph,
            claim_type="gross_weight", expected_value=42.0, expected_unit="kg",
            expected_subject_id=self.subject, expected_action_id=self.action,
            expected_action_payload_digest=self.action_digest,
            expected_document_digest=self.doc_digest, now=self.now,
        )

    def test_source_credential_leaf_must_match_source_id(self):
        with self.assertRaises(ValueError):
            issue_graph_bound_source_credential(
                graph_digest=self.graph["body"]["graph_digest"],
                dependency_leaf_node="source:other-witness",
                issuer_id="synthetic-registry", source_id="source-w1",
                source_type="weighbridge", key_id="key-w1",
                public_key=self.keys["w1"].public_key(), allowed_claims=["gross_weight"],
                acquisition_domain="acq-w1", administrative_domain="admin-w1",
                gateway_id="gateway-w1", key_admin_domain="kms-admin-w1",
                tenant_id=self.tenant, serial="serial-bad",
                issued_at=100, expires_at=400, issuer_private_key=self.root,
            )

    def test_graph_signature_and_transitive_ancestor_resolution(self):
        ok, reason, body = verify_dependency_graph(
            self.graph, trusted_registry_key=self.root.public_key(),
            tenant_id=self.tenant, now=self.now)
        self.assertEqual((ok, reason), (True, "valid_dependency_graph"))
        ancestors = resolve_ancestors(body["nodes"], "source:source-w1")
        self.assertIn("admin:w1", ancestors)
        self.assertIn("physical:w1", ancestors)

    def test_cycle_and_unresolved_parent_are_rejected(self):
        cyclic = {
            "source:w1": ["admin:w1"], "admin:w1": ["parent:x"],
            "parent:x": ["admin:w1"],
        }
        graph = issue_dependency_graph(
            graph_id="cycle", version="1", tenant_id=self.tenant,
            nodes=cyclic, issued_at=100, expires_at=400,
            signer_private_key=self.root,
        )
        ok, reason, _ = verify_dependency_graph(
            graph, trusted_registry_key=self.root.public_key(),
            tenant_id=self.tenant, now=self.now)
        self.assertEqual((ok, reason), (False, "dependency_cycle"))
        unresolved = {"source:w1": ["missing-parent"]}
        graph2 = issue_dependency_graph(
            graph_id="missing", version="1", tenant_id=self.tenant,
            nodes=unresolved, issued_at=100, expires_at=400,
            signer_private_key=self.root,
        )
        self.assertEqual(
            verify_dependency_graph(graph2, trusted_registry_key=self.root.public_key(),
                                    tenant_id=self.tenant, now=self.now)[1],
            "dependency_parent_unresolved",
        )

    def test_honest_graph_aware_quorum_passes(self):
        records = [(self.record(name, 42.0), self.credentials[name]) for name in self.names]
        self.assertEqual(self.evaluate(records, "graph_aware")[:2], (True, "quorum_valid"))

    def test_key_unique_and_field_distinct_pass_but_graph_aware_detects_shared_parent(self):
        graph = self.make_graph(shared={
            "members": ["w1", "w2"], "kind": "admin", "ancestor": "parent:holding",
        })
        creds = self.make_credentials(self.root, graph, self.names)
        records = [
            (self.record("w1", 42.0, creds["w1"]), creds["w1"]),
            (self.record("w2", 42.0, creds["w2"]), creds["w2"]),
            (self.record("w3", 99.0, creds["w3"]), creds["w3"]),
        ]
        self.assertTrue(self.evaluate(records, "key_unique", graph=graph)[0])
        self.assertTrue(self.evaluate(records, "field_distinct", graph=graph)[0])
        ok, reason, _ = self.evaluate(records, "graph_aware", graph=graph)
        self.assertFalse(ok)
        self.assertEqual(reason, "shared_dependency_graph:parent:holding")

    def test_shared_identity_provider_is_detected_transitively(self):
        graph = self.make_graph(shared={
            "members": ["w1", "w2"], "kind": "idp", "ancestor": "idp:shared-cloud",
        })
        creds = self.make_credentials(self.root, graph, self.names)
        records = [(self.record(n, 42.0, creds[n]), creds[n]) for n in ("w1", "w2")]
        ok, reason, _ = self.evaluate(records, "graph_aware", graph=graph)
        self.assertFalse(ok)
        self.assertEqual(reason, "shared_dependency_graph:idp:shared-cloud")

    def test_incomplete_dependency_manifest_fails_closed_only_for_graph_policy(self):
        creds = self.make_credentials(self.root, self.graph, self.names, incomplete=("w1",))
        records = [(self.record(n, 42.0, creds[n]), creds[n]) for n in ("w1", "w2")]
        self.assertTrue(self.evaluate(records, "field_distinct")[0])
        ok, reason, _ = self.evaluate(records, "graph_aware")
        self.assertFalse(ok)
        self.assertEqual(reason, "dependency_manifest_incomplete")

    def test_graph_signature_tampering_is_rejected(self):
        tampered = {"body": dict(self.graph["body"]), "signature_b64": self.graph["signature_b64"]}
        tampered["body"]["graph_id"] = "attacker-replaced"
        ok, reason, _ = verify_dependency_graph(
            tampered, trusted_registry_key=self.root.public_key(),
            tenant_id=self.tenant, now=self.now)
        self.assertFalse(ok)
        self.assertEqual(reason, "invalid_dependency_graph_signature_or_schema")

    def test_credential_must_bind_to_the_verified_graph_digest(self):
        wrong_graph = self.make_graph(shared={
            "members": ["w1", "w2"], "kind": "admin", "ancestor": "parent:holding",
        })
        creds = self.make_credentials(self.root, wrong_graph, self.names)
        records = [(self.record(n, 42.0, creds[n]), creds[n]) for n in ("w1", "w2")]
        ok, reason, _ = self.evaluate(records, "graph_aware", graph=self.graph)
        self.assertFalse(ok)
        self.assertEqual(reason, "dependency_graph_binding_mismatch")

    def test_two_compromised_witnesses_pass_2of3_but_not_3of3(self):
        records = [
            (self.record("w1", 42.0), self.credentials["w1"]),
            (self.record("w2", 42.0), self.credentials["w2"]),
            (self.record("w3", 99.0), self.credentials["w3"]),
        ]
        self.assertTrue(self.evaluate(records, "field_distinct", threshold=2)[0])
        ok, reason, _ = self.evaluate(records, "field_distinct", threshold=3)
        self.assertFalse(ok)
        self.assertEqual(reason, "quorum_disagreement")

    def test_one_compromised_witness_is_tolerated_by_2of3(self):
        records = [
            (self.record("w1", 42.0), self.credentials["w1"]),
            (self.record("w2", 99.0), self.credentials["w2"]),
            (self.record("w3", 42.0), self.credentials["w3"]),
        ]
        self.assertTrue(self.evaluate(records, "graph_aware", threshold=2)[0])
        self.assertFalse(self.evaluate(records, "field_distinct", threshold=3)[0])

    def test_full_roster_compromise_can_satisfy_3of3(self):
        records = [(self.record(n, 99.0), self.credentials[n]) for n in self.names]
        ok, reason, _ = evaluate_quorum(
            records, policy="field_distinct", threshold=3,
            trusted_registry_key=self.root.public_key(), tenant_id=self.tenant,
            graph_record=self.graph, claim_type="gross_weight", expected_value=99.0,
            expected_unit="kg", expected_subject_id=self.subject,
            expected_action_id=self.action, expected_action_payload_digest=self.action_digest,
            expected_document_digest=self.doc_digest, now=self.now,
        )
        self.assertEqual((ok, reason), (True, "quorum_valid"))

    def test_one_incomplete_member_can_be_excluded_when_two_complete_remain(self):
        creds = self.make_credentials(self.root, self.graph, self.names, incomplete=("w1",))
        records = [(self.record(n, 42.0, creds[n]), creds[n]) for n in self.names]
        self.assertTrue(self.evaluate(records, "graph_aware", threshold=2)[0])
        ok, reason, _ = self.evaluate(records, "graph_aware", threshold=3)
        self.assertFalse(ok)
        self.assertEqual(reason, "dependency_manifest_incomplete")

    def test_key_unique_is_weaker_than_direct_field_diversity(self):
        creds = self.make_credentials(self.root, self.graph, self.names, shared_direct=("w1", "w2"))
        records = [(self.record(n, 42.0, creds[n]), creds[n]) for n in ("w1", "w2")]
        self.assertTrue(self.evaluate(records, "key_unique")[0])
        ok, reason, _ = self.evaluate(records, "field_distinct")
        self.assertFalse(ok)
        self.assertEqual(reason, "insufficient_identity_independence")
        self.assertFalse(self.evaluate(records, "graph_aware")[0])

    def test_graph_aware_policy_cannot_prevent_full_roster_collusion(self):
        records = [(self.record(n, 99.0), self.credentials[n]) for n in self.names]
        ok, reason, _ = evaluate_quorum(
            records, policy="graph_aware", threshold=2,
            trusted_registry_key=self.root.public_key(), tenant_id=self.tenant,
            graph_record=self.graph, claim_type="gross_weight", expected_value=99.0,
            expected_unit="kg", expected_subject_id=self.subject,
            expected_action_id=self.action, expected_action_payload_digest=self.action_digest,
            expected_document_digest=self.doc_digest, now=self.now,
        )
        self.assertEqual((ok, reason), (True, "quorum_valid"))

    def test_graph_root_compromise_can_hide_a_shared_parent(self):
        # Model compromise of the existing issuer private key, not replacement
        # of the verifier's trust anchor. The verifier continues to pin self.root.
        forged_graph = self.make_graph(root=self.root)
        creds = self.make_credentials(self.root, forged_graph, self.names)
        records = [(self.record(n, 42.0, creds[n]), creds[n]) for n in ("w1", "w2")]

        # The real dependency exists in the attacker's ground-truth model but is
        # omitted from the graph signed by the compromised, already-trusted key.
        self.assertNotIn("parent:common-control", forged_graph["body"]["nodes"])

        ok, reason, _ = self.evaluate(
            records, "graph_aware", graph=forged_graph, root=self.root)
        self.assertEqual((ok, reason), (True, "quorum_valid"))


    def test_graph_issuer_rejects_malformed_node_and_parent_identifiers(self):
        with self.assertRaises(ValueError):
            issue_dependency_graph(
                graph_id="bad", version="1", tenant_id=self.tenant,
                nodes={"source:w1": "admin:w1"}, issued_at=100, expires_at=400,
                signer_private_key=self.root,
            )
        with self.assertRaises(ValueError):
            issue_dependency_graph(
                graph_id="bad", version="1", tenant_id=self.tenant,
                nodes={"source:w1": [""]}, issued_at=100, expires_at=400,
                signer_private_key=self.root,
            )

    def test_graph_verifier_rejects_invalid_identity_and_validity_metadata(self):
        bad_identity = {
            "body": dict(self.graph["body"], graph_id=""),
            "signature_b64": self.graph["signature_b64"],
        }
        ok, reason, _ = verify_dependency_graph(
            bad_identity, trusted_registry_key=self.root.public_key(),
            tenant_id=self.tenant, now=self.now)
        self.assertEqual((ok, reason), (False, "dependency_graph_identity_invalid"))

        bad_window = {
            "body": dict(self.graph["body"], expires_at=True),
            "signature_b64": self.graph["signature_b64"],
        }
        ok, reason, _ = verify_dependency_graph(
            bad_window, trusted_registry_key=self.root.public_key(),
            tenant_id=self.tenant, now=self.now)
        self.assertEqual((ok, reason), (False, "dependency_graph_validity_invalid"))

    def test_quorum_threshold_must_be_a_positive_non_boolean_integer(self):
        records = [(self.record(n, 42.0), self.credentials[n]) for n in self.names]
        for threshold in (0, -1, 2.0, True):
            with self.subTest(threshold=threshold):
                ok, reason, _ = self.evaluate(records, "field_distinct", threshold=threshold)
                self.assertEqual((ok, reason), (False, "invalid_quorum_threshold"))


    def test_graph_aware_detects_shared_gateway_and_physical_measurement_source(self):
        for kind, ancestor in (
            ("acquisition", "gateway:shared-acquisition"),
            ("physical", "scale:shared-source"),
        ):
            with self.subTest(kind=kind):
                graph = self.make_graph(shared={
                    "members": ["w1", "w2"], "kind": kind, "ancestor": ancestor,
                })
                creds = self.make_credentials(self.root, graph, self.names)
                records = [
                    (self.record(name, 42.0, creds[name]), creds[name])
                    for name in ("w1", "w2")
                ]
                ok, reason, _ = self.evaluate(records, "graph_aware", graph=graph)
                self.assertFalse(ok)
                self.assertEqual(reason, "shared_dependency_graph:" + ancestor)

    def test_graph_aware_selects_an_independent_matching_pair_from_three(self):
        graph = self.make_graph(shared={
            "members": ["w1", "w2"], "kind": "admin", "ancestor": "parent:holding",
        })
        creds = self.make_credentials(self.root, graph, self.names)
        records = [
            (self.record("w1", 42.0, creds["w1"]), creds["w1"]),
            (self.record("w2", 99.0, creds["w2"]), creds["w2"]),
            (self.record("w3", 42.0, creds["w3"]), creds["w3"]),
        ]
        ok, reason, supporters = self.evaluate(records, "graph_aware", graph=graph)
        self.assertEqual((ok, reason), (True, "quorum_valid"))
        self.assertEqual({item["source_id"] for item in supporters}, {"source-w1", "source-w3"})


if __name__ == "__main__":
    unittest.main()
