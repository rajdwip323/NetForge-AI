
import sys
import unittest

sys.path.insert(0, "src")

from deployment.deployment_models import (
    build_deployment_plan,
    build_deployment_authorization,
    build_deployment_result,
    EXECUTION_MODE_MOCK,
    DEPLOYMENT_SCHEMA_VERSION,
)


class TestPhase7101(unittest.TestCase):

    def test_valid_deployment_plan(self):
        actions = [
            {
                "action_id": "ACT-001",
                "resource": "interface",
                "operation": "configure",
                "parameters": {
                    "name": "GigabitEthernet0/1",
                    "admin_state": "up",
                },
            }
        ]

        result = build_deployment_plan(
            plan_id="PLAN-001",
            target="R1",
            actions=actions,
            created_by="engineer_1",
        )

        self.assertEqual(result["plan_id"], "PLAN-001")
        self.assertEqual(result["target"], "R1")
        self.assertEqual(result["execution_mode"], "mock")
        self.assertEqual(
            result["schema_version"],
            DEPLOYMENT_SCHEMA_VERSION,
        )

    def test_plan_uses_deep_copy(self):
        actions = [{"action_id": "ACT-001"}]

        result = build_deployment_plan(
            "PLAN-002",
            "R1",
            actions,
            "engineer_1",
        )

        actions[0]["action_id"] = "MODIFIED"

        self.assertEqual(
            result["actions"][0]["action_id"],
            "ACT-001",
        )

    def test_empty_plan_actions_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_plan(
                "PLAN-003",
                "R1",
                [],
                "engineer_1",
            )

    def test_invalid_plan_target_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_plan(
                "PLAN-004",
                "",
                [{"action_id": "ACT-001"}],
                "engineer_1",
            )

    def test_valid_deployment_authorization(self):
        result = build_deployment_authorization(
            authorization_id="AUTH-001",
            plan_id="PLAN-001",
            target="R1",
            plan_fingerprint="abc123",
            requested_by="engineer_1",
            approved_by="approver_1",
            status="approved",
            issued_at="2026-11-21T10:00:00+00:00",
            expires_at="2026-11-21T11:00:00+00:00",
        )

        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["plan_id"], "PLAN-001")
        self.assertEqual(result["target"], "R1")

    def test_invalid_authorization_status_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_authorization(
                "AUTH-002",
                "PLAN-001",
                "R1",
                "abc123",
                "engineer_1",
                "approver_1",
                "unknown",
                "2026-11-21T10:00:00+00:00",
                "2026-11-21T11:00:00+00:00",
            )

    def test_valid_deployment_result(self):
        result = build_deployment_result(
            deployment_id="DEP-001",
            target="R1",
            status="completed",
            actions_applied=1,
            actions_failed=0,
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["executed"])
        self.assertEqual(result["execution_mode"], "mock")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["actions_applied"], 1)
        self.assertEqual(result["verification_status"], "pending")

    def test_pending_result_not_executed(self):
        result = build_deployment_result(
            deployment_id="DEP-002",
            target="R1",
            status="pending",
        )

        self.assertFalse(result["executed"])

    def test_invalid_deployment_status_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_result(
                "DEP-003",
                "R1",
                status="unknown",
            )

    def test_negative_action_count_rejected(self):
        with self.assertRaises(ValueError):
            build_deployment_result(
                "DEP-004",
                "R1",
                actions_applied=-1,
            )


if __name__ == "__main__":
    unittest.main()
