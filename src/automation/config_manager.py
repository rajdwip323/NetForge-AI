import ipaddress
from ssh.ssh_manager import execute_command



def generate_config_commands(config_type, config):
    """
    Generate network device configuration commands.

    This function only generates commands.
    It does not connect to or modify any device.
    """

    commands = []

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

    elif config_type == "ip":
        interface = config.get("interface")
        ip = config.get("ip")
        mask = config.get("mask")

        # Validate interface
        if not interface or not isinstance(interface, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid interface name"
            }

        # Validate IP address
        if not ip or not isinstance(ip, str):
            return {
                "success": False,
                "commands": [],
                "error": "Invalid IP address"
            }

        try:
            import ipaddress
            ipaddress.ip_address(ip)
        except ValueError:
            return {
                "success": False,
                "commands": [],
                "error": "Invalid IP address"
            }

        # Validate subnet mask
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

        commands.append(f"ip route {network} {mask} {gateway}")

    else:
        return {
            "success": False,
            "commands": [],
            "error": "Unsupported configuration type"
        }

    return {
        "success": True,
        "commands": commands,
        "error": ""
    }


def dry_run_config(config_type, config):
    """
    Generate and preview configuration commands
    without executing them on a device.
    """

    result = generate_config_commands(config_type, config)

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

    If dry_run is True, commands are only returned for preview
    and are not executed.
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
        result = execute_command(client, command)

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
    Parse Cisco 'show interfaces description' output
    for a specific interface.

    Returns:
        success      -> Parsing operation successful or not
        interface    -> Normalized interface name
        status       -> Actual interface status
        description  -> Actual interface description
        error        -> Error message if parsing fails
    """

    # Validate interface input
    if not isinstance(interface, str) or not interface.strip():
        return {
            "success": False,
            "interface": interface,
            "status": None,
            "description": None,
            "error": "Invalid interface name"
        }

    # Validate command output
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
        """
        Normalize common Cisco interface name formats.

        Example:
        GigabitEthernet0/1 -> Gi0/1
        FastEthernet0/1   -> Fa0/1
        TenGigabitEthernet0/1 -> Te0/1
        """

        name = name.strip()

        prefixes = {
            "gigabitethernet": "Gi",
            "fastethernet": "Fa",
            "tengigabitethernet": "Te"
        }

        lower_name = name.lower()

        for prefix, abbreviation in prefixes.items():
            if lower_name.startswith(prefix):
                return abbreviation + name[len(prefix):]

        return name

    target_interface = normalize_interface_name(interface)

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        # Skip header/separator lines
        if line.lower().startswith("interface"):
            continue

        # Cisco show interfaces description format:
        #
        # Gi0/1    up          up       UPLINK_TO_CORE
        # Gi0/2    admin down  down     USER_ACCESS
        #
        import re

        match = re.match(
            r"^(?P<interface>\S+)\s+"
            r"(?P<status>admin(?:istratively)?\s+down|up|down)\s+"
            r"(?P<protocol>administratively\s+down|up|down)\s*"
            r"(?P<description>.*)$",
            line,
            re.IGNORECASE
        )

        if not match:

            # Check whether this malformed line belongs
            # to the requested interface.
            first_word = line.split()[0] if line.split() else ""

            if normalize_interface_name(first_word).lower() == target_interface.lower():
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

        if actual_interface.lower() != target_interface.lower():
            continue

        actual_status = " ".join(
            match.group("status").lower().split()
        )

        actual_description = match.group("description").strip()

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
    Verify an interface's description and operational status.

    Workflow:
    Validate â†’ Execute show command â†’ Parse â†’ Compare â†’ Verify

    This function does not modify the device.
    """

    # Validate interface
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

    # Validate expected description
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

    # Validate expected status
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

    # Execute verification command
    result = execute_command(
        client,
        "show interfaces description"
    )

    if not result["success"]:
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_description": expected_description,
            "actual_description": None,
            "expected_status": expected_status,
            "actual_status": None,
            "error": result["error"]
        }

    # Parse device output
    parsed = parse_interface_description(
        result["output"],
        interface
    )

    if not parsed["success"]:
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_description": expected_description,
            "actual_description": parsed["description"],
            "expected_status": expected_status,
            "actual_status": parsed["status"],
            "error": parsed["error"]
        }

    # Extract actual values
    actual_description = parsed["description"]
    actual_status = parsed["status"]

    # Compare expected vs actual
    description_match = (
        actual_description == expected_description
    )

    status_match = (
        actual_status == expected_status
    )

    # Both values match
    if description_match and status_match:
        return {
            "success": True,
            "verified": True,
            "interface": interface,
            "expected_description": expected_description,
            "actual_description": actual_description,
            "expected_status": expected_status,
            "actual_status": actual_status,
            "error": None
        }

    # Device responded successfully,
    # but actual configuration does not match expected.
    return {
        "success": True,
        "verified": False,
        "interface": interface,
        "expected_description": expected_description,
        "actual_description": actual_description,
        "expected_status": expected_status,
        "actual_status": actual_status,
        "error": "Interface verification failed"
    }



def parse_interface_ip(output, interface):
    """
    Parse interface IP information from device command output.

    Returns:
        success
        interface
        ip
        mask
        error
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
                return abbreviation + name[len(prefix):]

        return name

    target_interface = normalize_interface_name(interface)

    import re

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

        if actual_interface.lower() != target_interface.lower():
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

    Compares expected IP/mask with the parsed device output.
    """

    # Validate interface
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

    # Validate expected IP
    try:
        ipaddress.ip_address(expected_ip)
    except ValueError:
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

    # Validate expected mask
    try:
        ipaddress.IPv4Network(
            f"0.0.0.0/{expected_mask}"
        )
    except ValueError:
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

    # Get device IP information
    result = execute_command(
        client,
        "show ip interface brief"
    )

    if not result["success"]:
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_ip": expected_ip,
            "actual_ip": None,
            "expected_mask": expected_mask,
            "actual_mask": None,
            "error": result["error"]
        }

    # Parse interface IP information
    parsed = parse_interface_ip(
        result["output"],
        interface
    )

    if not parsed["success"]:
        return {
            "success": False,
            "verified": False,
            "interface": interface,
            "expected_ip": expected_ip,
            "actual_ip": parsed.get("ip"),
            "expected_mask": expected_mask,
            "actual_mask": parsed.get("mask"),
            "error": parsed["error"]
        }

    actual_ip = parsed["ip"]
    actual_mask = parsed["mask"]

    # Compare expected vs actual
    ip_match = actual_ip == expected_ip
    mask_match = actual_mask == expected_mask

    if ip_match and mask_match:
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

    # Device responded, but state does not match
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

    Workflow:
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

    # Step 1: Validate + Generate
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

    # Step 2: Preview
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

    # Dry-run stops after preview
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

    # Step 3: Apply
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

    # Step 4: Verify
    verification = verify_ip_configuration(
        client,
        interface,
        ip,
        mask
    )

    if not verification["success"] or not verification["verified"]:
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

    # Complete workflow successful
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

    Workflow:
    Validate â†’ Generate â†’ Preview â†’ Apply â†’ Verify

    If dry_run is True:
    Validate â†’ Generate â†’ Preview

    No device changes are made during dry run.
    """

    config = {
        "interface": interface,
        "description": description,
        "status": status
    }

    # Step 1: Validate + Generate
    generated = generate_config_commands("interface", config)

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

    # Step 2: Preview
    preview = dry_run_config("interface", config)

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

    # Dry-run stops after preview
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

    # Step 3: Apply
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

    # Step 4: Verify
    verification = verify_interface(
        client,
        interface,
        description,
        status
    )

    if not verification["success"] or not verification["verified"]:
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

    # Complete workflow successful
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
    Verify that a VLAN exists on the device and
    that its name matches the expected name.

    This function does not modify the device.
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

    result = execute_command(client, "show vlan brief")

    if not result["success"]:
        return {
            "success": False,
            "verified": False,
            "vlan_id": vlan_id,
            "expected_name": expected_name,
            "actual_name": None,
            "error": result["error"]
        }

    output = result["output"]

    for line in output.splitlines():
        parts = line.split()

        if len(parts) < 2:
            continue

        try:
            device_vlan_id = int(parts[0])
        except ValueError:
            continue

        if device_vlan_id == vlan_id:
            actual_name = parts[1]

            if actual_name == expected_name:
                return {
                    "success": True,
                    "verified": True,
                    "vlan_id": vlan_id,
                    "expected_name": expected_name,
                    "actual_name": actual_name,
                    "error": ""
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



def configure_vlan(client, vlan_id, name, dry_run=False):
    """
    Complete VLAN configuration workflow.

    Workflow:
    Validate â†’ Generate â†’ Preview â†’ Apply â†’ Verify

    If dry_run is True:
    Validate â†’ Generate â†’ Preview

    No device changes are made during dry run.
    """

    config = {
        "vlan_id": vlan_id,
        "name": name
    }

    # Step 1: Validate + Generate
    generated = generate_config_commands("vlan", config)

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

    # Step 2: Preview
    preview = dry_run_config("vlan", config)

    if not preview["success"]:
        return {
            "success": False,
            "dry_run": dry_run,
            "commands": commands,
            "apply": None,
            "verification": None,
            "error": preview["error"]
        }

    # Dry-run stops after preview
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "commands": preview["commands"],
            "apply": None,
            "verification": None,
            "error": ""
        }

    # Step 3: Apply
    apply_result = apply_config(client, commands, dry_run=False)

    if not apply_result["success"]:
        return {
            "success": False,
            "dry_run": False,
            "commands": commands,
            "apply": apply_result,
            "verification": None,
            "error": apply_result["error"]
        }

    # Step 4: Verify
    verification = verify_vlan(client, vlan_id, name)

    if not verification["success"] or not verification["verified"]:
        return {
            "success": False,
            "dry_run": False,
            "commands": commands,
            "apply": apply_result,
            "verification": verification,
            "error": verification["error"]
        }

    # Complete workflow successful
    return {
        "success": True,
        "dry_run": False,
        "commands": commands,
        "apply": apply_result,
        "verification": verification,
        "error": ""
    }
