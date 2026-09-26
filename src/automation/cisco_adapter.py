from automation.vendor_adapter import VendorAdapter


class CiscoAdapter(VendorAdapter):
    """
    Cisco reference implementation for NetForge-AI.

    Cisco-specific commands stay inside this adapter.
    Core automation workflows should not depend directly
    on these commands.
    """

    vendor_name = "cisco"

    COMMANDS = {
        "show_running_config": "show running-config",
        "show_ip_route": "show ip route",
        "show_interfaces_description": "show interfaces description",
        "show_ip_interface": "show ip interface brief",
    }

    def get_command(self, operation):
        """
        Return the Cisco-specific command for an operation.
        """

        if not isinstance(operation, str):
            raise ValueError("Operation must be a string")

        operation = operation.strip()

        if operation not in self.COMMANDS:
            raise ValueError(
                f"Unsupported Cisco operation: {operation}"
            )

        return self.COMMANDS[operation]

    def parse_output(self, operation, output):
        """
        Convert Cisco command output into a normalized structure.
        """

        if not isinstance(operation, str):
            return {
                "success": False,
                "data": None,
                "error": "Operation must be a string"
            }

        if not isinstance(output, str):
            return {
                "success": False,
                "data": None,
                "error": "Invalid command output"
            }

        operation = operation.strip()

        if operation == "show_running_config":
            return {
                "success": True,
                "data": {
                    "configuration": output
                },
                "error": None
            }

        if operation == "show_ip_route":
            return {
                "success": True,
                "data": {
                    "raw_output": output
                },
                "error": None
            }

        if operation == "show_interfaces_description":
            return {
                "success": True,
                "data": {
                    "raw_output": output
                },
                "error": None
            }

        if operation == "show_ip_interface":
            return {
                "success": True,
                "data": {
                    "raw_output": output
                },
                "error": None
            }

        return {
            "success": False,
            "data": None,
            "error": f"Unsupported Cisco operation: {operation}"
        }

    def build_config(self, operation, config):
        """
        Build Cisco-specific configuration commands.
        """

        if not isinstance(operation, str):
            raise ValueError("Operation must be a string")

        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")

        operation = operation.strip()

        if operation == "vlan":
            vlan_id = config.get("vlan_id")
            name = config.get("name")

            if not isinstance(vlan_id, int):
                raise ValueError("VLAN ID must be an integer")

            if vlan_id < 1 or vlan_id > 4094:
                raise ValueError("VLAN ID must be between 1 and 4094")

            if not isinstance(name, str) or not name.strip():
                raise ValueError("VLAN name is required")

            return [
                f"vlan {vlan_id}",
                f"name {name.strip()}"
            ]

        if operation == "interface":
            interface = config.get("interface")

            if not isinstance(interface, str) or not interface.strip():
                raise ValueError("Interface is required")

            commands = [
                f"interface {interface.strip()}"
            ]

            description = config.get("description")

            if description is not None:
                if not isinstance(description, str):
                    raise ValueError(
                        "Interface description must be a string"
                    )

                commands.append(
                    f"description {description.strip()}"
                )

            return commands

        raise ValueError(
            f"Unsupported Cisco configuration operation: {operation}"
        )