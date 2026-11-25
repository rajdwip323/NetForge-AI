
"""
NETFORGE-AI
Phase 7.10.3 - Deployment Safety Gate

Responsibilities:
- Validate deployment plan structure and schema.
- Validate deployment actions.
- Enforce mock-only execution.
- Validate deployment authorization.
- Verify authorization identity and actor separation.
- Verify authorization validity period.
- Verify full deployment plan SHA-256 fingerprint.

Safety:
- No vendor command generation.
- No device connection.
- No configuration application.
- No authorization approval.
- No deployment execution.

The safety gate is independent from the deployment executor.
"""

import hashlib
import json
import math
import re

from datetime import datetime, timezone

from .deployment_models import (
    DEPLOYMENT_SCHEMA_VERSION,
    EXECUTION_MODE_MOCK,
    AUTHORIZATION_STATUSES,
)

from .deployment_validator import validate_deployment_plan


# ============================================================
# REQUIRED SCHEMA FIELDS
# ============================================================

PLAN_REQUIRED_FIELDS = {
    "schema_version",
    "plan_id",
    "target",
    "actions",
    "execution_mode",
    "created_by",
    "created_at",
}

AUTHORIZATION_REQUIRED_FIELDS = {
    "schema_version",
    "authorization_id",
    "plan_id",
    "target",
    "plan_fingerprint",
    "requested_by",
    "approved_by",
    "status",
    "issued_at",
    "expires_at",
}

FINGERPRINT_PATTERN = re.compile(r"^[a-f0-9]{64}$")


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _is_non_empty_string(value):
    """Check whether a value is a non-empty string."""

    return isinstance(value, str) and bool(value.strip())


def _parse_aware_timestamp(value):
    """
    Parse an ISO-8601 timestamp.

    Naive timestamps are rejected.
    Timezone-aware timestamps are required.
    """

    if not isinstance(value, str):
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            return None

        if parsed.utcoffset() is None:
            return None

        return parsed

    except (ValueError, TypeError, OverflowError):
        return None


def _is_json_value(value, visited=None):
    """
    Check whether a value contains only safe JSON-compatible data.

    Reject:
    - Unsupported Python objects
    - NaN and infinity
    - Non-string dictionary keys
    - Circular references
    """

    if visited is None:
        visited = set()

    if value is None:
        return True

    if isinstance(value, (str, bool, int)):
        return True

    if isinstance(value, float):
        return math.isfinite(value)

    if isinstance(value, (list, dict)):
        object_id = id(value)

        if object_id in visited:
            return False

        visited.add(object_id)

        try:
            if isinstance(value, list):
                return all(
                    _is_json_value(item, visited)
                    for item in value
                )

            return all(
                isinstance(key, str)
                and _is_json_value(item, visited)
                for key, item in value.items()
            )

        finally:
            visited.remove(object_id)

    return False


def _has_exact_fields(data, required_fields):
    """
    Ensure that a dictionary contains exactly the expected fields.
    """

    if not isinstance(data, dict):
        return False

    return set(data.keys()) == required_fields


# ============================================================
# DEPLOYMENT PLAN SCHEMA VALIDATION
# ============================================================

def _validate_plan_schema(plan):
    """
    Validate deployment plan structure and schema.

    Action-level validation is performed separately
    by deployment_validator.py.
    """

    errors = []

    if not isinstance(plan, dict):
        return False, [
            "Deployment plan must be a dictionary."
        ]

    if not _has_exact_fields(
        plan,
        PLAN_REQUIRED_FIELDS
    ):
        errors.append(
            "Deployment plan contains missing or unsupported top-level fields."
        )

    if plan.get("schema_version") != DEPLOYMENT_SCHEMA_VERSION:
        errors.append(
            "Unsupported deployment schema version."
        )

    if not _is_non_empty_string(plan.get("plan_id")):
        errors.append("Invalid plan_id.")

    if not _is_non_empty_string(plan.get("target")):
        errors.append("Invalid deployment target.")

    actions = plan.get("actions")

    if not isinstance(actions, list) or not actions:
        errors.append(
            "Deployment actions must be a non-empty list."
        )

    if plan.get("execution_mode") != EXECUTION_MODE_MOCK:
        errors.append(
            "Deployment plan must use mock execution mode."
        )

    if not _is_non_empty_string(plan.get("created_by")):
        errors.append("Invalid plan creator.")

    created_at = _parse_aware_timestamp(
        plan.get("created_at")
    )

    if created_at is None:
        errors.append(
            "created_at must be a valid timezone-aware ISO-8601 timestamp."
        )

    if not _is_json_value(plan):
        errors.append(
            "Deployment plan contains unsupported or unsafe JSON values."
        )

    return not errors, errors


# ============================================================
# DEPLOYMENT AUTHORIZATION SCHEMA VALIDATION
# ============================================================

def _validate_authorization_schema(authorization):
    """
    Validate deployment authorization structure and fields.
    """

    errors = []

    if not isinstance(authorization, dict):
        return False, [
            "Authorization must be a dictionary."
        ]

    if not _has_exact_fields(
        authorization,
        AUTHORIZATION_REQUIRED_FIELDS
    ):
        errors.append(
            "Authorization contains missing or unsupported top-level fields."
        )

    if authorization.get("schema_version") != DEPLOYMENT_SCHEMA_VERSION:
        errors.append(
            "Unsupported authorization schema version."
        )

    if not _is_non_empty_string(
        authorization.get("authorization_id")
    ):
        errors.append("Invalid authorization_id.")

    if not _is_non_empty_string(
        authorization.get("plan_id")
    ):
        errors.append("Invalid authorization plan_id.")

    if not _is_non_empty_string(
        authorization.get("target")
    ):
        errors.append("Invalid authorization target.")

    fingerprint = authorization.get("plan_fingerprint")

    if (
        not isinstance(fingerprint, str)
        or FINGERPRINT_PATTERN.fullmatch(fingerprint) is None
    ):
        errors.append(
            "Invalid authorization plan fingerprint."
        )

    if not _is_non_empty_string(
        authorization.get("requested_by")
    ):
        errors.append("Invalid authorization requester.")

    if not _is_non_empty_string(
        authorization.get("approved_by")
    ):
        errors.append("Invalid authorization approver.")

    if authorization.get("status") not in AUTHORIZATION_STATUSES:
        errors.append("Invalid authorization status.")

    issued_at = _parse_aware_timestamp(
        authorization.get("issued_at")
    )

    expires_at = _parse_aware_timestamp(
        authorization.get("expires_at")
    )

    if issued_at is None:
        errors.append(
            "issued_at must be a valid timezone-aware ISO-8601 timestamp."
        )

    if expires_at is None:
        errors.append(
            "expires_at must be a valid timezone-aware ISO-8601 timestamp."
        )

    if issued_at is not None and expires_at is not None:
        if expires_at <= issued_at:
            errors.append(
                "Authorization expiry must be later than issue time."
            )

    if not _is_json_value(authorization):
        errors.append(
            "Authorization contains unsupported or unsafe JSON values."
        )

    return not errors, errors


# ============================================================
# CURRENT TIME VALIDATION
# ============================================================

def _resolve_current_time(current_time):
    """
    Resolve current time for authorization validation.

    An injectable timezone-aware datetime makes tests deterministic.
    """

    if current_time is None:
        return datetime.now(timezone.utc)

    if not isinstance(current_time, datetime):
        return None

    try:
        if current_time.tzinfo is None:
            return None

        if current_time.utcoffset() is None:
            return None

        return current_time

    except (TypeError, ValueError, OverflowError):
        return None


# ============================================================
# PLAN FINGERPRINT
# ============================================================

def calculate_plan_fingerprint(plan):
    """
    Generate a deterministic SHA-256 fingerprint for the full plan.

    Every plan field participates in the fingerprint.

    Dictionary key order does not affect the fingerprint.
    Changing any plan value changes the fingerprint.
    """

    if not isinstance(plan, dict):
        raise ValueError(
            "Plan must be a dictionary."
        )

    if not _is_json_value(plan):
        raise ValueError(
            "Plan contains unsupported or unsafe JSON values."
        )

    try:
        canonical_plan = json.dumps(
            plan,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

        return hashlib.sha256(
            canonical_plan.encode("utf-8")
        ).hexdigest()

    except (
        TypeError,
        ValueError,
        RecursionError,
    ) as exc:
        raise ValueError(
            "Unable to calculate deployment plan fingerprint."
        ) from exc


# ============================================================
# DEPLOYMENT SAFETY EVALUATION
# ============================================================

def evaluate_deployment_safety(
    plan,
    authorization,
    current_time=None,
):
    """
    Evaluate every independent deployment safety check.

    Any failed check blocks deployment.

    This function does not execute deployment actions.
    """

    checks = {
        "plan_structure": False,
        "plan_schema": False,
        "action_validation": False,
        "execution_mode_mock": False,
        "authorization_present": False,
        "authorization_schema": False,
        "authorization_approved": False,
        "plan_id_match": False,
        "target_match": False,
        "actor_separation": False,
        "authorization_time_valid": False,
        "fingerprint_match": False,
    }

    errors = []
    actual_fingerprint = None

    # --------------------------------------------------
    # 1. Plan structure
    # --------------------------------------------------

    checks["plan_structure"] = isinstance(
        plan,
        dict
    )

    if not checks["plan_structure"]:
        errors.append(
            "Deployment plan must be a dictionary."
        )

    # --------------------------------------------------
    # 2. Plan schema
    # --------------------------------------------------

    try:
        plan_schema_valid, plan_schema_errors = (
            _validate_plan_schema(plan)
        )

        checks["plan_schema"] = plan_schema_valid
        errors.extend(plan_schema_errors)

    except Exception as exc:
        checks["plan_schema"] = False

        errors.append(
            "Unexpected error during plan schema validation: {}".format(
                type(exc).__name__
            )
        )

    # --------------------------------------------------
    # 3. Action validation
    # --------------------------------------------------

    if isinstance(plan, dict):
        try:
            action_result = validate_deployment_plan(
                plan
            )

            if isinstance(action_result, dict):
                checks["action_validation"] = (
                    action_result.get("valid") is True
                )

                action_errors = action_result.get(
                    "errors",
                    []
                )

                if isinstance(action_errors, list):
                    errors.extend(
                        str(error)
                        for error in action_errors
                    )

            else:
                errors.append(
                    "Deployment validator returned an invalid result."
                )

        except Exception as exc:
            checks["action_validation"] = False

            errors.append(
                "Unexpected error during deployment action validation: {}".format(
                    type(exc).__name__
                )
            )

    else:
        errors.append(
            "Action validation skipped because plan is not a dictionary."
        )

    # --------------------------------------------------
    # 4. Mock-only execution
    # --------------------------------------------------

    if isinstance(plan, dict):
        checks["execution_mode_mock"] = (
            plan.get("execution_mode") == EXECUTION_MODE_MOCK
        )

    if not checks["execution_mode_mock"]:
        errors.append(
            "Only mock execution mode is permitted by this safety gate."
        )

    # --------------------------------------------------
    # 5. Authorization presence
    # --------------------------------------------------

    checks["authorization_present"] = isinstance(
        authorization,
        dict
    )

    if not checks["authorization_present"]:
        errors.append(
            "Valid deployment authorization is required."
        )

    # --------------------------------------------------
    # 6. Authorization schema
    # --------------------------------------------------

    if checks["authorization_present"]:
        try:
            authorization_schema_valid, authorization_errors = (
                _validate_authorization_schema(
                    authorization
                )
            )

            checks["authorization_schema"] = (
                authorization_schema_valid
            )

            errors.extend(authorization_errors)

        except Exception as exc:
            checks["authorization_schema"] = False

            errors.append(
                "Unexpected error during authorization validation: {}".format(
                    type(exc).__name__
                )
            )

    # --------------------------------------------------
    # 7. Authorization approved
    # --------------------------------------------------

    if checks["authorization_present"]:
        checks["authorization_approved"] = (
            authorization.get("status") == "approved"
        )

    if not checks["authorization_approved"]:
        errors.append(
            "Deployment authorization must have approved status."
        )

    # --------------------------------------------------
    # 8. Plan ID match
    # --------------------------------------------------

    if (
        isinstance(plan, dict)
        and checks["authorization_present"]
    ):
        checks["plan_id_match"] = (
            plan.get("plan_id")
            == authorization.get("plan_id")
        )

    if not checks["plan_id_match"]:
        errors.append(
            "Authorization plan_id does not match deployment plan."
        )

    # --------------------------------------------------
    # 9. Target match
    # --------------------------------------------------

    if (
        isinstance(plan, dict)
        and checks["authorization_present"]
    ):
        checks["target_match"] = (
            plan.get("target")
            == authorization.get("target")
        )

    if not checks["target_match"]:
        errors.append(
            "Authorization target does not match deployment target."
        )

    # --------------------------------------------------
    # 10. Requester and approver separation
    # --------------------------------------------------

    if checks["authorization_present"]:
        requester = authorization.get("requested_by")
        approver = authorization.get("approved_by")

        checks["actor_separation"] = (
            _is_non_empty_string(requester)
            and _is_non_empty_string(approver)
            and requester.strip().casefold()
            != approver.strip().casefold()
        )

    if not checks["actor_separation"]:
        errors.append(
            "Requester and approver must be different people."
        )

    # --------------------------------------------------
    # 11. Authorization time validity
    # --------------------------------------------------

    now = _resolve_current_time(
        current_time
    )

    if (
        now is not None
        and checks["authorization_present"]
    ):
        issued_at = _parse_aware_timestamp(
            authorization.get("issued_at")
        )

        expires_at = _parse_aware_timestamp(
            authorization.get("expires_at")
        )

        if (
            issued_at is not None
            and expires_at is not None
        ):
            try:
                now_utc = now.astimezone(
                    timezone.utc
                )

                issued_utc = issued_at.astimezone(
                    timezone.utc
                )

                expires_utc = expires_at.astimezone(
                    timezone.utc
                )

                checks["authorization_time_valid"] = (
                    issued_utc <= now_utc < expires_utc
                )

            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                checks["authorization_time_valid"] = False

    if not checks["authorization_time_valid"]:
        errors.append(
            "Authorization is not currently within its validity period."
        )

    # --------------------------------------------------
    # 12. Full plan fingerprint
    # --------------------------------------------------

    if (
        isinstance(plan, dict)
        and checks["authorization_present"]
    ):
        try:
            actual_fingerprint = (
                calculate_plan_fingerprint(plan)
            )

            expected_fingerprint = authorization.get(
                "plan_fingerprint"
            )

            checks["fingerprint_match"] = (
                isinstance(expected_fingerprint, str)
                and actual_fingerprint == expected_fingerprint
            )

        except (
            ValueError,
            TypeError,
            RecursionError,
        ):
            checks["fingerprint_match"] = False

    if not checks["fingerprint_match"]:
        errors.append(
            "Full deployment plan fingerprint validation failed."
        )

    # --------------------------------------------------
    # FINAL FAIL-CLOSED DECISION
    # --------------------------------------------------

    allowed = all(
        checks.values()
    )

    return {
        "allowed": allowed,
        "checks": checks,
        "errors": errors,
        "fingerprint": (
            actual_fingerprint
            if checks["fingerprint_match"]
            else None
        ),
        "execution_mode": (
            plan.get("execution_mode")
            if isinstance(plan, dict)
            else None
        ),
        "executed": False,
    }
