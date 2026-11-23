import copy
import unittest

from src.action_authorization import (
    authorize_action,
    sign_catalog,
    verify_catalog,
    verify_execution_binding,
)


KEY = b"synthetic-test-key-not-for-production"
VERSION = "catalog-2026-11-01"
ACTIONS = {
    "save_temporary_record": {
        "risk_level": "LOW", "reversibility": "HIGH", "external_effect": "LOW"
    },
    "advance_operational_workflow": {
        "risk_level": "HIGH", "reversibility": "LOW", "external_effect": "HIGH"
    },
}
HIGH_ACTION = {"name": "advance_operational_workflow", **ACTIONS["advance_operational_workflow"]}


class SignedActionCatalogTests(unittest.TestCase):
    def setUp(self):
        self.manifest = sign_catalog(VERSION, ACTIONS, KEY)

    def test_valid_manifest_and_authorization(self):
        self.assertTrue(verify_catalog(self.manifest, KEY, VERSION))
        token = authorize_action(
            HIGH_ACTION, trusted_action_id=HIGH_ACTION["name"], manifest=self.manifest,
            key=KEY, expected_catalog_version=VERSION,
        )
        self.assertIsNotNone(token)
        self.assertTrue(verify_execution_binding(
            token, invoked_action_id=HIGH_ACTION["name"],
            current_catalog_version=VERSION, key=KEY,
        ))

    def test_catalog_tampering_invalidates_signature(self):
        tampered = copy.deepcopy(self.manifest)
        tampered["payload"]["actions"]["advance_operational_workflow"]["risk_level"] = "LOW"
        self.assertFalse(verify_catalog(tampered, KEY, VERSION))
        self.assertIsNone(authorize_action(
            {**HIGH_ACTION, "risk_level": "LOW"},
            trusted_action_id=HIGH_ACTION["name"], manifest=tampered,
            key=KEY, expected_catalog_version=VERSION,
        ))

    def test_stale_catalog_version_fails_closed(self):
        self.assertFalse(verify_catalog(self.manifest, KEY, "catalog-newer"))
        self.assertIsNone(authorize_action(
            HIGH_ACTION, trusted_action_id=HIGH_ACTION["name"], manifest=self.manifest,
            key=KEY, expected_catalog_version="catalog-newer",
        ))

    def test_action_alias_substitution_fails_closed(self):
        alias = {
            "name": "save_temporary_record",
            **ACTIONS["save_temporary_record"],
        }
        self.assertIsNone(authorize_action(
            alias, trusted_action_id="advance_operational_workflow",
            manifest=self.manifest, key=KEY, expected_catalog_version=VERSION,
        ))

    def test_executor_tool_substitution_fails_closed(self):
        token = authorize_action(
            HIGH_ACTION, trusted_action_id=HIGH_ACTION["name"], manifest=self.manifest,
            key=KEY, expected_catalog_version=VERSION,
        )
        self.assertFalse(verify_execution_binding(
            token, invoked_action_id="save_temporary_record",
            current_catalog_version=VERSION, key=KEY,
        ))

    def test_catalog_version_change_after_authorization_fails_closed(self):
        token = authorize_action(
            HIGH_ACTION, trusted_action_id=HIGH_ACTION["name"], manifest=self.manifest,
            key=KEY, expected_catalog_version=VERSION,
        )
        self.assertFalse(verify_execution_binding(
            token, invoked_action_id=HIGH_ACTION["name"],
            current_catalog_version="catalog-2026-11-02", key=KEY,
        ))

    def test_tampered_authorization_token_fails_closed(self):
        token = authorize_action(
            HIGH_ACTION, trusted_action_id=HIGH_ACTION["name"], manifest=self.manifest,
            key=KEY, expected_catalog_version=VERSION,
        )
        token["payload"]["action_id"] = "save_temporary_record"
        self.assertFalse(verify_execution_binding(
            token, invoked_action_id="save_temporary_record",
            current_catalog_version=VERSION, key=KEY,
        ))


if __name__ == "__main__":
    unittest.main()
