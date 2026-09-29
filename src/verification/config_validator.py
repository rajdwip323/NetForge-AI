"""
NETFORGE-AI Configuration Validator

Phase 5.6:
Configuration validation foundation.

This module is vendor-independent.

It validates the basic structure and safety
of configuration command input before execution.
"""


def validate_configuration(commands):
    """
    Validate a configuration command collection.

    Returns:
        {
            "valid": True/False,
            "commands": [...],
            "errors": [...]
        }
    """

    errors = []

    # Validate command collection
    if not isinstance(commands, (list, tuple)):
        return {
            "valid": False,
            "commands": commands,
            "errors": [
                "Configuration commands must be a list or tuple"
            ]
        }

    # Validate individual commands
    for index, command in enumerate(commands):

        if not isinstance(command, str):
            errors.append(
                f"Command {index + 1} must be a string"
            )
            continue

        if not command.strip():
            errors.append(
                f"Command {index + 1} cannot be empty"
            )

    return {
        "valid": len(errors) == 0,
        "commands": list(commands),
        "errors": errors
    }
