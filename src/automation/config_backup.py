import os
from datetime import datetime

from ssh.ssh_manager import execute_command


def backup_configuration(
    client,
    backup_command="show running-config"
):
    """
    Retrieve the current device configuration.

    The actual backup command can be supplied by a
    vendor-specific adapter in the future.
    """

    if client is None:
        return {
            "success": False,
            "backup": None,
            "command": backup_command,
            "timestamp": None,
            "error": "Invalid client"
        }

    if not isinstance(backup_command, str) or not backup_command.strip():
        return {
            "success": False,
            "backup": None,
            "command": backup_command,
            "timestamp": None,
            "error": "Invalid backup command"
        }

    result = execute_command(
        client,
        backup_command
    )

    if not result.get("success"):
        return {
            "success": False,
            "backup": None,
            "command": backup_command,
            "timestamp": None,
            "error": result.get(
                "error",
                "Configuration backup command failed"
            )
        }

    output = result.get("output", "")

    if not isinstance(output, str) or not output.strip():
        return {
            "success": False,
            "backup": None,
            "command": backup_command,
            "timestamp": None,
            "error": "Empty configuration output"
        }

    return {
        "success": True,
        "backup": output,
        "command": backup_command,
        "timestamp": datetime.now().isoformat(),
        "error": None
    }


def save_configuration_backup(
    backup,
    backup_directory="backups",
    filename=None
):
    """
    Save configuration backup to a local file.
    """

    if not isinstance(backup, str) or not backup.strip():
        return {
            "success": False,
            "path": None,
            "error": "Invalid backup data"
        }

    if not isinstance(backup_directory, str) or not backup_directory.strip():
        return {
            "success": False,
            "path": None,
            "error": "Invalid backup directory"
        }

def restore_configuration(
    client,
    backup,
    restore_command_prefix="configure replace"
):
    """
    Restore a previously saved configuration backup.

    The restore command prefix can be supplied by a
    vendor-specific adapter in the future.
    """

    if client is None:
        return {
            "success": False,
            "restored": False,
            "error": "Invalid client"
        }

    if not isinstance(backup, str) or not backup.strip():
        return {
            "success": False,
            "restored": False,
            "error": "Invalid backup data"
        }

    if (
        not isinstance(restore_command_prefix, str)
        or not restore_command_prefix.strip()
    ):
        return {
            "success": False,
            "restored": False,
            "error": "Invalid restore command"
        }

    # The actual device-specific restore mechanism
    # should be supplied by a vendor adapter.
    restore_command = (
        f"{restore_command_prefix.strip()} {backup.strip()}"
    )

    result = execute_command(
        client,
        restore_command
    )

    if not result.get("success"):
        return {
            "success": False,
            "restored": False,
            "command": restore_command,
            "error": result.get(
                "error",
                "Configuration restore failed"
            )
        }

    return {
        "success": True,
        "restored": True,
        "command": restore_command,
        "output": result.get("output", ""),
        "error": None
    }

    try:
        os.makedirs(
            backup_directory,
            exist_ok=True
        )

        if filename is None:
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            filename = f"config_backup_{timestamp}.txt"

        if not isinstance(filename, str) or not filename.strip():
            return {
                "success": False,
                "path": None,
                "error": "Invalid backup filename"
            }

        backup_path = os.path.join(
            backup_directory,
            filename
        )

        with open(
            backup_path,
            "w",
            encoding="utf-8"
        ) as backup_file:
            backup_file.write(backup)

        return {
            "success": True,
            "path": backup_path,
            "error": None
        }

    except OSError as exc:
        return {
            "success": False,
            "path": None,
            "error": str(exc)
        }

def recover_from_backup(
    client,
    backup,
    restore_command_prefix="configure replace"
):
    """
    Recover device configuration from a previously
    captured backup.

    This function performs the recovery operation only.
    Verification of the restored state is handled by
    the caller or a vendor-specific workflow.
    """

    if client is None:
        return {
            "success": False,
            "recovered": False,
            "error": "Invalid client"
        }

    if not isinstance(backup, str) or not backup.strip():
        return {
            "success": False,
            "recovered": False,
            "error": "Invalid backup data"
        }

    restore_result = restore_configuration(
        client,
        backup,
        restore_command_prefix
    )

    if not restore_result["success"]:
        return {
            "success": False,
            "recovered": False,
            "restore": restore_result,
            "error": restore_result["error"]
        }

    return {
        "success": True,
        "recovered": True,
        "restore": restore_result,
        "error": None
    }