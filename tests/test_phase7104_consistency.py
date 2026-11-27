
"""
NETFORGE-AI
Phase 7.10.4 - Mock Deployment Executor
Consistency Tests
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


class TestPhase7104Consistency(unittest.TestCase):

    def setUp(self):

        self.now = datetime(
            2026, 11, 27, 10, 30,
            tzinfo=timezone.utc,
        )

        self.plan = build_deployment_plan(
            plan_id="PLAN-CONS-7104",
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
            authorization_id="AUTH-CONS-7104",
            plan_id="PLAN-CONS-7104",
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
            deployment_id="DEPLOY-CONS-001",
            **kwargs,
        )

    def test_same_input_produces_same_execution_decision(self):

        first = self.execute()
        second = self.execute()

        self.assertEqual(
            first["allowed"],
            second["allowed"],
        )

        self.assertEqual(
            first["executed"],
            second["executed"],
        )

        self.assertEqual(
            first["status"],
            second["status"],
        )

    def test_same_input_produces_same_action_results(self):

        first = self.execute()
        second = self.execute()

        self.assertEqual(
            first["action_results"],
            second["action_results"],
        )

    def test_same_input_produces_same_deployment_summary(self):

        first = self.execute()
        second = self.execute()

        first_summary = deepcopy(
            first["deployment_result"]
        )

        second_summary = deepcopy(
            second["deployment_result"]
        )

        first_created_at = first_summary.pop("created_at")
        second_created_at = second_summary.pop("created_at")

        self.assertEqual(
            first_summary,
            second_summary,
        )

        self.assertIsInstance(first_created_at, str)
        self.assertIsInstance(second_created_at, str)

    def test_action_order_is_preserved(self):

        result = self.execute()

        action_ids = [
            item["action_id"]
            for item in result["action_results"]
        ]

        self.assertEqual(
            action_ids,
            ["ACTION-001", "ACTION-002"],
        )

    def test_failure_injection_is_deterministic(self):

        first = self.execute(
            failure_action_ids=["ACTION-002"]
        )

        second = self.execute(
            failure_action_ids=["ACTION-002"]
        )

        self.assertEqual(
            first["action_results"],
            second["action_results"],
        )

        self.assertEqual(
            first["status"],
            second["status"],
        )

    def test_failure_injection_does_not_modify_plan(self):

        original_plan = deepcopy(self.plan)

        self.execute(
            failure_action_ids=["ACTION-001"]
        )

        self.assertEqual(
            self.plan,
            original_plan,
        )

    def test_execution_does_not_modify_authorization(self):

        original_authorization = deepcopy(
            self.authorization
        )

        self.execute()

        self.assertEqual(
            self.authorization,
            original_authorization,
        )

    def test_execution_does_not_change_plan_fingerprint(self):

        original_fingerprint = calculate_plan_fingerprint(
            self.plan
        )

        self.execute(
            failure_action_ids=["ACTION-002"]
        )

        updated_fingerprint = calculate_plan_fingerprint(
            self.plan
        )

        self.assertEqual(
            original_fingerprint,
            updated_fingerprint,
        )

    def test_all_action_results_have_consistent_structure(self):

        result = self.execute()

        expected_fields = {
            "action_id",
            "resource",
            "operation",
            "status",
            "success",
            "error",
        }

        for action_result in result["action_results"]:

            with self.subTest(
                action_id=action_result["action_id"]
            ):

                self.assertEqual(
                    set(action_result.keys()),
                    expected_fields,
                )

    def test_success_and_failure_counts_match_action_results(self):

        result = self.execute(
            failure_action_ids=["ACTION-002"]
        )

        successful_count = sum(
            1
            for item in result["action_results"]
            if item["success"] is True
        )

        failed_count = sum(
            1
            for item in result["action_results"]
            if item["success"] is False
        )

        deployment_result = result["deployment_result"]

        self.assertEqual(
            deployment_result["actions_applied"],
            successful_count,
        )

        self.assertEqual(
            deployment_result["actions_failed"],
            failed_count,
        )

    def test_mock_execution_never_changes_execution_mode(self):

        result = self.execute()

        self.assertEqual(
            result["execution_mode"],
            "mock",
        )

        self.assertEqual(
            result["deployment_result"]["execution_mode"],
            "mock",
        )

    def test_allowed_equals_safety_gate_decision(self):

        result = self.execute()

        self.assertEqual(
            result["allowed"],
            result["safety_result"]["allowed"],
        )


if __name__ == "__main__":
    unittest.main()
