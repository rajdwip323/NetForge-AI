import paramiko


def connect_ssh(host, username, password, port=22, timeout=5):
    """
    Establish an SSH connection to a network device.
    """

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout
        )

        return {
            "success": True,
            "message": "SSH connection successful",
            "client": client
        }

    except paramiko.AuthenticationException:
        client.close()

        return {
            "success": False,
            "message": "SSH authentication failed",
            "client": None
        }

    except paramiko.SSHException as e:
        client.close()

        return {
            "success": False,
            "message": f"SSH error: {e}",
            "client": None
        }

    except Exception as e:
        client.close()

        return {
            "success": False,
            "message": f"Connection error: {e}",
            "client": None
        }


def execute_command(client, command):
    """
    Execute a command on an established SSH connection.
    """

    try:
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            return {
                "success": False,
                "output": output,
                "error": error
            }

        return {
            "success": True,
            "output": output,
            "error": ""
        }

    except paramiko.SSHException as e:
        return {
            "success": False,
            "output": "",
            "error": f"SSH error: {e}"
        }

    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Command execution error: {e}"
        }  