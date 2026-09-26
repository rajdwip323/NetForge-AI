from ssh.ssh_manager import connect_ssh, execute_command


def execute_on_devices(devices, command):
    """
    Execute the same command on multiple network devices sequentially.

    Each device is handled independently.
    A failure on one device does not stop the remaining devices.

    Returns:
        success
        total
        successful
        failed
        results
        error
    """

    # Validate devices
    if not isinstance(devices, list) or not devices:
        return {
            "success": False,
            "total": 0,
            "successful": 0,
            "failed": 0,
            "results": [],
            "error": "No devices provided"
        }

    # Validate command
    if not isinstance(command, str) or not command.strip():
        return {
            "success": False,
            "total": len(devices),
            "successful": 0,
            "failed": 0,
            "results": [],
            "error": "Invalid command"
        }

    command = command.strip()

    results = []

    for device in devices:

        # Validate individual device entry
        if not isinstance(device, dict):
            results.append({
                "host": None,
                "success": False,
                "output": "",
                "error": "Invalid device entry"
            })
            continue

        host = device.get("host")
        username = device.get("username")
        password = device.get("password")
        port = device.get("port", 22)

        if (
            not isinstance(host, str)
            or not host.strip()
            or not isinstance(username, str)
            or not username.strip()
            or not isinstance(password, str)
            or not password
        ):
            results.append({
                "host": host,
                "success": False,
                "output": "",
                "error": "Invalid device credentials"
            })
            continue

        connection = connect_ssh(
            host,
            username,
            password,
            port
        )

        if not connection["success"]:
            results.append({
                "host": host,
                "success": False,
                "output": "",
                "error": connection["message"]
            })
            continue

        client = connection["client"]

        try:
            result = execute_command(
                client,
                command
            )

            results.append({
                "host": host,
                "success": result["success"],
                "output": result["output"],
                "error": result["error"]
            })

        except Exception as exc:
            results.append({
                "host": host,
                "success": False,
                "output": "",
                "error": str(exc)
            })

        finally:
            try:
                client.close()
            except Exception:
                pass

    successful = sum(
        1
        for result in results
        if result["success"]
    )

    failed = len(results) - successful

    return {
        "success": failed == 0,
        "total": len(devices),
        "successful": successful,
        "failed": failed,
        "results": results,
        "error": None if failed == 0 else "One or more devices failed"
    }