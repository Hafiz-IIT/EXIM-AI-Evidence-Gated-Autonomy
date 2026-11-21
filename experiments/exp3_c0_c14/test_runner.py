import unittest
from runner import build_plan, execute

class RunnerTests(unittest.TestCase):
    def test_routing_plan_is_28_calls_and_plan_only(self):
        plan=build_plan("routing")
        self.assertEqual(plan["calls"],28)
        self.assertFalse(plan["execution_enabled"])
        self.assertEqual(plan["status"],"PLAN_ONLY_NO_NETWORK")

    def test_primary_plan_is_630_calls_and_plan_only(self):
        plan=build_plan("primary")
        self.assertEqual(plan["calls"],630)
        self.assertFalse(plan["execution_enabled"])

    def test_prompt_pack_v2_routing_plan_is_28_calls(self):
        plan=build_plan("routing-v3")
        self.assertEqual(plan["calls"],28)
        self.assertEqual(plan["manifest_id"],"E3-DRY-RUN-MANIFEST-v3-prompt-pack-v2")
        self.assertFalse(plan["execution_enabled"])

    def test_protocol_v2_primary_plan_is_630_calls(self):
        plan=build_plan("primary-v3")
        self.assertEqual(plan["calls"],630)
        self.assertEqual(plan["manifest_id"],"E3-PRIMARY-MATRIX-v3-PROMPT-PACK-v2")
        self.assertFalse(plan["execution_enabled"])

    def test_execution_is_hard_blocked(self):
        with self.assertRaisesRegex(RuntimeError,"EXECUTION BLOCKED"):
            execute({"execution_enabled":False})

if __name__=="__main__": unittest.main()
