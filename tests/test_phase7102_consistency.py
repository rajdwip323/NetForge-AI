
import copy
import unittest

from src.deployment.deployment_validator import validate_deployment_plan


class TestPhase7102Consistency(unittest.TestCase):

    def _build_plan(self, actions):
        return {
            "plan_id": "PLAN-CONSISTENCY-001",
            "target": "R1",
            "actions": actions,
        }

    def _action(self, resource, operation, parameters, action_id="ACTION-001"):
        return {
            "action_id": action_id,
            "resource": resource,
            "operation": operation,
            "parameters": parameters,
        }

    def test_all_six_approved_operations_are_valid(self):
        valid_cases = [
            (
                "interface",
                "configure",
                {"name": "GigabitEthernet0/1"},
            ),
            (
                "interface",
                "enable",
                {"name": "GigabitEthernet0/1"},
            ),
            (
                "interface",
                "disable",
                {"name": "GigabitEthernet0/1"},
            ),
            (
                "vlan",
                "create",
                {"vlan_id": 100},
            ),
            (
                "vlan",
                "configure",
                {"vlan_id": 100, "name": "OFFICE"},
            ),
            (
                "vlan",
                "delete",
                {"vlan_id": 100},
            ),
        ]

        for index, (resource, operation, parameters) in enumerate(valid_cases):
            with self.subTest(resource=resource, operation=operation):
                plan = self._build_plan([
                    self._action(
                        resource,
                        operation,
                        parameters,
                        action_id="ACTION-{}".format(index + 1),
                    )
                ])

                result = validate_deployment_plan(plan)

                self.assertTrue(result["valid"])
                self.assertEqual(result["errors"], [])

    def test_valid_optional_interface_parameters(self):
        plan = self._build_plan([
            self._action(
                "interface",
                "configure",
                {
                    "name": "GigabitEthernet0/1",
                    "description": "Uplink",
                    "admin_state": "up",
                },
            )
        ])

        result = validate_deployment_plan(plan)

        self.assertTrue(result["valid"])

    def test_valid_optional_vlan_name(self):
        plan = self._build_plan([
            self._action(
                "vlan",
                "create",
                {
                    "vlan_id": 100,
                    "name": "OFFICE",
                },
            )
        ])

        result = validate_deployment_plan(plan)

        self.assertTrue(result["valid"])

    def test_unsupported_resources_are_rejected(self):
        unsupported_resources = [
            "routing",
            "device",
            "firewall",
            "switch",
        ]

        for resource in unsupported_resources:
            with self.subTest(resource=resource):
                plan = self._build_plan([
                    self._action(
                        resource,
                        "configure",
                        {"name": "GigabitEthernet0/1"},
                    )
                ])

                result = validate_deployment_plan(plan)

                self.assertFalse(result["valid"])

    def test_unsupported_interface_operations_are_rejected(self):
        unsupported_operations = [
            "create",
            "delete",
            "reload",
            "shutdown",
        ]

        for operation in unsupported_operations:
            with self.subTest(operation=operation):
                plan = self._build_plan([
                    self._action(
                        "interface",
                        operation,
                        {"name": "GigabitEthernet0/1"},
                    )
                ])

                result = validate_deployment_plan(plan)

                self.assertFalse(result["valid"])

    def test_unsupported_vlan_operations_are_rejected(self):
        unsupported_operations = [
            "enable",
            "disable",
            "reload",
            "shutdown",
        ]

        for operation in unsupported_operations:
            with self.subTest(operation=operation):
                plan = self._build_plan([
                    self._action(
                        "vlan",
                        operation,
                        {"vlan_id": 100},
                    )
                ])

                result = validate_deployment_plan(plan)

                self.assertFalse(result["valid"])

    def test_interface_configure_requires_name(self):
        plan = self._build_plan([
            self._action("interface", "configure", {})
        ])

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_interface_enable_requires_name(self):
        plan = self._build_plan([
            self._action("interface", "enable", {})
        ])

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_interface_disable_requires_name(self):
        plan = self._build_plan([
            self._action("interface", "disable", {})
        ])

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_vlan_create_requires_vlan_id(self):
        plan = self._build_plan([
            self._action("vlan", "create", {})
        ])

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_vlan_configure_requires_vlan_id_and_name(self):
        missing_vlan_id = self._build_plan([
            self._action(
                "vlan",
                "configure",
                {"name": "OFFICE"},
            )
        ])

        missing_name = self._build_plan([
            self._action(
                "vlan",
                "configure",
                {"vlan_id": 100},
            )
        ])

        self.assertFalse(validate_deployment_plan(missing_vlan_id)["valid"])
        self.assertFalse(validate_deployment_plan(missing_name)["valid"])

    def test_vlan_delete_requires_vlan_id(self):
        plan = self._build_plan([
            self._action("vlan", "delete", {})
        ])

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_unknown_action_fields_are_rejected(self):
        plan = self._build_plan([
            self._action(
                "interface",
                "enable",
                {"name": "GigabitEthernet0/1"},
            )
        ])
        plan["actions"][0]["vendor_command"] = "shutdown"

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_unknown_parameter_fields_are_rejected(self):
        plan = self._build_plan([
            self._action(
                "interface",
                "configure",
                {
                    "name": "GigabitEthernet0/1",
                    "vendor_command": "shutdown",
                },
            )
        ])

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_multiple_valid_actions_are_accepted(self):
        plan = self._build_plan([
            self._action(
                "interface",
                "configure",
                {"name": "GigabitEthernet0/1"},
                "ACTION-001",
            ),
            self._action(
                "interface",
                "enable",
                {"name": "GigabitEthernet0/1"},
                "ACTION-002",
            ),
            self._action(
                "vlan",
                "create",
                {"vlan_id": 100},
                "ACTION-003",
            ),
        ])

        result = validate_deployment_plan(plan)

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_one_invalid_action_invalidates_entire_plan(self):
        plan = self._build_plan([
            self._action(
                "interface",
                "enable",
                {"name": "GigabitEthernet0/1"},
                "ACTION-001",
            ),
            self._action(
                "routing",
                "configure",
                {"name": "GigabitEthernet0/1"},
                "ACTION-002",
            ),
        ])

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])

    def test_valid_plan_is_not_modified(self):
        plan = self._build_plan([
            self._action(
                "interface",
                "configure",
                {
                    "name": "GigabitEthernet0/1",
                    "description": "Uplink",
                },
            )
        ])
        original_plan = copy.deepcopy(plan)

        validate_deployment_plan(plan)

        self.assertEqual(plan, original_plan)

    def test_invalid_plan_is_not_modified(self):
        plan = self._build_plan([
            self._action(
                "interface",
                "configure",
                {"name": "eth0; shutdown"},
            )
        ])
        original_plan = copy.deepcopy(plan)

        validate_deployment_plan(plan)

        self.assertEqual(plan, original_plan)

    def test_validation_errors_are_returned_as_list(self):
        plan = self._build_plan([
            self._action("interface", "configure", {})
        ])

        result = validate_deployment_plan(plan)

        self.assertFalse(result["valid"])
        self.assertIsInstance(result["errors"], list)

        for error in result["errors"]:
            self.assertIsInstance(error, str)


if __name__ == "__main__":
    unittest.main()
