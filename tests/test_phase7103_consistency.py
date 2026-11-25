
"""
NETFORGE-AI
Phase 7.10.3 - Deployment Safety Gate
Consistency Tests
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


class TestPhase7103Consistency(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 11, 25, 20, 30,
            tzinfo=timezone.utc
        )

        self.plan = build_deployment_plan(
            plan_id="PLAN-CONS-001",
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
            authorization_id="AUTH-CONS-001",
            plan_id="PLAN-CONS-001",
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

    def evaluate(self, plan=None, authorization=None):
        return evaluate_deployment_safety(
            self.plan if plan is None else plan,
            self.authorization if authorization is None else authorization,
            self.now,
        )

    def test_same_plan_generates_same_fingerprint(self):
        first = calculate_plan_fingerprint(self.plan)
        second = calculate_plan_fingerprint(self.plan)

        self.assertEqual(first, second)

    def test_dictionary_key_order_does_not_change_fingerprint(self):
        reordered_plan = dict(
            reversed(list(self.plan.items()))
        )

        original_fingerprint = calculate_plan_fingerprint(
            self.plan
        )

        reordered_fingerprint = calculate_plan_fingerprint(
            reordered_plan
        )

        self.assertEqual(
            original_fingerprint,
            reordered_fingerprint,
        )

    def test_plan_value_change_changes_fingerprint(self):
        modified_plan = dict(self.plan)
        modified_plan["created_by"] = "different_engineer"

        original_fingerprint = calculate_plan_fingerprint(
            self.plan
        )

        modified_fingerprint = calculate_plan_fingerprint(
            modified_plan
        )

        self.assertNotEqual(
            original_fingerprint,
            modified_fingerprint,
        )

    def test_valid_plan_always_produces_same_decision(self):
        first = self.evaluate()
        second = self.evaluate()

        self.assertEqual(first["allowed"], second["allowed"])
        self.assertEqual(first["checks"], second["checks"])
        self.assertTrue(first["allowed"])

    def test_valid_plan_has_all_expected_checks(self):
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

    def test_all_check_results_are_booleans(self):
        result = self.evaluate()

        for check_name, check_value in result["checks"].items():
            with self.subTest(check=check_name):
                self.assertIsInstance(check_value, bool)

    def test_allowed_equals_all_safety_checks(self):
        result = self.evaluate()

        self.assertEqual(
            result["allowed"],
            all(result["checks"].values()),
        )

    def test_one_failed_check_blocks_complete_plan(self):
        modified_plan = dict(self.plan)
        modified_plan["execution_mode"] = "real"

        result = self.evaluate(plan=modified_plan)

        self.assertFalse(
            result["checks"]["execution_mode_mock"]
        )

        self.assertFalse(result["allowed"])

    def test_valid_result_contains_sha256_fingerprint(self):
        result = self.evaluate()

        fingerprint = result["fingerprint"]

        self.assertIsInstance(fingerprint, str)
        self.assertEqual(len(fingerprint), 64)

        self.assertEqual(
            fingerprint,
            calculate_plan_fingerprint(self.plan),
        )

    def test_safety_gate_never_executes_actions(self):
        result = self.evaluate()

        self.assertFalse(result["executed"])

    def test_invalid_plan_never_returns_allowed(self):
        modified_plan = dict(self.plan)
        modified_plan["unexpected"] = "value"

        result = self.evaluate(plan=modified_plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["executed"])

    def test_modified_plan_never_keeps_original_fingerprint(self):
        modified_plan = dict(self.plan)
        modified_plan["created_by"] = "another_engineer"

        result = self.evaluate(plan=modified_plan)

        self.assertFalse(result["checks"]["fingerprint_match"])
        self.assertFalse(result["allowed"])


if __name__ == "__main__":
    unittest.main()
