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