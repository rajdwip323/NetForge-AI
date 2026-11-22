"""
NETFORGE-AI
Phase 7.10.1 - Deployment Foundation & Data Contracts

Purpose:
    Define vendor-independent deployment data models.

Safety:
    - Mock execution only.
    - No real device execution.
    - Deployment authorization is separate from diagnostic approval.
"""

from copy import deepcopy
from datetime import datetime, timezone


# ============================================================
# CONSTANTS
# ============================================================

DEPLOYMENT_SCHEMA_VERSION = "1.0"

EXECUTION_MODE_MOCK = "mock"

DEPLOYMENT_STATUSES = (
    "pending",
    "running",
    "completed",
    "partially_failed",
    "failed",
    "cancelled",
)

AUTHORIZATION_STATUSES = (
    "pending",
    "approved",
    "rejected",
    "expired",
    "revoked",
)

VERIFICATION_STATUSES = (
    "pending",
    "verified",
    "failed",
    "mismatch",
    "unavailable",
)


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _require_non_empty_string(value, field_name):
    """Validate a required non-empty string."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "{} must be a non-empty string".format(field_name)
        )


def _current_timestamp():
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


def _parse_aware_timestamp(value, field_name):
    """Parse and validate a timezone-aware ISO 8601 timestamp."""

    _require_non_empty_string(value, field_name)

    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(
            "{} must be a valid ISO 8601 timestamp".format(
                field_name
            )
        )

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(
            "{} must include timezone information".format(
                field_name
            )
        )

    return parsed


# ============================================================
# DEPLOYMENT PLAN
# ============================================================

def build_deployment_plan(
    plan_id,
    target,
    actions,
    created_by,
    created_at=None,
):
    """
    Build a vendor-independent deployment plan.

    Vendor-specific commands must not be stored here.
    Action-level validation belongs to deployment_validator.py.
    """

    _require_non_empty_string(plan_id, "plan_id")
    _require_non_empty_string(target, "target")
    _require_non_empty_string(created_by, "created_by")

    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")

    for action in actions:
        if not isinstance(action, dict):
            raise ValueError(
                "each action must be a dictionary"
            )

    if created_at is None:
        created_at = _current_timestamp()

    _require_non_empty_string(created_at, "created_at")

    return {
        "schema_version": DEPLOYMENT_SCHEMA_VERSION,
        "plan_id": plan_id,
        "target": target,
        "actions": deepcopy(actions),
        "execution_mode": EXECUTION_MODE_MOCK,
        "created_by": created_by,
        "created_at": created_at,
    }


# ============================================================
# DEPLOYMENT AUTHORIZATION
# ============================================================

def build_deployment_authorization(
    authorization_id,
    plan_id,
    target,
    plan_fingerprint,
    requested_by,
    approved_by,
    status,
    issued_at,
    expires_at,
):
    """
    Build a deployment-specific authorization record.

    Security:
        - Requester and approver must be different.
        - Timestamps must be timezone-aware ISO 8601.
        - Expiry must be later than issue time.

    This is NOT the Phase 7.9 diagnostic approval object.
    """

    _require_non_empty_string(
        authorization_id, "authorization_id"
    )
    _require_non_empty_string(plan_id, "plan_id")
    _require_non_empty_string(target, "target")
    _require_non_empty_string(
        plan_fingerprint, "plan_fingerprint"
    )
    _require_non_empty_string(requested_by, "requested_by")
    _require_non_empty_string(approved_by, "approved_by")

    if status not in AUTHORIZATION_STATUSES:
        raise ValueError("invalid authorization status")

    if requested_by.strip().casefold() == approved_by.strip().casefold():
        raise ValueError(
            "requester and approver must be different"
        )

    issued_time = _parse_aware_timestamp(
        issued_at, "issued_at"
    )
    expires_time = _parse_aware_timestamp(
        expires_at, "expires_at"
    )

    if expires_time <= issued_time:
        raise ValueError(
            "expires_at must be later than issued_at"
        )

    return {
        "schema_version": DEPLOYMENT_SCHEMA_VERSION,
        "authorization_id": authorization_id,
        "plan_id": plan_id,
        "target": target,
        "plan_fingerprint": plan_fingerprint,
        "requested_by": requested_by,
        "approved_by": approved_by,
        "status": status,
        "issued_at": issued_at,
        "expires_at": expires_at,
    }


# ============================================================
# DEPLOYMENT RESULT
# ============================================================

def build_deployment_result(
    deployment_id,
    target,
    status="pending",
    actions_applied=0,
    actions_failed=0,
    verification_status="pending",
    error=None,
):
    """
    Build a standardized deployment execution result.

    Consistency:
        - completed cannot contain failed actions.
        - partially_failed requires applied and failed actions.
        - success is determined by deployment status.
        - execution is separate from verification.

    Safety:
        - Mock execution only.
        - No real device execution.
    """

    # --------------------------------------------------------
    # BASIC INPUT VALIDATION
    # --------------------------------------------------------

    _require_non_empty_string(
        deployment_id, "deployment_id"
    )
    _require_non_empty_string(target, "target")

    if status not in DEPLOYMENT_STATUSES:
        raise ValueError("invalid deployment status")

    if verification_status not in VERIFICATION_STATUSES:
        raise ValueError("invalid verification status")

    # --------------------------------------------------------
    # ACTION COUNT VALIDATION
    # --------------------------------------------------------

    if (
        not isinstance(actions_applied, int)
        or isinstance(actions_applied, bool)
        or actions_applied < 0
    ):
        raise ValueError(
            "actions_applied must be a non-negative integer"
        )

    if (
        not isinstance(actions_failed, int)
        or isinstance(actions_failed, bool)
        or actions_failed < 0
    ):
        raise ValueError(
            "actions_failed must be a non-negative integer"
        )

    # --------------------------------------------------------
    # DEPLOYMENT STATUS CONSISTENCY
    # --------------------------------------------------------

    if status == "completed" and actions_failed > 0:
        raise ValueError(
            "completed deployment cannot contain failed actions"
        )

    if status == "partially_failed":
        if actions_applied == 0 or actions_failed == 0:
            raise ValueError(
                "partially_failed deployment requires "
                "both applied and failed actions"
            )

    # --------------------------------------------------------
    # ERROR VALIDATION
    # --------------------------------------------------------

    if error is not None and not isinstance(error, str):
        raise ValueError("error must be a string or None")

    # --------------------------------------------------------
    # EXECUTION AND SUCCESS DETERMINATION
    # --------------------------------------------------------

    executed = status in (
        "completed",
        "partially_failed",
        "failed",
    )

    success = status == "completed"

    # --------------------------------------------------------
    # STANDARDIZED DEPLOYMENT RESULT
    # --------------------------------------------------------

    return {
        "schema_version": DEPLOYMENT_SCHEMA_VERSION,
        "deployment_id": deployment_id,
        "target": target,
        "status": status,
        "success": success,
        "executed": executed,
        "execution_mode": EXECUTION_MODE_MOCK,
        "actions_applied": actions_applied,
        "actions_failed": actions_failed,
        "verification_status": verification_status,
        "error": error,
        "created_at": _current_timestamp(),
    }
