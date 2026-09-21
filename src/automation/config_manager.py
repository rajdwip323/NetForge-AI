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

        if not mask or not isinstance(mask, str):
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
    Validate → Generate → Preview → Apply → Verify

    If dry_run is True:
    Validate → Generate → Preview

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