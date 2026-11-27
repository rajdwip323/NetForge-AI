
"""
NETFORGE-AI
Phase 7.10.4 - Mock Deployment Executor
Functional Tests
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


class TestPhase7104(unittest.TestCase):

    def setUp(self):

        self.now = datetime(
            2026, 11, 27, 10, 30,
            tzinfo=timezone.utc,
        )

        self.plan = build_deployment_plan(
            plan_id="PLAN-7104-001",
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
                {
                    "action_id": "ACTION-003",
                    "resource": "interface",
                    "operation": "disable",
                    "parameters": {
                        "name": "GigabitEthernet0/2"
                    },
                },
            ],
            created_by="engineer_a",
            created_at="2026-11-27T09:30:00+00:00",
        )

        self.authorization = build_deployment_authorization(
            authorization_id="AUTH-7104-001",
            plan_id="PLAN-7104-001",
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

    def test_all_actions_successfully_complete(self):

        result = self.execute(
            deployment_id="DEPLOY-001"
        )

        self.assertTrue(result["allowed"])
        self.assertTrue(result["executed"])
        self.assertEqual(result["status"], "completed")

        self.assertEqual(
            len(result["action_results"]),
            3,
        )

        self.assertEqual(
            result["deployment_result"]["actions_applied"],
            3,
        )

        self.assertEqual(
            result["deployment_result"]["actions_failed"],
            0,
        )

        self.assertTrue(
            result["deployment_result"]["success"]
        )

    def test_single_action_failure_produces_partial_failure(self):

        result = self.execute(
            failure_action_ids=["ACTION-002"],
            deployment_id="DEPLOY-002",
        )

        self.assertTrue(result["allowed"])
        self.assertTrue(result["executed"])

        self.assertEqual(
            result["status"],
            "partially_failed",
        )

        self.assertEqual(
            result["deployment_result"]["actions_applied"],
            2,
        )

        self.assertEqual(
            result["deployment_result"]["actions_failed"],
            1,
        )

        self.assertFalse(
            result["deployment_result"]["success"]
        )

    def test_all_actions_failed(self):

        result = self.execute(
            failure_action_ids=[
                "ACTION-001",
                "ACTION-002",
                "ACTION-003",
            ],
            deployment_id="DEPLOY-003",
        )

        self.assertTrue(result["allowed"])
        self.assertTrue(result["executed"])

        self.assertEqual(result["status"], "failed")

        self.assertEqual(
            result["deployment_result"]["actions_applied"],
            0,
        )

        self.assertEqual(
            result["deployment_result"]["actions_failed"],
            3,
        )

    def test_successful_actions_have_success_status(self):

        result = self.execute()

        for action_result in result["action_results"]:

            with self.subTest(
                action_id=action_result["action_id"]
            ):

                self.assertEqual(
                    action_result["status"],
                    "success",
                )

                self.assertTrue(
                    action_result["success"]
                )

                self.assertIsNone(
                    action_result["error"]
                )

    def test_failed_action_contains_error(self):

        result = self.execute(
            failure_action_ids=["ACTION-001"]
        )

        failed_action = result["action_results"][0]

        self.assertEqual(
            failed_action["status"],
            "failed",
        )

        self.assertFalse(failed_action["success"])
        self.assertIsNotNone(failed_action["error"])

    def test_verification_remains_pending(self):

        result = self.execute()

        self.assertEqual(
            result["deployment_result"]["verification_status"],
            "pending",
        )

    def test_execution_mode_is_mock(self):

        result = self.execute()

        self.assertEqual(
            result["execution_mode"],
            "mock",
        )

        self.assertEqual(
            result["deployment_result"]["execution_mode"],
            "mock",
        )

    def test_blocked_authorization_prevents_execution(self):

        invalid_authorization = deepcopy(
            self.authorization
        )

        invalid_authorization["status"] = "pending"

        result = execute_mock_deployment(
            self.plan,
            invalid_authorization,
            current_time=self.now,
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(result["executed"])

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["action_results"], [])
        self.assertIsNone(result["deployment_result"])

    def test_invalid_plan_prevents_execution(self):

        invalid_plan = deepcopy(self.plan)

        invalid_plan["actions"][0]["operation"] = "reload"

        result = execute_mock_deployment(
            invalid_plan,
            self.authorization,
            current_time=self.now,
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["status"], "blocked")

    def test_deployment_result_contains_supplied_id(self):

        result = self.execute(
            deployment_id="DEPLOY-CUSTOM-001"
        )

        self.assertEqual(
            result["deployment_result"]["deployment_id"],
            "DEPLOY-CUSTOM-001",
        )

    def test_result_contains_all_action_results(self):

        result = self.execute()

        action_ids = [
            item["action_id"]
            for item in result["action_results"]
        ]

        self.assertEqual(
            action_ids,
            [
                "ACTION-001",
                "ACTION-002",
                "ACTION-003",
            ],
        )


if __name__ == "__main__":
    unittest.main()
