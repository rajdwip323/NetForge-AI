
import sys
import unittest

sys.path.insert(0, "src")

from deployment.deployment_models import (
    build_deployment_plan,
    build_deployment_authorization,
    build_deployment_result,
)


class TestPhase7101Edges(unittest.TestCase):

    def test_empty_plan_id_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_plan(
                "", "R1", [{"action_id": "A1"}], "engineer"
            )

    def test_whitespace_target_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_plan(
                "P1", "   ", [{"action_id": "A1"}], "engineer"
            )

    def test_empty_created_by_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_plan(
                "P1", "R1", [{"action_id": "A1"}], ""
            )

    def test_non_list_actions_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_plan(
                "P1", "R1", {"action_id": "A1"}, "engineer"
            )

    def test_invalid_action_type_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_plan(
                "P1", "R1", ["invalid"], "engineer"
            )

    def test_nested_action_data_is_deep_copied(self):
        actions = [
            {
                "action_id": "A1",
                "parameters": {"admin_state": "up"},
            }
        ]

        result = build_deployment_plan(
            "P1", "R1", actions, "engineer"
        )

        actions[0]["parameters"]["admin_state"] = "down"

        self.assertEqual(
            result["actions"][0]["parameters"]["admin_state"],
            "up",
        )

    def test_boolean_action_count_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_result(
                "D1", "R1", actions_applied=True
            )

    def test_negative_failed_count_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_result(
                "D1", "R1", actions_failed=-1
            )

    def test_invalid_verification_status_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_result(
                "D1", "R1", verification_status="unknown"
            )

    def test_invalid_error_type_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_result(
                "D1", "R1", error={"message": "failure"}
            )

    def test_empty_deployment_id_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_result("", "R1")

    def test_whitespace_authorization_id_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_authorization(
                "   ",
                "P1",
                "R1",
                "fingerprint",
                "engineer",
                "approver",
                "approved",
                "2026-11-21T10:00:00+00:00",
                "2026-11-21T11:00:00+00:00",
            )

    def test_partial_failure_is_not_success(self):
        result = build_deployment_result(
            "D1",
            "R1",
            status="partially_failed",
            actions_applied=1,
            actions_failed=1,
        )

        self.assertFalse(result["success"])
        self.assertTrue(result["executed"])

    def test_failed_execution_is_not_success(self):
        result = build_deployment_result(
            "D2",
            "R1",
            status="failed",
            actions_failed=1,
        )

        self.assertFalse(result["success"])
        self.assertTrue(result["executed"])

    def test_pending_result_is_not_executed_or_successful(self):
        result = build_deployment_result(
            "D3", "R1", status="pending"
        )

        self.assertFalse(result["success"])
        self.assertFalse(result["executed"])


if __name__ == "__main__":
    unittest.main()
