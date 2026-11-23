
import copy
import unittest

from src.deployment.deployment_validator import validate_deployment_plan


class TestPhase7102Security(unittest.TestCase):

    def _build_plan(self, resource="interface", operation="configure", parameters=None):
        if parameters is None:
            parameters = {"name": "GigabitEthernet0/1"}

        return {
            "plan_id": "PLAN-SEC-001",
            "target": "R1",
            "actions": [
                {
                    "action_id": "ACTION-001",
                    "resource": resource,
                    "operation": operation,
                    "parameters": parameters,
                }
            ],
        }

    def test_action_id_non_string_rejected(self):
        plan = self._build_plan()
        plan["actions"][0]["action_id"] = 123

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_command_injection_interface_name_rejected(self):
        plan = self._build_plan(
            parameters={"name": "eth0; shutdown"}
        )

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_newline_in_interface_name_rejected(self):
        plan = self._build_plan(
            parameters={"name": "eth0\nshutdown"}
        )

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_newline_in_description_rejected(self):
        plan = self._build_plan(
            parameters={
                "name": "GigabitEthernet0/1",
                "description": "Uplink\nshutdown",
            }
        )

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_newline_in_vlan_name_rejected(self):
        plan = self._build_plan(
            resource="vlan",
            operation="create",
            parameters={
                "vlan_id": 100,
                "name": "OFFICE\nshutdown",
            },
        )

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_non_string_action_field_key_rejected_safely(self):
        plan = self._build_plan()
        plan["actions"][0][123] = "unexpected"

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])
        self.assertIsInstance(result["errors"], list)

    def test_non_string_parameter_key_rejected_safely(self):
        plan = self._build_plan()
        plan["actions"][0]["parameters"][123] = "unexpected"

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])
        self.assertIsInstance(result["errors"], list)

    def test_operation_list_rejected_safely(self):
        plan = self._build_plan()
        plan["actions"][0]["operation"] = ["configure"]

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_resource_list_rejected_safely(self):
        plan = self._build_plan()
        plan["actions"][0]["resource"] = ["interface"]

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_vendor_command_field_rejected(self):
        plan = self._build_plan()
        plan["actions"][0]["command"] = "shutdown"

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_vlan_boolean_does_not_bypass_integer_check(self):
        plan = self._build_plan(
            resource="vlan",
            operation="create",
            parameters={"vlan_id": True},
        )

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_validation_does_not_modify_input(self):
        plan = self._build_plan(
            parameters={
                "name": "GigabitEthernet0/1",
                "description": "Uplink",
            }
        )
        original_plan = copy.deepcopy(plan)

        validate_deployment_plan(plan)

        self.assertEqual(plan, original_plan)


if __name__ == "__main__":
    unittest.main()
