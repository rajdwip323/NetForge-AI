
import sys
import unittest
from copy import deepcopy
from datetime import datetime, timezone

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


class TestPhase7104Security(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 11, 27, 10, 30, tzinfo=timezone.utc
        )

        self.plan = build_deployment_plan(
            plan_id="PLAN-SEC-7104",
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
                        "name": "USERS",
                    },
                },
            ],
            created_by="engineer_a",
            created_at="2026-11-27T09:30:00+00:00",
        )

        self.authorization = build_deployment_authorization(
            authorization_id="AUTH-SEC-7104",
            plan_id="PLAN-SEC-7104",
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

    def execute(self, plan=None, authorization=None, **kwargs):
        return execute_mock_deployment(
            plan=self.plan if plan is None else plan,
            authorization=(
                self.authorization
                if authorization is None
                else authorization
            ),
            current_time=self.now,
            **kwargs
        )

    def assert_blocked(self, result):
        self.assertFalse(result["allowed"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["action_results"], [])
        self.assertIsNone(result["deployment_result"])

    def test_pending_authorization_is_blocked(self):
        auth = deepcopy(self.authorization)
        auth["status"] = "pending"

        self.assert_blocked(
            self.execute(authorization=auth)
        )

    def test_rejected_authorization_is_blocked(self):
        auth = deepcopy(self.authorization)
        auth["status"] = "rejected"

        self.assert_blocked(
            self.execute(authorization=auth)
        )

    def test_revoked_authorization_is_blocked(self):
        auth = deepcopy(self.authorization)
        auth["status"] = "revoked"

        self.assert_blocked(
            self.execute(authorization=auth)
        )

    def test_requester_cannot_approve_own_deployment(self):
        auth = deepcopy(self.authorization)
        auth["approved_by"] = auth["requested_by"]

        self.assert_blocked(
            self.execute(authorization=auth)
        )

    def test_tampered_plan_parameters_are_blocked(self):
        plan = deepcopy(self.plan)
        plan["actions"][0]["parameters"]["name"] = (
            "GigabitEthernet0/2"
        )

        self.assert_blocked(
            self.execute(plan=plan)
        )

    def test_tampered_plan_target_is_blocked(self):
        plan = deepcopy(self.plan)
        plan["target"] = "R2"

        self.assert_blocked(
            self.execute(plan=plan)
        )

    def test_tampered_authorization_fingerprint_is_blocked(self):
        auth = deepcopy(self.authorization)
        auth["plan_fingerprint"] = "invalid-fingerprint"

        self.assert_blocked(
            self.execute(authorization=auth)
        )

    def test_authorization_plan_id_mismatch_is_blocked(self):
        auth = deepcopy(self.authorization)
        auth["plan_id"] = "ANOTHER-PLAN"

        self.assert_blocked(
            self.execute(authorization=auth)
        )

    def test_authorization_target_mismatch_is_blocked(self):
        auth = deepcopy(self.authorization)
        auth["target"] = "R2"

        self.assert_blocked(
            self.execute(authorization=auth)
        )

    def test_expired_authorization_is_blocked(self):
        auth = deepcopy(self.authorization)
        auth["expires_at"] = "2026-11-27T10:00:00+00:00"

        self.assert_blocked(
            self.execute(authorization=auth)
        )

    def test_vendor_command_field_is_rejected(self):
        plan = deepcopy(self.plan)
        plan["actions"][0]["command"] = (
            "configure terminal"
        )

        self.assert_blocked(
            self.execute(plan=plan)
        )

    def test_cli_command_field_is_rejected(self):
        plan = deepcopy(self.plan)
        plan["actions"][0]["cli_command"] = (
            "interface GigabitEthernet0/1"
        )

        self.assert_blocked(
            self.execute(plan=plan)
        )

    def test_newline_in_interface_name_is_rejected(self):
        plan = deepcopy(self.plan)
        plan["actions"][0]["parameters"]["name"] = (
            "GigabitEthernet0/1\nshutdown"
        )

        self.assert_blocked(
            self.execute(plan=plan)
        )

    def test_unknown_failure_injection_is_blocked(self):
        result = self.execute(
            failure_action_ids=["UNKNOWN-ACTION"]
        )

        self.assert_blocked(result)

    def test_invalid_failure_injection_type_is_blocked(self):
        result = self.execute(
            failure_action_ids="ACTION-001"
        )

        self.assert_blocked(result)

    def test_blocked_execution_has_no_deployment_result(self):
        auth = deepcopy(self.authorization)
        auth["status"] = "rejected"

        result = self.execute(authorization=auth)

        self.assertIsNone(result["deployment_result"])
        self.assertEqual(result["action_results"], [])
        self.assertFalse(result["executed"])

    def test_failure_injection_does_not_modify_plan(self):
        original_plan = deepcopy(self.plan)

        self.execute(
            failure_action_ids=["ACTION-001"]
        )

        self.assertEqual(self.plan, original_plan)

    def test_failure_injection_does_not_modify_authorization(self):
        original_auth = deepcopy(self.authorization)

        self.execute(
            failure_action_ids=["ACTION-001"]
        )

        self.assertEqual(
            self.authorization,
            original_auth,
        )

    def test_action_results_do_not_contain_vendor_commands(self):
        result = self.execute()

        self.assertTrue(result["allowed"])
        self.assertEqual(
            result["execution_mode"],
            "mock",
        )

        expected_keys = {
            "action_id",
            "resource",
            "operation",
            "status",
            "success",
            "error",
        }

        for action_result in result["action_results"]:
            self.assertEqual(
                set(action_result.keys()),
                expected_keys,
            )
            self.assertNotIn("command", action_result)
            self.assertNotIn("cli_command", action_result)

    def test_successful_simulation_remains_mock_only(self):
        result = self.execute()

        self.assertTrue(result["allowed"])
        self.assertTrue(result["executed"])
        self.assertEqual(
            result["execution_mode"],
            "mock",
        )
        self.assertEqual(
            result["deployment_result"]["execution_mode"],
            "mock",
        )


if __name__ == "__main__":
    unittest.main()
