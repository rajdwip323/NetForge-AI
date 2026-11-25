
"""
NETFORGE-AI
Phase 7.10.3 - Deployment Safety Gate
Edge Case Tests
"""

import sys
import unittest

from datetime import datetime, timezone

sys.path.insert(0, "src")

from deployment.deployment_models import (
    build_deployment_plan,
    build_deployment_authorization,
)

from deployment.deployment_safety_gate import (
    calculate_plan_fingerprint,
    evaluate_deployment_safety,
)


class TestPhase7103Edges(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 11, 25, 20, 30,
            tzinfo=timezone.utc
        )

        self.plan = build_deployment_plan(
            plan_id="PLAN-EDGE-001",
            target="R1",
            actions=[
                {
                    "action_id": "ACTION-001",
                    "resource": "interface",
                    "operation": "enable",
                    "parameters": {
                        "name": "GigabitEthernet0/1"
                    },
                }
            ],
            created_by="engineer_a",
            created_at="2026-11-25T19:55:00+00:00",
        )

        self.authorization = build_deployment_authorization(
            authorization_id="AUTH-EDGE-001",
            plan_id="PLAN-EDGE-001",
            target="R1",
            plan_fingerprint=calculate_plan_fingerprint(
                self.plan
            ),
            requested_by="engineer_a",
            approved_by="supervisor_b",
            status="approved",
            issued_at="2026-11-25T20:00:00+00:00",
            expires_at="2026-11-25T21:00:00+00:00",
        )

    def evaluate(self, plan=None, authorization=None, current_time=None):
        return evaluate_deployment_safety(
            self.plan if plan is None else plan,
            self.authorization if authorization is None else authorization,
            self.now if current_time is None else current_time,
        )

    def test_missing_plan_field_is_blocked(self):
        plan = dict(self.plan)
        del plan["created_by"]

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["plan_schema"])

    def test_extra_plan_field_is_blocked(self):
        plan = dict(self.plan)
        plan["unexpected_field"] = "injected"

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["plan_schema"])

    def test_empty_actions_are_blocked(self):
        plan = dict(self.plan)
        plan["actions"] = []

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])

    def test_naive_created_at_is_blocked(self):
        plan = dict(self.plan)
        plan["created_at"] = "2026-11-25T19:55:00"

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["plan_schema"])

    def test_invalid_created_at_is_blocked(self):
        plan = dict(self.plan)
        plan["created_at"] = "not-a-timestamp"

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])

    def test_unsupported_plan_value_is_blocked(self):
        plan = dict(self.plan)
        plan["created_by"] = object()

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["plan_schema"])

    def test_missing_authorization_field_is_blocked(self):
        authorization = dict(self.authorization)
        del authorization["authorization_id"]

        result = self.evaluate(authorization=authorization)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_schema"])

    def test_extra_authorization_field_is_blocked(self):
        authorization = dict(self.authorization)
        authorization["unexpected"] = "value"

        result = self.evaluate(authorization=authorization)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_schema"])

    def test_naive_authorization_timestamp_is_blocked(self):
        authorization = dict(self.authorization)
        authorization["issued_at"] = "2026-11-25T20:00:00"

        result = self.evaluate(authorization=authorization)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_schema"])

    def test_expiry_equal_to_issue_time_is_blocked(self):
        authorization = dict(self.authorization)
        authorization["expires_at"] = authorization["issued_at"]

        result = self.evaluate(authorization=authorization)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_schema"])

    def test_naive_current_time_is_blocked(self):
        current_time = datetime(2026, 11, 25, 20, 30)

        result = self.evaluate(current_time=current_time)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_time_valid"])

    def test_non_datetime_current_time_is_blocked(self):
        result = self.evaluate(current_time="2026-11-25T20:30:00Z")

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_time_valid"])

    def test_time_before_authorization_issue_is_blocked(self):
        current_time = datetime(
            2026, 11, 25, 19, 59,
            tzinfo=timezone.utc
        )

        result = self.evaluate(current_time=current_time)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_time_valid"])

    def test_exact_expiry_time_is_blocked(self):
        current_time = datetime(
            2026, 11, 25, 21, 0,
            tzinfo=timezone.utc
        )

        result = self.evaluate(current_time=current_time)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_time_valid"])


if __name__ == "__main__":
    unittest.main()
