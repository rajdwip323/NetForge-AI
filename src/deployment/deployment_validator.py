
"""
NETFORGE-AI Phase 7.10.2
Deployment Action Validation

Vendor-independent validation only.
No vendor commands and no device execution.
"""

import re
import unicodedata


RESOURCE_OPERATIONS = {
    "interface": {
        "configure": {
            "required": {"name"},
            "optional": {"description", "admin_state"},
        },
        "enable": {
            "required": {"name"},
            "optional": set(),
        },
        "disable": {
            "required": {"name"},
            "optional": set(),
        },
    },
    "vlan": {
        "create": {
            "required": {"vlan_id"},
            "optional": {"name"},
        },
        "configure": {
            "required": {"vlan_id", "name"},
            "optional": set(),
        },
        "delete": {
            "required": {"vlan_id"},
            "optional": set(),
        },
    },
}

ACTION_REQUIRED_FIELDS = {
    "action_id",
    "resource",
    "operation",
    "parameters",
}


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _contains_control_characters(value):
    return any(
        unicodedata.category(character) == "Cc"
        for character in value
    )


def _is_valid_interface_name(value):
    """
    Accept common vendor-independent interface-name characters.

    Examples:
        GigabitEthernet0/1
        ge-0/0/0
        Ethernet1/1
        ens33
    """

    if not _is_non_empty_string(value):
        return False

    if _contains_control_characters(value):
        return False

    return re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._:/-]*",
        value,
    ) is not None


def _validate_vlan_id(value):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and 1 <= value <= 4094
    )


def _validate_parameters(resource, operation, parameters, errors, index):

    if not isinstance(parameters, dict):
        errors.append(
            f"Action {index}: parameters must be a dictionary"
        )
        return

    if any(not isinstance(key, str) for key in parameters):
        errors.append(
            f"Action {index}: parameter keys must be strings"
        )
        return

    schema = RESOURCE_OPERATIONS[resource][operation]

    required = schema["required"]
    optional = schema["optional"]

    missing = required - set(parameters)
    unknown = set(parameters) - required - optional

    for field in sorted(missing):
        errors.append(
            f"Action {index}: missing required parameter '{field}'"
        )

    for field in sorted(unknown):
        errors.append(
            f"Action {index}: unsupported parameter '{field}'"
        )

    if "name" in parameters:
        name = parameters["name"]

        if resource == "interface":
            if not _is_valid_interface_name(name):
                errors.append(
                    f"Action {index}: invalid interface name"
                )
        else:
            if (
                not _is_non_empty_string(name)
                or _contains_control_characters(name)
            ):
                errors.append(
                    f"Action {index}: name must be a non-empty "
                    "string without control characters"
                )

    if "description" in parameters:
        description = parameters["description"]

        if (
            not isinstance(description, str)
            or _contains_control_characters(description)
        ):
            errors.append(
                f"Action {index}: description must be a string "
                "without control characters"
            )

    if "admin_state" in parameters:
        if parameters["admin_state"] not in ("up", "down"):
            errors.append(
                f"Action {index}: admin_state must be 'up' or 'down'"
            )

    if "vlan_id" in parameters:
        if not _validate_vlan_id(parameters["vlan_id"]):
            errors.append(
                f"Action {index}: vlan_id must be an integer "
                "between 1 and 4094"
            )


def validate_deployment_plan(plan):
    """
    Validate deployment action structure and parameters.

    Returns:
        {
            "valid": bool,
            "errors": list
        }

    This function never modifies the original plan.
    It never generates or executes vendor commands.
    """

    errors = []

    if not isinstance(plan, dict):
        return {
            "valid": False,
            "errors": ["Deployment plan must be a dictionary"],
        }

    actions = plan.get("actions")

    if not isinstance(actions, list) or not actions:
        return {
            "valid": False,
            "errors": [
                "Deployment plan must contain a non-empty actions list"
            ],
        }

    seen_action_ids = set()

    for index, action in enumerate(actions, start=1):

        if not isinstance(action, dict):
            errors.append(
                f"Action {index}: action must be a dictionary"
            )
            continue

        if any(not isinstance(key, str) for key in action):
            errors.append(
                f"Action {index}: action field keys must be strings"
            )
            continue

        missing_fields = ACTION_REQUIRED_FIELDS - set(action)
        unknown_fields = set(action) - ACTION_REQUIRED_FIELDS

        for field in sorted(missing_fields):
            errors.append(
                f"Action {index}: missing required field '{field}'"
            )

        for field in sorted(unknown_fields):
            errors.append(
                f"Action {index}: unsupported field '{field}'"
            )

        action_id = action.get("action_id")
        resource = action.get("resource")
        operation = action.get("operation")
        parameters = action.get("parameters")

        if not _is_non_empty_string(action_id):
            errors.append(
                f"Action {index}: action_id must be a non-empty string"
            )
        else:
            normalized_id = action_id.strip().casefold()

            if normalized_id in seen_action_ids:
                errors.append(
                    f"Action {index}: duplicate action_id '{action_id}'"
                )
            else:
                seen_action_ids.add(normalized_id)

        if not _is_non_empty_string(resource):
            errors.append(
                f"Action {index}: resource must be a non-empty string"
            )
            continue

        if resource not in RESOURCE_OPERATIONS:
            errors.append(
                f"Action {index}: unsupported resource '{resource}'"
            )
            continue

        if not _is_non_empty_string(operation):
            errors.append(
                f"Action {index}: operation must be a non-empty string"
            )
            continue

        if operation not in RESOURCE_OPERATIONS[resource]:
            errors.append(
                f"Action {index}: operation '{operation}' "
                f"is not supported for resource '{resource}'"
            )
            continue

        _validate_parameters(
            resource,
            operation,
            parameters,
            errors,
            index,
        )

    return {
        "valid": not errors,
        "errors": errors,
    }
