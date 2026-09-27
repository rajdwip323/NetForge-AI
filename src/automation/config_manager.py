import ipaddress
import re

from abc import ABC

from ssh.ssh_manager import execute_command

from verification.verification_engine import (
    verification_passed,
    verification_failed,
    verification_error
)

from verification.interface_verifier import (
    verify_interface_state
)


class itry(ABC):
    """Utility wrapper for common configuration workflows."""

    @staticmethod
    def validate_ip_address(ip_value):
        """Return True when a value is a valid IPv4 or IPv6 address."""
        try:
            ipaddress.ip_address(ip_value)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def generate_config_commands(config_type, config):
        return generate_config_commands(config_type, config)

    @staticmethod
    def dry_run_config(config_type, config):
        return dry_run_config(config_type, config)

    @staticmethod
    def apply_config(client, commands, dry_run=False):
        return apply_config(client, commands, dry_run=dry_run)

    @staticmethod
    def parse_interface_description(output, interface):
        return parse_interface_description(output, interface)

    @staticmethod
    def verify_interface(
        client,
        interface,
        expected_description,
        expected_status
    ):
        return verify_interface(
            client,
            interface,
            expected_description,
            expected_status
        )

    @staticmethod
    def parse_interface_ip(output, interface):
        return parse_interface_ip(output, interface)

    @staticmethod
    def verify_ip_configuration(
        client,
        interface,
        expected_ip,
        expected_mask
    ):
        return verify_ip_configuration(
            client,
            interface,
            expected_ip,
            expected_mask
        )

    @staticmethod
    def configure_ip(
        client,
        interface,
        ip,
        mask,
        dry_run=False
    ):
        return configure_ip(
            client,
            interface,
            ip,
            mask,
            dry_run=dry_run
        )

    @staticmethod
    def configure_interface(
        client,
        interface,
        description,
        status,
        dry_run=False
    ):
        return configure_interface(
            client,
            interface,
            description,
            status,
            dry_run=dry_run
        )

    @staticmethod
    def verify_vlan(client, vlan_id, expected_name):
        return verify_vlan(client, vlan_id, expected_name)

    @staticmethod
    def configure_vlan(
        client,
        vlan_id,
        name,
        dry_run=False
    ):
        return configure_vlan(
            client,
            vlan_id,
            name,
            dry_run=dry_run
        )


def generate_config_commands(config_type, config):
    """
    Generate network device configuration commands.

    This function only generates commands.
    It does not connect to or modify any device.
    """

    commands = []

    if not isinstance(config, dict):
        return {
            "success": False,
            "commands": [],
            "error": "Configuration must be a dictionary"
        }

    # --------------------------------------------------------
    # VLAN configuration
    # --------------------------------------------------------

    if config_type == "vlan":

        vlan_id = config.get("vlan_id")
        name = config.get("name")

        if not isinstance(vlan_id, int) or not 1 <= vlan_id <= 4094:
            return {
                "success": False,
                "commands": [],
                "error": "Invalid VLAN ID"
            }

        if not name or not isinstance(name, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid VLAN name"
            }

        commands.append(f"vlan {vlan_id}")
        commands.append(f"name {name}")

    # --------------------------------------------------------
    # Interface configuration
    # --------------------------------------------------------

    elif config_type == "interface":

        interface = config.get("interface")
        description = config.get("description")
        status = config.get("status")

        if not interface or not isinstance(interface, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid interface name"
            }

        if description is not None and not isinstance(description, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid interface description"
            }

        if status not in ["up", "down"]:
            return {
                "success": False,
                "commands": [],
                "error": "Invalid interface status"
            }

        commands.append(f"interface {interface}")

        if description:
            commands.append(f"description {description}")

        if status == "up":
            commands.append("no shutdown")
        else:
            commands.append("shutdown")

    # --------------------------------------------------------
    # IP configuration
    # --------------------------------------------------------

    elif config_type == "ip":

        interface = config.get("interface")
        ip = config.get("ip")
        mask = config.get("mask")

        if not interface or not isinstance(interface, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid interface name"
            }

        if not ip or not isinstance(ip, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid IP address"
            }

        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return {
                "success": False,
                "commands": [],
                "error": "Invalid IP address"
            }

        if not mask or not isinstance(mask, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid subnet mask"
            }

        try:
            ipaddress.IPv4Network(
                f"0.0.0.0/{mask}"
            )
        except ValueError:
            return {
                "success": False,
                "commands": [],
                "error": "Invalid subnet mask"
            }

        commands.append(f"interface {interface}")
        commands.append(f"ip address {ip} {mask}")
        commands.append("no shutdown")

    # --------------------------------------------------------
    # Static route configuration
    # --------------------------------------------------------

    elif config_type == "route":

        network = config.get("network")
        mask = config.get("mask")
        gateway = config.get("gateway")

        if not network or not isinstance(network, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid destination network"
            }

        if not mask or not isinstance(mask, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid subnet mask"
            }

        if not gateway or not isinstance(gateway, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid gateway"
            }

        try:
            ipaddress.IPv4Network(
                f"{network}/{mask}",
                strict=True
            )
        except ValueError:
            return {
                "success": False,
                "commands": [],
                "error": "Invalid destination network or subnet mask"
            }

        try:
            ipaddress.IPv4Address(gateway)
        except ValueError:
            return {
                "success": False,
                "commands": [],
                "error": "Invalid gateway"
            }

        commands.append(
            f"ip route {network} {mask} {gateway}"
        )

    else:
        return {
            "success": False,
            "commands": [],
            "error": "Unsupported config type"
        }

    return {
        "success": True,
        "commands": commands,
        "error": ""
    }


def parse_static_route(output, network, mask, gateway):
    """
    Parse static route information from device output.
    """

    if not isinstance(output, str):
        return {
            "success": False,
            "network": network,
            "mask": mask,
            "gateway": None,
            "error": "Invalid command output"
        }

    if not output.strip():
        return {
            "success": False,
            "network": network,
            "mask": mask,
            "gateway": None,
            "error": "Empty command output"
        }

    if not isinstance(network, str) or not network.strip():
        return {
            "success": False,
            "network": network,
            "mask": mask,
            "gateway": None,
            "error": "Invalid destination network"
        }

    if not isinstance(mask, str) or not mask.strip():
        return {
            "success": False,
            "network": network,
            "mask": mask,
            "gateway": None,
            "error": "Invalid subnet mask"
        }

    if not isinstance(gateway, str) or not gateway.strip():
        return {
            "success": False,
            "network": network,
            "mask": mask,
            "gateway": None,
            "error": "Invalid gateway"
        }

    target_network = network.strip()
    target_mask = mask.strip()
    target_gateway = gateway.strip()

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) < 3:
            continue

        actual_network = parts[0]
        actual_mask = parts[1]
        actual_gateway = parts[2]

        if (
            actual_network == target_network
            and actual_mask == target_mask
            and actual_gateway == target_gateway
        ):
            return {
                "success": True,
                "network": actual_network,
                "mask": actual_mask,
                "gateway": actual_gateway,
                "error": None
            }

    return {
        "success": False,
        "network": target_network,
        "mask": target_mask,
        "gateway": None,
        "error": "Static route not found"
    }


def verify_static_route(
    client,
    network,
    mask,
    gateway,
    verification_command="show ip route"
):
    """
    Verify whether the expected static route exists.
    """

    if not isinstance(network, str) or not network.strip():
        return {
            "success": False,
            "verified": False,
            "network": network,
            "mask": mask,
            "gateway": gateway,
            "actual_gateway": None,
            "error": "Invalid destination network"
        }

    if not isinstance(mask, str) or not mask.strip():
        return {
            "success": False,
            "verified": False,
            "network": network,
            "mask": mask,
            "gateway": gateway,
            "actual_gateway": None,
            "error": "Invalid subnet mask"
        }

    if not isinstance(gateway, str) or not gateway.strip():
        return {
            "success": False,
            "verified": False,
            "network": network,
            "mask": mask,
            "gateway": gateway,
            "actual_gateway": None,
            "error": "Invalid gateway"
        }

    command_result = execute_command(
        client,
        verification_command
    )

    if not command_result.get("success"):
        return {
            "success": False,
            "verified": False,
            "network": network,
            "mask": mask,
            "gateway": gateway,
            "actual_gateway": None,
            "error": command_result.get(
                "error",
                "Route verification command failed"
            )
        }

    parsed = parse_static_route(
        command_result.get("output", ""),
        network,
        mask,
        gateway
    )

    if not parsed.get("success"):
        return {
            "success": True,
            "verified": False,
            "network": network,
            "mask": mask,
            "gateway": gateway,
            "actual_gateway": parsed.get("gateway"),
            "error": parsed.get(
                "error",
                "Static route verification failed"
            )
        }

    actual_gateway = parsed.get("gateway")

    if actual_gateway != gateway:
        return {
            "success": True,
            "verified": False,
            "network": network,
            "mask": mask,
            "gateway": gateway,
            "actual_gateway": actual_gateway,
            "error": "Gateway does not match"
        }

    return {
        "success": True,
        "verified": True,
        "network": network,
        "mask": mask,
        "gateway": gateway,
        "actual_gateway": actual_gateway,
        "error": None
    }


def validate_config_commands(commands):
    """
    Validate configuration commands before execution.

    This is a vendor-independent safety layer.
    """

    if not isinstance(commands, list):
        return {
            "success": False,
            "commands": [],
            "error": "Configuration commands must be a list"
        }

    if not commands:
        return {
            "success": False,
            "commands": [],
            "error": "No configuration commands provided"
        }

    normalized_commands = []

    for command in commands:

        if not isinstance(command, str):
            return {
                "success": False,
                "commands": [],
                "error": "Configuration command must be a string"
            }

        normalized_command = command.strip()

        if not normalized_command:
            return {
                "success": False,
                "commands": [],
                "error": "Configuration command cannot be empty"
            }

        normalized_commands.append(normalized_command)

    return {
        "success": True,
        "commands": normalized_commands,
        "error": ""
    }


def dry_run_config(config_type, config):
    """
    Generate and preview configuration commands.
    """

    result = generate_config_commands(
        config_type,
        config
    )

    if not result["success"]:
        return {
            "success": False,
            "dry_run": True,
            "commands": [],
            "error": result["error"]
        }

    return {
        "success": True,
        "dry_run": True,
        "commands": result["commands"],
        "error": ""
    }


def apply_config(client, commands, dry_run=False):
    """
    Apply configuration commands to a connected device.
    """

    if not isinstance(commands, list) or not commands:
        return {
            "success": False,
            "dry_run": dry_run,
            "results": [],
            "error": "No configuration commands provided"
        }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "results": commands,
            "error": ""
        }

    results = []

    for command in commands:

        result = execute_command(
            client,
            command
        )

        results.append({
            "command": command,
            "success": result["success"],
            "output": result["output"],
            "error": result["error"]
        })

        if not result["success"]:
            return {
                "success": False,
                "dry_run": False,
                "results": results,
                "error": result["error"]
            }

    return {
        "success": True,
        "dry_run": False,
        "results": results,
        "error": ""
    }


def parse_interface_description(output, interface):
    """
    Parse interface description output.

    The current parser understands the existing Cisco-style
    'show interfaces description' test format.

    Vendor-specific parsers can be moved to adapters later.
    """

    if not isinstance(interface, str) or not interface.strip():
        return {
            "success": False,
            "interface": interface,
            "status": None,
            "description": None,
            "error": "Invalid interface name"
        }

    if not isinstance(output, str):
        return {
            "success": False,
            "interface": interface,
            "status": None,
            "description": None,
            "error": "Invalid command output"
        }

    if not output.strip():
        return {
            "success": False,
            "interface": interface,
            "status": None,
            "description": None,
            "error": "Empty command output"
        }

    def normalize_interface_name(name):
        name = name.strip()

        prefixes = {
            "gigabitethernet": "Gi",
            "fastethernet": "Fa",
            "tengigabitethernet": "Te"
        }

        lower_name = name.lower()

        for prefix, abbreviation in prefixes.items():

            if lower_name.startswith(prefix):
                return (
                    abbreviation
                    + name[len(prefix):]
                )

        return name

    target_interface = normalize_interface_name(
        interface
    )

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.lower().startswith("interface"):
            continue

        match = re.match(
            r"^(?P<interface>\S+)\s+"
            r"(?P<status>admin(?:istratively)?\s+down|up|down)\s+"
            r"(?P<protocol>administratively\s+down|up|down)\s+"
            r"(?P<description>.*)$",
            line,
            re.IGNORECASE
        )

        if not match:

            first_word = (
                line.split()[0]
                if line.split()
                else ""
            )

            if (
                normalize_interface_name(first_word).lower()
                == target_interface.lower()
            ):
                return {
                    "success": False,
                    "interface": target_interface,
                    "status": None,
                    "description": None,
                    "error": "Unable to parse interface output"
                }

            continue

        actual_interface = normalize_interface_name(
            match.group("interface")
        )

        if (
            actual_interface.lower()
            != target_interface.lower()
        ):
            continue

        actual_status = " ".join(
            match.group("status").lower().split()
        )

        actual_description = (
            match.group("description").strip()
        )

        return {
            "success": True,
            "interface": actual_interface,
            "status": actual_status,
            "description": actual_description,
            "error": None
        }

    return {
        "success": False,
        "interface": target_interface,
        "status": None,
        "description": None,
        "error": "Interface not found"
    }


def verify_interface(
    client,
    interface,
    expected_description,
    expected_status
):
    """
    Verify an interface's description and status.

    Workflow:

        Validate
            ↓
        Execute command
            ↓
        Parse output
            ↓
        Interface Verifier
            ↓
        Standard Verification Result
    """

    # --------------------------------------------------------
    # Validate interface
    # --------------------------------------------------------

    if not isinstance(interface, str) or not interface.strip():

        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_description": expected_description,
            "actual_description": None,
            "expected_status": expected_status,
            "actual_status": None,
            "error": "Invalid interface name"
        }

    # --------------------------------------------------------
    # Validate expected description
    # --------------------------------------------------------

    if not isinstance(expected_description, str):

        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_description": expected_description,
            "actual_description": None,
            "expected_status": expected_status,
            "actual_status": None,
            "error": "Invalid expected interface description"
        }

    # --------------------------------------------------------
    # Validate expected status
    # --------------------------------------------------------

    if expected_status not in ["up", "down"]:

        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_description": expected_description,
            "actual_description": None,
            "expected_status": expected_status,
            "actual_status": None,
            "error": "Invalid expected interface status"
        }

    # --------------------------------------------------------
    # Execute verification command
    # --------------------------------------------------------

    result = execute_command(
        client,
        "show interfaces description"
    )

    if not result.get("success"):

        verification = verification_error(
            target=interface,
            expected={
                "description": expected_description,
                "status": expected_status
            },
            error=result.get(
                "error",
                "Interface verification command failed"
            )
        )

        return {
            "success": verification["success"],
            "verified": verification["verified"],
            "interface": interface,
            "expected_description": expected_description,
            "actual_description": None,
            "expected_status": expected_status,
            "actual_status": None,
            "error": verification["error"]
        }

    # --------------------------------------------------------
    # Parse device output
    # --------------------------------------------------------

    parsed = parse_interface_description(
        result.get("output", ""),
        interface
    )

    if not parsed.get("success"):

        verification = verification_error(
            target=interface,
            expected={
                "description": expected_description,
                "status": expected_status
            },
            actual={
                "description": parsed.get("description"),
                "status": parsed.get("status")
            },
            error=parsed.get(
                "error",
                "Interface parsing failed"
            )
        )

        return {
            "success": verification["success"],
            "verified": verification["verified"],
            "interface": interface,
            "expected_description": expected_description,
            "actual_description": parsed.get("description"),
            "expected_status": expected_status,
            "actual_status": parsed.get("status"),
            "error": verification["error"]
        }

    # --------------------------------------------------------
    # Delegate comparison to Phase 5.2 verifier
    # --------------------------------------------------------

    verification = verify_interface_state(
        interface=interface,
        expected_description=expected_description,
        expected_status=expected_status,
        actual_description=parsed.get("description"),
        actual_status=parsed.get("status")
    )

    # --------------------------------------------------------
    # Preserve existing external contract
    # --------------------------------------------------------

    return {
        "success": verification["success"],
        "verified": verification["verified"],
        "interface": interface,
        "expected_description": expected_description,
        "actual_description": parsed.get("description"),
        "expected_status": expected_status,
        "actual_status": parsed.get("status"),
        "error": verification["error"]
    }


def parse_interface_ip(output, interface):
    """
    Parse interface IP information.
    """

    if not isinstance(interface, str) or not interface.strip():
        return {
            "success": False,
            "interface": interface,
            "ip": None,
            "mask": None,
            "error": "Invalid interface name"
        }

    if not isinstance(output, str):
        return {
            "success": False,
            "interface": interface,
            "ip": None,
            "mask": None,
            "error": "Invalid command output"
        }

    if not output.strip():
        return {
            "success": False,
            "interface": interface,
            "ip": None,
            "mask": None,
            "error": "Empty command output"
        }

    def normalize_interface_name(name):

        name = name.strip()

        prefixes = {
            "gigabitethernet": "Gi",
            "fastethernet": "Fa",
            "tengigabitethernet": "Te"
        }

        lower_name = name.lower()

        for prefix, abbreviation in prefixes.items():

            if lower_name.startswith(prefix):
                return (
                    abbreviation
                    + name[len(prefix):]
                )

        return name

    target_interface = normalize_interface_name(
        interface
    )

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        match = re.match(
            r"^(?P<interface>\S+)\s+"
            r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
            r"(?P<mask>\d+\.\d+\.\d+\.\d+)",
            line
        )

        if not match:
            continue

        actual_interface = normalize_interface_name(
            match.group("interface")
        )

        if (
            actual_interface.lower()
            != target_interface.lower()
        ):
            continue

        return {
            "success": True,
            "interface": actual_interface,
            "ip": match.group("ip"),
            "mask": match.group("mask"),
            "error": None
        }

    return {
        "success": False,
        "interface": target_interface,
        "ip": None,
        "mask": None,
        "error": "Interface IP information not found"
    }


def verify_ip_configuration(
    client,
    interface,
    expected_ip,
    expected_mask
):
    """
    Verify IP configuration on a network device.
    """

    if not isinstance(interface, str) or not interface.strip():
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_ip": expected_ip,
            "actual_ip": None,
            "expected_mask": expected_mask,
            "actual_mask": None,
            "error": "Invalid interface"
        }

    try:
        ipaddress.ip_address(expected_ip)
    except (TypeError, ValueError):
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_ip": expected_ip,
            "actual_ip": None,
            "expected_mask": expected_mask,
            "actual_mask": None,
            "error": "Invalid IP address"
        }

    try:
        ipaddress.IPv4Network(
            f"0.0.0.0/{expected_mask}"
        )
    except (TypeError, ValueError):
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_ip": expected_ip,
            "actual_ip": None,
            "expected_mask": expected_mask,
            "actual_mask": None,
            "error": "Invalid subnet mask"
        }

    result = execute_command(
        client,
        "show ip interface brief"
    )

    if not result.get("success"):
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_ip": expected_ip,
            "actual_ip": None,
            "expected_mask": expected_mask,
            "actual_mask": None,
            "error": result.get("error")
        }

    parsed = parse_interface_ip(
        result.get("output", ""),
        interface
    )

    if not parsed.get("success"):
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_ip": expected_ip,
            "actual_ip": parsed.get("ip"),
            "expected_mask": expected_mask,
            "actual_mask": parsed.get("mask"),
            "error": parsed.get("error")
        }

    actual_ip = parsed.get("ip")
    actual_mask = parsed.get("mask")

    if (
        actual_ip == expected_ip
        and actual_mask == expected_mask
    ):
        return {
            "success": True,
            "verified": True,
            "interface": interface,
            "expected_ip": expected_ip,
            "actual_ip": actual_ip,
            "expected_mask": expected_mask,
            "actual_mask": actual_mask,
            "error": None
        }

    return {
        "success": True,
        "verified": False,
        "interface": interface,
        "expected_ip": expected_ip,
        "actual_ip": actual_ip,
        "expected_mask": expected_mask,
        "actual_mask": actual_mask,
        "error": "IP configuration verification failed"
    }


def configure_ip(
    client,
    interface,
    ip,
    mask,
    dry_run=False
):
    """
    Complete IP configuration workflow.

    Validate
    -> Generate
    -> Preview
    -> Apply
    -> Verify
    """

    config = {
        "interface": interface,
        "ip": ip,
        "mask": mask
    }

    generated = generate_config_commands(
        "ip",
        config
    )

    if not generated["success"]:
        return {
            "success": False,
            "dry_run": dry_run,
            "interface": interface,
            "ip": ip,
            "mask": mask,
            "commands": [],
            "apply": None,
            "verification": None,
            "error": generated["error"]
        }

    commands = generated["commands"]

    preview = dry_run_config(
        "ip",
        config
    )

    if not preview["success"]:
        return {
            "success": False,
            "dry_run": dry_run,
            "interface": interface,
            "ip": ip,
            "mask": mask,
            "commands": commands,
            "apply": None,
            "verification": None,
            "error": preview["error"]
        }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "interface": interface,
            "ip": ip,
            "mask": mask,
            "commands": preview["commands"],
            "apply": None,
            "verification": None,
            "error": ""
        }

    apply_result = apply_config(
        client,
        commands,
        dry_run=False
    )

    if not apply_result["success"]:
        return {
            "success": False,
            "dry_run": False,
            "interface": interface,
            "ip": ip,
            "mask": mask,
            "commands": commands,
            "apply": apply_result,
            "verification": None,
            "error": apply_result["error"]
        }

    verification = verify_ip_configuration(
        client,
        interface,
        ip,
        mask
    )

    if (
        not verification["success"]
        or not verification["verified"]
    ):
        return {
            "success": False,
            "dry_run": False,
            "interface": interface,
            "ip": ip,
            "mask": mask,
            "commands": commands,
            "apply": apply_result,
            "verification": verification,
            "error": verification["error"]
        }

    return {
        "success": True,
        "dry_run": False,
        "interface": interface,
        "ip": ip,
        "mask": mask,
        "commands": commands,
        "apply": apply_result,
        "verification": verification,
        "error": ""
    }


def configure_interface(
    client,
    interface,
    description,
    status,
    dry_run=False
):
    """
    Complete interface configuration workflow.

    Validate
    -> Generate
    -> Preview
    -> Apply
    -> Verify
    """

    config = {
        "interface": interface,
        "description": description,
        "status": status
    }

    generated = generate_config_commands(
        "interface",
        config
    )

    if not generated["success"]:
        return {
            "success": False,
            "dry_run": dry_run,
            "interface": interface,
            "description": description,
            "status": status,
            "commands": [],
            "apply": None,
            "verification": None,
            "error": generated["error"]
        }

    commands = generated["commands"]

    preview = dry_run_config(
        "interface",
        config
    )

    if not preview["success"]:
        return {
            "success": False,
            "dry_run": dry_run,
            "interface": interface,
            "description": description,
            "status": status,
            "commands": commands,
            "apply": None,
            "verification": None,
            "error": preview["error"]
        }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "interface": interface,
            "description": description,
            "status": status,
            "commands": preview["commands"],
            "apply": None,
            "verification": None,
            "error": ""
        }

    apply_result = apply_config(
        client,
        commands,
        dry_run=False
    )

    if not apply_result["success"]:
        return {
            "success": False,
            "dry_run": False,
            "interface": interface,
            "description": description,
            "status": status,
            "commands": commands,
            "apply": apply_result,
            "verification": None,
            "error": apply_result["error"]
        }

    verification = verify_interface(
        client,
        interface,
        description,
        status
    )

    if (
        not verification["success"]
        or not verification["verified"]
    ):
        return {
            "success": False,
            "dry_run": False,
            "interface": interface,
            "description": description,
            "status": status,
            "commands": commands,
            "apply": apply_result,
            "verification": verification,
            "error": verification["error"]
        }

    return {
        "success": True,
        "dry_run": False,
        "interface": interface,
        "description": description,
        "status": status,
        "commands": commands,
        "apply": apply_result,
        "verification": verification,
        "error": ""
    }


def verify_vlan(client, vlan_id, expected_name):
    """
    Verify VLAN existence and name.
    """

    if not isinstance(vlan_id, int) or not 1 <= vlan_id <= 4094:
        return {
            "success": False,
            "verified": False,
            "vlan_id": vlan_id,
            "expected_name": expected_name,
            "actual_name": None,
            "error": "Invalid VLAN ID"
        }

    if not expected_name or not isinstance(expected_name, str):
        return {
            "success": False,
            "verified": False,
            "vlan_id": vlan_id,
            "expected_name": expected_name,
            "actual_name": None,
            "error": "Invalid VLAN name"
        }

    result = execute_command(
        client,
        "show vlan brief"
    )

    if not result["success"]:
        return {
            "success": False,
            "verified": False,
            "vlan_id": vlan_id,
            "expected_name": expected_name,
            "actual_name": None,
            "error": result["error"]
        }

    for line in result["output"].splitlines():

        parts = line.split()

        if len(parts) < 2:
            continue

        try:
            device_vlan_id = int(parts[0])
        except ValueError:
            continue

        if device_vlan_id != vlan_id:
            continue

        actual_name = parts[1]

        if actual_name == expected_name:
            return {
                "success": True,
                "verified": True,
                "vlan_id": vlan_id,
                "expected_name": expected_name,
                "actual_name": actual_name,
                "error": None
            }

        return {
            "success": True,
            "verified": False,
            "vlan_id": vlan_id,
            "expected_name": expected_name,
            "actual_name": actual_name,
            "error": "VLAN name does not match"
        }

    return {
        "success": True,
        "verified": False,
        "vlan_id": vlan_id,
        "expected_name": expected_name,
        "actual_name": None,
        "error": "VLAN not found"
    }


def configure_vlan(
    client,
    vlan_id,
    name,
    dry_run=False
):
    """
    Complete VLAN configuration workflow.

    Validate
    -> Generate
    -> Preview
    -> Apply
    -> Verify
    """

    config = {
        "vlan_id": vlan_id,
        "name": name
    }

    generated = generate_config_commands(
        "vlan",
        config
    )

    if not generated["success"]:
        return {
            "success": False,
            "dry_run": dry_run,
            "commands": [],
            "apply": None,
            "verification": None,
            "error": generated["error"]
        }

    commands = generated["commands"]

    preview = dry_run_config(
        "vlan",
        config
    )

    if not preview["success"]:
        return {
            "success": False,
            "dry_run": dry_run,
            "commands": commands,
            "apply": None,
            "verification": None,
            "error": preview["error"]
        }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "commands": preview["commands"],
            "apply": None,
            "verification": None,
            "error": ""
        }

    apply_result = apply_config(
        client,
        commands,
        dry_run=False
    )

    if not apply_result["success"]:
        return {
            "success": False,
            "dry_run": False,
            "commands": commands,
            "apply": apply_result,
            "verification": None,
            "error": apply_result["error"]
        }

    verification = verify_vlan(
        client,
        vlan_id,
        name
    )

    if (
        not verification["success"]
        or not verification["verified"]
    ):
        return {
            "success": False,
            "dry_run": False,
            "commands": commands,
            "apply": apply_result,
            "verification": verification,
            "error": verification["error"]
        }

    return {
        "success": True,
        "dry_run": False,
        "commands": commands,
        "apply": apply_result,
        "verification": verification,
        "error": ""
    }