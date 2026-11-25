
"""
NETFORGE-AI
Phase 7.10.3 - Deployment Safety Gate Functional Tests
"""

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
    evaluate_deployment_safety,
)


class TestPhase7103Functional(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 11, 25, 20, 30,
            tzinfo=timezone.utc
        )

        self.issued_at = "2026-11-25T20:00:00+00:00"
        self.expires_at = "2026-11-25T21:00:00+00:00"

        self.plan = build_deployment_plan(
            plan_id="PLAN-7103-001",
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

        self.authorization = self.build_authorization(
            self.plan
        )

    def build_authorization(
        self,
        plan,
        status="approved",
        requested_by="engineer_a",
        approved_by="supervisor_b",
    ):
        fingerprint = calculate_plan_fingerprint(plan)

        return build_deployment_authorization(
            authorization_id="AUTH-7103-001",
            plan_id=plan["plan_id"],
            target=plan["target"],
            plan_fingerprint=fingerprint,
            requested_by=requested_by,
            approved_by=approved_by,
            status=status,
            issued_at=self.issued_at,
            expires_at=self.expires_at,
        )

    def evaluate(self, plan=None, authorization=None):
        return evaluate_deployment_safety(
            plan if plan is not None else self.plan,
            (
                authorization
                if authorization is not None
                else self.authorization
            ),
            current_time=self.now,
        )

    def test_valid_plan_and_authorization_are_allowed(self):
        result = self.evaluate()

        self.assertTrue(result["allowed"])
        self.assertEqual(result["errors"], [])
        self.assertTrue(all(result["checks"].values()))

    def test_valid_result_contains_all_safety_checks(self):
        result = self.evaluate()

        expected_checks = {
            "plan_structure",
            "plan_schema",
            "action_validation",
            "execution_mode_mock",
            "authorization_present",
            "authorization_schema",
            "authorization_approved",
            "plan_id_match",
            "target_match",
            "actor_separation",
            "authorization_time_valid",
            "fingerprint_match",
        }

        self.assertEqual(
            set(result["checks"].keys()),
            expected_checks,
        )

    def test_pending_authorization_is_blocked(self):
        authorization = self.build_authorization(
            self.plan,
            status="pending",
        )

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(
            result["checks"]["authorization_approved"]
        )

    def test_modified_plan_fails_fingerprint_validation(self):
        modified_plan = deepcopy(self.plan)

        modified_plan["created_by"] = "different_engineer"

        result = self.evaluate(plan=modified_plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(
            result["checks"]["fingerprint_match"]
        )

    def test_real_execution_mode_is_blocked(self):
        modified_plan = deepcopy(self.plan)

        modified_plan["execution_mode"] = "real"

        authorization = self.build_authorization(
            modified_plan
        )

        result = self.evaluate(
            plan=modified_plan,
            authorization=authorization,
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(
            result["checks"]["execution_mode_mock"]
        )

    def test_same_requester_and_approver_are_blocked(self):
        authorization = deepcopy(self.authorization)

        authorization["approved_by"] = "ENGINEER_A"

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(
            result["checks"]["actor_separation"]
        )

    def test_expired_authorization_is_blocked(self):
        authorization = deepcopy(self.authorization)

        authorization["expires_at"] = (
            "2026-11-25T20:29:00+00:00"
        )

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(
            result["checks"]["authorization_time_valid"]
        )

    def test_plan_target_mismatch_is_blocked(self):
        authorization = deepcopy(self.authorization)

        authorization["target"] = "R2"

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(
            result["checks"]["target_match"]
        )

    def test_plan_id_mismatch_is_blocked(self):
        authorization = deepcopy(self.authorization)

        authorization["plan_id"] = "ANOTHER-PLAN"

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(
            result["checks"]["plan_id_match"]
        )

    def test_execution_is_never_performed_by_safety_gate(self):
        result = self.evaluate()

        self.assertFalse(result["executed"])

    def test_valid_result_contains_full_fingerprint(self):
        result = self.evaluate()

        self.assertEqual(
            result["fingerprint"],
            calculate_plan_fingerprint(self.plan),
        )

    def test_input_plan_and_authorization_are_not_modified(self):
        original_plan = deepcopy(self.plan)
        original_authorization = deepcopy(
            self.authorization
        )

        self.evaluate()

        self.assertEqual(self.plan, original_plan)
        self.assertEqual(
            self.authorization,
            original_authorization,
        )


if __name__ == "__main__":
    unittest.main()
