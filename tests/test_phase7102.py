
import sys
import unittest
import copy

sys.path.insert(0, "src")

from deployment.deployment_validator import validate_deployment_plan


class TestPhase7102Functional(unittest.TestCase):

    def build_plan(self, action):
        return {
            "actions": [action]
        }

    def test_valid_interface_configure(self):
        action = {
            "action_id": "ACT-001",
            "resource": "interface",
            "operation": "configure",
            "parameters": {
                "name": "GigabitEthernet0/1",
                "description": "Uplink",
                "admin_state": "up",
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_valid_interface_enable(self):
        action = {
            "action_id": "ACT-002",
            "resource": "interface",
            "operation": "enable",
            "parameters": {
                "name": "eth0",
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertTrue(result["valid"])

    def test_valid_interface_disable(self):
        action = {
            "action_id": "ACT-003",
            "resource": "interface",
            "operation": "disable",
            "parameters": {
                "name": "eth1",
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertTrue(result["valid"])

    def test_valid_vlan_create(self):
        action = {
            "action_id": "ACT-004",
            "resource": "vlan",
            "operation": "create",
            "parameters": {
                "vlan_id": 100,
                "name": "OFFICE",
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertTrue(result["valid"])

    def test_valid_vlan_configure(self):
        action = {
            "action_id": "ACT-005",
            "resource": "vlan",
            "operation": "configure",
            "parameters": {
                "vlan_id": 200,
                "name": "GUEST",
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertTrue(result["valid"])

    def test_valid_vlan_delete(self):
        action = {
            "action_id": "ACT-006",
            "resource": "vlan",
            "operation": "delete",
            "parameters": {
                "vlan_id": 300,
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertTrue(result["valid"])

    def test_unsupported_resource_rejected(self):
        action = {
            "action_id": "ACT-007",
            "resource": "routing",
            "operation": "configure",
            "parameters": {},
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertFalse(result["valid"])

    def test_invalid_resource_operation_combination(self):
        action = {
            "action_id": "ACT-008",
            "resource": "interface",
            "operation": "delete",
            "parameters": {
                "name": "eth0",
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertFalse(result["valid"])

    def test_missing_required_parameter(self):
        action = {
            "action_id": "ACT-009",
            "resource": "interface",
            "operation": "configure",
            "parameters": {
                "description": "Uplink",
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertFalse(result["valid"])

    def test_unsupported_parameter_rejected(self):
        action = {
            "action_id": "ACT-010",
            "resource": "interface",
            "operation": "enable",
            "parameters": {
                "name": "eth0",
                "vlan_id": 100,
            },
        }

        result = validate_deployment_plan(
            self.build_plan(action)
        )

        self.assertFalse(result["valid"])

    def test_multiple_valid_actions(self):
        plan = {
            "actions": [
                {
                    "action_id": "ACT-011",
                    "resource": "interface",
                    "operation": "enable",
                    "parameters": {
                        "name": "eth0",
                    },
                },
                {
                    "action_id": "ACT-012",
                    "resource": "vlan",
                    "operation": "create",
                    "parameters": {
                        "vlan_id": 100,
                    },
                },
            ]
        }

        result = validate_deployment_plan(plan)

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_valid_plan_does_not_modify_input(self):
        plan = {
            "actions": [
                {
                    "action_id": "ACT-013",
                    "resource": "interface",
                    "operation": "configure",
                    "parameters": {
                        "name": "eth0",
                        "description": "Uplink",
                    },
                }
            ]
        }

        original_plan = copy.deepcopy(plan)

        validate_deployment_plan(plan)

        self.assertEqual(plan, original_plan)


if __name__ == "__main__":
    unittest.main()
