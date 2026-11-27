
"""
NETFORGE-AI
Phase 7.10.4 - Mock Deployment Executor
Edge Case Tests
"""

import sys
import unittest

from datetime import datetime, timezone
from copy import deepcopy

sys.path.insert(0, "src")

from deployment.deployment_models import (
    build_deployment_plan,
    build_deployment_authorization,
)

from deployment.deployment_safety_gate import (
    calculate_plan_fingerprint,
)

from deployment.mock_deployment_executor import (
    execute_mock_deployment,
)


class TestPhase7104Edges(unittest.TestCase):

    def setUp(self):

        self.now = datetime(
            2026, 11, 27, 10, 30,
            tzinfo=timezone.utc,
        )

        self.plan = build_deployment_plan(
            plan_id="PLAN-EDGE-7104",
            target="R1",
            actions=[
                {
                    "action_id": "ACTION-001",
                    "resource": "interface",
                    "operation": "enable",
                    "parameters": {
                        "name": "GigabitEthernet0/1"
                    },
                },
                {
                    "action_id": "ACTION-002",
                    "resource": "vlan",
                    "operation": "create",
                    "parameters": {
                        "vlan_id": 100,
                        "name": "OFFICE",
                    },
                },
            ],
            created_by="engineer_a",
            created_at="2026-11-27T09:30:00+00:00",
        )

        self.authorization = build_deployment_authorization(
            authorization_id="AUTH-EDGE-7104",
            plan_id="PLAN-EDGE-7104",
            target="R1",
            plan_fingerprint=calculate_plan_fingerprint(
                self.plan
            ),
            requested_by="engineer_a",
            approved_by="supervisor_b",
            status="approved",
            issued_at="2026-11-27T10:00:00+00:00",
            expires_at="2026-11-27T11:30:00+00:00",
        )

    def execute(self, **kwargs):

        return execute_mock_deployment(
            self.plan,
            self.authorization,
            current_time=self.now,
            **kwargs,
        )

    def assert_blocked(self, result):

        self.assertFalse(result["allowed"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["action_results"], [])
        self.assertIsNone(result["deployment_result"])

    def test_none_failure_action_ids(self):

        result = self.execute(
            failure_action_ids=None
        )

        self.assertTrue(result["allowed"])
        self.assertEqual(result["status"], "completed")

    def test_empty_failure_action_ids(self):

        result = self.execute(
            failure_action_ids=[]
        )

        self.assertTrue(result["allowed"])
        self.assertEqual(result["status"], "completed")

    def test_tuple_failure_action_ids(self):

        result = self.execute(
            failure_action_ids=("ACTION-001",)
        )

        self.assertEqual(
            result["status"],
            "partially_failed",
        )

    def test_set_failure_action_ids(self):

        result = self.execute(
            failure_action_ids={"ACTION-001"}
        )

        self.assertEqual(
            result["status"],
            "partially_failed",
        )

    def test_invalid_failure_action_ids_type(self):

        result = self.execute(
            failure_action_ids="ACTION-001"
        )

        self.assert_blocked(result)

    def test_integer_failure_action_id_rejected(self):

        result = self.execute(
            failure_action_ids=[123]
        )

        self.assert_blocked(result)

    def test_empty_failure_action_id_rejected(self):

        result = self.execute(
            failure_action_ids=[""]
        )

        self.assert_blocked(result)

    def test_whitespace_failure_action_id_rejected(self):

        result = self.execute(
            failure_action_ids=["   "]
        )

        self.assert_blocked(result)

    def test_duplicate_failure_action_ids_rejected(self):

        result = self.execute(
            failure_action_ids=[
                "ACTION-001",
                "ACTION-001",
            ]
        )

        self.assert_blocked(result)

    def test_case_insensitive_duplicate_failure_ids_rejected(self):

        result = self.execute(
            failure_action_ids=[
                "ACTION-001",
                "action-001",
            ]
        )

        self.assert_blocked(result)

    def test_unknown_failure_action_id_rejected(self):

        result = self.execute(
            failure_action_ids=["UNKNOWN-ACTION"]
        )

        self.assert_blocked(result)

    def test_case_insensitive_action_id_matching(self):

        result = self.execute(
            failure_action_ids=["action-001"]
        )

        self.assertEqual(
            result["action_results"][0]["status"],
            "failed",
        )

    def test_invalid_deployment_id_type_rejected(self):

        result = self.execute(
            deployment_id=123
        )

        self.assert_blocked(result)

    def test_empty_deployment_id_rejected(self):

        result = self.execute(
            deployment_id=""
        )

        self.assert_blocked(result)

    def test_whitespace_deployment_id_rejected(self):

        result = self.execute(
            deployment_id="   "
        )

        self.assert_blocked(result)

    def test_missing_plan_rejected(self):

        result = execute_mock_deployment(
            None,
            self.authorization,
            current_time=self.now,
        )

        self.assert_blocked(result)

    def test_missing_authorization_rejected(self):

        result = execute_mock_deployment(
            self.plan,
            None,
            current_time=self.now,
        )

        self.assert_blocked(result)

    def test_expired_authorization_rejected(self):

        expired_authorization = deepcopy(
            self.authorization
        )

        expired_authorization["expires_at"] = (
            "2026-11-27T10:00:00+00:00"
        )

        result = execute_mock_deployment(
            self.plan,
            expired_authorization,
            current_time=self.now,
        )

        self.assert_blocked(result)

    def test_plan_fingerprint_mismatch_rejected(self):

        modified_plan = deepcopy(self.plan)

        modified_plan["target"] = "R2"

        result = execute_mock_deployment(
            modified_plan,
            self.authorization,
            current_time=self.now,
        )

        self.assert_blocked(result)

    def test_invalid_current_time_rejected(self):

        result = execute_mock_deployment(
            self.plan,
            self.authorization,
            current_time="invalid-time",
        )

        self.assert_blocked(result)

    def test_failure_injection_does_not_affect_other_actions(self):

        result = self.execute(
            failure_action_ids=["ACTION-001"]
        )

        self.assertEqual(
            result["action_results"][0]["status"],
            "failed",
        )

        self.assertEqual(
            result["action_results"][1]["status"],
            "success",
        )

    def test_generated_deployment_id_has_mock_prefix(self):

        result = self.execute()

        deployment_id = (
            result["deployment_result"]["deployment_id"]
        )

        self.assertTrue(
            deployment_id.startswith("MOCK-")
        )

    def test_action_results_are_empty_when_blocked(self):

        invalid_authorization = deepcopy(
            self.authorization
        )

        invalid_authorization["status"] = "pending"

        result = execute_mock_deployment(
            self.plan,
            invalid_authorization,
            current_time=self.now,
        )

        self.assertEqual(
            result["action_results"],
            [],
        )

    def test_invalid_failure_injection_prevents_all_execution(self):

        result = self.execute(
            failure_action_ids=["ACTION-001", "UNKNOWN"]
        )

        self.assert_blocked(result)

    def test_failure_injection_does_not_change_authorization(self):

        original_authorization = deepcopy(
            self.authorization
        )

        self.execute(
            failure_action_ids=["ACTION-001"]
        )

        self.assertEqual(
            self.authorization,
            original_authorization,
        )


if __name__ == "__main__":
    unittest.main()
