
"""
NETFORGE-AI
Phase 7.10.3 - Deployment Safety Gate
Security Tests
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


class TestPhase7103Security(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 11, 25, 20, 30,
            tzinfo=timezone.utc
        )

        self.plan = build_deployment_plan(
            plan_id="PLAN-SEC-001",
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
            authorization_id="AUTH-SEC-001",
            plan_id="PLAN-SEC-001",
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

    def test_command_injection_interface_name_rejected(self):
        plan = dict(self.plan)
        plan["actions"] = [
            dict(self.plan["actions"][0])
        ]

        plan["actions"][0]["parameters"] = {
            "name": "GigabitEthernet0/1; reload"
        }

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["action_validation"])

    def test_newline_command_injection_interface_name_rejected(self):
        plan = dict(self.plan)
        plan["actions"] = [
            dict(self.plan["actions"][0])
        ]

        plan["actions"][0]["parameters"] = {
            "name": "GigabitEthernet0/1\nreload"
        }

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["action_validation"])

    def test_newline_in_description_rejected(self):
        plan = dict(self.plan)
        plan["actions"] = [
            dict(self.plan["actions"][0])
        ]

        plan["actions"][0]["parameters"] = {
            "name": "GigabitEthernet0/1",
            "description": "Office interface\nreload"
        }

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["action_validation"])

    def test_vendor_command_field_rejected(self):
        plan = dict(self.plan)
        plan["actions"] = [
            dict(self.plan["actions"][0])
        ]

        plan["actions"][0]["command"] = "reload"

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["action_validation"])

    def test_unsupported_action_field_rejected(self):
        plan = dict(self.plan)
        plan["actions"] = [
            dict(self.plan["actions"][0])
        ]

        plan["actions"][0]["vendor_command"] = (
            "configure terminal"
        )

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["action_validation"])

    def test_non_string_action_id_rejected(self):
        plan = dict(self.plan)
        plan["actions"] = [
            dict(self.plan["actions"][0])
        ]

        plan["actions"][0]["action_id"] = 12345

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["action_validation"])

    def test_non_string_parameter_value_rejected(self):
        plan = dict(self.plan)
        plan["actions"] = [
            dict(self.plan["actions"][0])
        ]

        plan["actions"][0]["parameters"] = {
            "name": ["GigabitEthernet0/1"]
        }

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["action_validation"])

    def test_nan_in_plan_is_rejected(self):
        plan = dict(self.plan)
        plan["created_by"] = float("nan")

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["plan_schema"])

    def test_circular_plan_reference_is_rejected(self):
        plan = dict(self.plan)
        plan["actions"] = [
            dict(self.plan["actions"][0])
        ]

        circular_parameters = {
            "name": "GigabitEthernet0/1"
        }

        circular_parameters["self"] = circular_parameters

        plan["actions"][0]["parameters"] = (
            circular_parameters
        )

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["plan_schema"])

    def test_malformed_fingerprint_is_rejected(self):
        authorization = dict(self.authorization)
        authorization["plan_fingerprint"] = "invalid"

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_schema"])

    def test_forged_fingerprint_is_rejected(self):
        authorization = dict(self.authorization)

        authorization["plan_fingerprint"] = "0" * 64

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["fingerprint_match"])

    def test_authorization_injection_field_rejected(self):
        authorization = dict(self.authorization)

        authorization["execution_command"] = "reload"

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_schema"])

    def test_unsupported_authorization_status_rejected(self):
        authorization = dict(self.authorization)

        authorization["status"] = "trusted"

        result = self.evaluate(
            authorization=authorization
        )

        self.assertFalse(result["allowed"])
        self.assertFalse(result["checks"]["authorization_schema"])

    def test_blocked_request_never_executes(self):
        plan = dict(self.plan)
        plan["execution_mode"] = "real"

        result = self.evaluate(plan=plan)

        self.assertFalse(result["allowed"])
        self.assertFalse(result["executed"])


if __name__ == "__main__":
    unittest.main()
