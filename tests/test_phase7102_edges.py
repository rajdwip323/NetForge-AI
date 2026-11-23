
import sys
import unittest
import copy

sys.path.insert(0, "src")

from deployment.deployment_validator import validate_deployment_plan


class TestPhase7102Edges(unittest.TestCase):

    def build_action(self, **overrides):
        action = {
            "action_id": "ACT-001",
            "resource": "interface",
            "operation": "enable",
            "parameters": {
                "name": "eth0",
            },
        }
        action.update(overrides)
        return action

    def build_plan(self, actions):
        return {"actions": actions}

    def test_non_dictionary_plan_rejected(self):
        result = validate_deployment_plan([])
        self.assertFalse(result["valid"])

    def test_empty_plan_rejected(self):
        result = validate_deployment_plan({})
        self.assertFalse(result["valid"])

    def test_empty_actions_rejected(self):
        result = validate_deployment_plan({"actions": []})
        self.assertFalse(result["valid"])

    def test_actions_not_list_rejected(self):
        result = validate_deployment_plan({"actions": {}})
        self.assertFalse(result["valid"])

    def test_non_dictionary_action_rejected(self):
        result = validate_deployment_plan(
            self.build_plan(["invalid"])
        )
        self.assertFalse(result["valid"])

    def test_empty_action_id_rejected(self):
        action = self.build_action(action_id="")
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_whitespace_action_id_rejected(self):
        action = self.build_action(action_id="   ")
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_missing_action_field_rejected(self):
        action = self.build_action()
        del action["operation"]

        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_unknown_action_field_rejected(self):
        action = self.build_action(extra="unexpected")
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_duplicate_action_ids_rejected(self):
        first = self.build_action()
        second = self.build_action(
            resource="vlan",
            operation="create",
            parameters={"vlan_id": 100},
        )

        result = validate_deployment_plan(
            self.build_plan([first, second])
        )
        self.assertFalse(result["valid"])

    def test_duplicate_action_ids_case_insensitive(self):
        first = self.build_action(action_id="ACT-001")
        second = self.build_action(action_id="act-001")

        result = validate_deployment_plan(
            self.build_plan([first, second])
        )
        self.assertFalse(result["valid"])

    def test_parameters_not_dictionary_rejected(self):
        action = self.build_action(parameters=[])
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_empty_interface_name_rejected(self):
        action = self.build_action(
            parameters={"name": ""}
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_whitespace_interface_name_rejected(self):
        action = self.build_action(
            parameters={"name": "   "}
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_vlan_id_lower_boundary_accepted(self):
        action = self.build_action(
            resource="vlan",
            operation="create",
            parameters={"vlan_id": 1},
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertTrue(result["valid"])

    def test_vlan_id_upper_boundary_accepted(self):
        action = self.build_action(
            resource="vlan",
            operation="create",
            parameters={"vlan_id": 4094},
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertTrue(result["valid"])

    def test_vlan_id_zero_rejected(self):
        action = self.build_action(
            resource="vlan",
            operation="create",
            parameters={"vlan_id": 0},
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_vlan_id_above_maximum_rejected(self):
        action = self.build_action(
            resource="vlan",
            operation="create",
            parameters={"vlan_id": 4095},
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_boolean_vlan_id_rejected(self):
        action = self.build_action(
            resource="vlan",
            operation="create",
            parameters={"vlan_id": True},
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_invalid_admin_state_rejected(self):
        action = self.build_action(
            operation="configure",
            parameters={
                "name": "eth0",
                "admin_state": "enabled",
            },
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_non_string_description_rejected(self):
        action = self.build_action(
            operation="configure",
            parameters={
                "name": "eth0",
                "description": 123,
            },
        )
        result = validate_deployment_plan(
            self.build_plan([action])
        )
        self.assertFalse(result["valid"])

    def test_validation_does_not_modify_nested_input(self):
        plan = self.build_plan([
            self.build_action(
                operation="configure",
                parameters={
                    "name": "eth0",
                    "description": "Uplink",
                    "admin_state": "up",
                },
            )
        ])

        original = copy.deepcopy(plan)

        validate_deployment_plan(plan)

        self.assertEqual(plan, original)


if __name__ == "__main__":
    unittest.main()
