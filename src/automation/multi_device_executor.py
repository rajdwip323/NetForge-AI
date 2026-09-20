from ssh.ssh_manager import connect_ssh, execute_command


def execute_on_devices(devices, command):
    """
    Execute the same command on multiple network devices sequentially.

    devices:
        List of dictionaries containing host, username, password,
        and optional port.

    command:
        Command to execute on every device.
    """

    results = []

    for device in devices:
        host = device.get("host")
        username = device.get("username")
        password = device.get("password")
        port = device.get("port", 22)

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

        result = execute_command(client, command)

        results.append({
            "host": host,
            "success": result["success"],
            "output": result["output"],
            "error": result["error"]
        })

        client.close()

    return results