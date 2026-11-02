
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from uuid import uuid4


VALID_STATUSES = {
    "pending",
    "approved",
    "rejected",
}


def _valid_text(value):
    return isinstance(value, str) and bool(value.strip())


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _error_result(message):
    return {
        "success": False,
        "status": "error",
        "error": message,
    }


def _action_fingerprint(target, proposed_actions, preview_timestamp):
    """Create a stable fingerprint for approved preview actions."""

    payload = {
        "target": target,
        "proposed_actions": proposed_actions,
        "preview_timestamp": preview_timestamp,
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def _validate_proposed_actions(actions):
    if not isinstance(actions, list) or not actions:
        return "Proposed actions must be a non-empty list."

    for item in actions:
        if not isinstance(item, dict):
            return "Proposed action contains an invalid item."

        if not _valid_text(item.get("fault_type")):
            return "Proposed action fault_type must be non-empty."

        if item.get("type") != "diagnostic":
            return "Only diagnostic actions are allowed."

        if not _valid_text(item.get("action")):
            return "Proposed action must contain a non-empty action."

        if item.get("confidence") != "low":
            return "Unsupported proposed action confidence."

    return None


def _validate_audit_event(event, expected_action,
                          expected_actor, expected_timestamp,
                          previous_status, new_status):
    """Validate one audit event against the request lifecycle."""

    if not isinstance(event, dict):
        return "Audit event must be a dictionary."

    if event.get("action") != expected_action:
        return "Unexpected audit event action."

    if not _valid_text(event.get("performed_by")):
        return "Audit event actor must be non-empty."

    if event.get("performed_by") != expected_actor:
        return "Audit event actor does not match request decision."

    if not _valid_text(event.get("timestamp")):
        return "Audit event timestamp must be non-empty."

    if event.get("timestamp") != expected_timestamp:
        return "Audit event timestamp does not match request."

    if event.get("previous_status") != previous_status:
        return "Audit event previous status mismatch."

    if event.get("new_status") != new_status:
        return "Audit event new status mismatch."

    return None


def _validate_audit_trail(request):
    """Validate audit records against the current request status."""

    audit_trail = request.get("audit_trail")

    if not isinstance(audit_trail, list):
        return "Invalid approval audit trail."

    status = request["status"]

    expected_length = 1 if status == "pending" else 2

    if len(audit_trail) != expected_length:
        return "Audit trail does not match approval lifecycle."

    created_event = audit_trail[0]

    error = _validate_audit_event(
        created_event,
        "created",
        request["requested_by"],
        request["requested_at"],
        None,
        "pending",
    )

    if error:
        return error

    if status == "pending":
        if request.get("approved_by") is not None:
            return "Pending request cannot contain an approver."

        if request.get("rejected_by") is not None:
            return "Pending request cannot contain a rejector."

        if request.get("decided_at") is not None:
            return "Pending request cannot contain a decision timestamp."

        if request.get("rejection_reason") is not None:
            return "Pending request cannot contain a rejection reason."

        return None

    decision_event = audit_trail[1]

    if not _valid_text(request.get("decided_at")):
        return "Decision timestamp must be non-empty."

    if status == "approved":
        approved_by = request.get("approved_by")

        if not _valid_text(approved_by):
            return "Approved request requires an approver."

        if request.get("rejected_by") is not None:
            return "Approved request cannot contain a rejector."

        if request.get("rejection_reason") is not None:
            return "Approved request cannot contain a rejection reason."

        return _validate_audit_event(
            decision_event,
            "approved",
            approved_by,
            request["decided_at"],
            "pending",
            "approved",
        )

    if status == "rejected":
        rejected_by = request.get("rejected_by")
        rejection_reason = request.get("rejection_reason")

        if not _valid_text(rejected_by):
            return "Rejected request requires a rejector."

        if not _valid_text(rejection_reason):
            return "Rejected request requires a rejection reason."

        if request.get("approved_by") is not None:
            return "Rejected request cannot contain an approver."

        error = _validate_audit_event(
            decision_event,
            "rejected",
            rejected_by,
            request["decided_at"],
            "pending",
            "rejected",
        )

        if error:
            return error

        if decision_event.get("reason") != rejection_reason:
            return "Rejection reason does not match audit event."

        return None

    return "Unsupported approval status."


def create_approval_request(target, dry_run_result, requested_by):
    """Create an approval request from a valid read-only preview."""

    if not _valid_text(target):
        return _error_result("Target must be a non-empty string.")

    target = target.strip()

    if not _valid_text(requested_by):
        return _error_result("requested_by must be a non-empty string.")

    requested_by = requested_by.strip()

    if not isinstance(dry_run_result, dict):
        return _error_result("dry_run_result must be a dictionary.")

    if dry_run_result.get("success") is not True:
        return _error_result("Diagnostic preview was not successful.")

    if dry_run_result.get("status") != "preview_ready":
        return _error_result("Diagnostic preview is not ready.")

    if dry_run_result.get("executed") is not False:
        return _error_result("Executed previews cannot be approved.")

    if dry_run_result.get("target") != target:
        return _error_result("Approval target mismatch.")

    preview = dry_run_result.get("preview")

    if not isinstance(preview, dict):
        return _error_result("Preview metadata must be a dictionary.")

    if preview.get("type") != "read_only_diagnostic":
        return _error_result("Unsupported preview type.")

    proposed_actions = dry_run_result.get("proposed_actions")
    error = _validate_proposed_actions(proposed_actions)

    if error:
        return _error_result(error)

    preview_timestamp = dry_run_result.get("timestamp")

    if not _valid_text(preview_timestamp):
        return _error_result("Preview timestamp must be non-empty.")

    try:
        actions_snapshot = deepcopy(proposed_actions)

        fingerprint = _action_fingerprint(
            target,
            actions_snapshot,
            preview_timestamp,
        )
    except (TypeError, ValueError):
        return _error_result(
            "Preview actions must contain valid JSON data."
        )

    created_at = _timestamp()

    request = {
        "success": True,
        "request_id": str(uuid4()),
        "target": target,
        "status": "pending",
        "requested_by": requested_by,
        "approved_by": None,
        "rejected_by": None,
        "proposed_actions": actions_snapshot,
        "proposed_actions_snapshot": deepcopy(actions_snapshot),
        "preview_timestamp": preview_timestamp,
        "action_fingerprint": fingerprint,
        "requested_at": created_at,
        "decided_at": None,
        "rejection_reason": None,
        "audit_trail": [
            {
                "action": "created",
                "performed_by": requested_by,
                "timestamp": created_at,
                "previous_status": None,
                "new_status": "pending",
            }
        ],
    }

    return request


def validate_approval_request(approval_request):
    """Validate request structure, integrity and audit consistency."""

    if not isinstance(approval_request, dict):
        return _error_result(
            "approval_request must be a dictionary."
        )

    if approval_request.get("success") is not True:
        return _error_result("Approval request is not successful.")

    required_text_fields = (
        "request_id",
        "target",
        "requested_by",
        "preview_timestamp",
        "requested_at",
        "action_fingerprint",
    )

    for field in required_text_fields:
        if not _valid_text(approval_request.get(field)):
            return _error_result(
                "Approval request has an invalid " + field + "."
            )

    status = approval_request.get("status")

    if not isinstance(status, str) or status not in VALID_STATUSES:
        return _error_result("Unsupported approval status.")

    actions = approval_request.get("proposed_actions")
    snapshot = approval_request.get("proposed_actions_snapshot")

    error = _validate_proposed_actions(actions)

    if error:
        return _error_result(error)

    if not isinstance(snapshot, list):
        return _error_result("Invalid proposed actions snapshot.")

    if actions != snapshot:
        return _error_result("Proposed actions were modified.")

    try:
        expected_fingerprint = _action_fingerprint(
            approval_request["target"],
            snapshot,
            approval_request["preview_timestamp"],
        )
    except (TypeError, ValueError):
        return _error_result(
            "Approval request contains invalid JSON data."
        )

    if expected_fingerprint != approval_request["action_fingerprint"]:
        return _error_result("Approval request fingerprint mismatch.")

    error = _validate_audit_trail(approval_request)

    if error:
        return _error_result(error)

    return {
        "success": True,
        "status": "valid",
        "request_id": approval_request["request_id"],
        "target": approval_request["target"],
    }


def approve_request(approval_request, approved_by):
    """Approve a valid pending request without executing any action."""

    validation = validate_approval_request(approval_request)

    if validation.get("success") is not True:
        return validation

    if not _valid_text(approved_by):
        return _error_result("approved_by must be a non-empty string.")

    if approval_request["status"] != "pending":
        return _error_result("Only pending requests can be approved.")

    approved_by = approved_by.strip()
    decided_at = _timestamp()
    previous_status = approval_request["status"]

    approval_request["status"] = "approved"
    approval_request["approved_by"] = approved_by
    approval_request["decided_at"] = decided_at

    approval_request["audit_trail"].append({
        "action": "approved",
        "performed_by": approved_by,
        "timestamp": decided_at,
        "previous_status": previous_status,
        "new_status": "approved",
    })

    return {
        "success": True,
        "status": "approved",
        "request_id": approval_request["request_id"],
        "target": approval_request["target"],
        "approved_by": approved_by,
        "decided_at": decided_at,
        "executed": False,
    }


def reject_request(approval_request, rejected_by, reason):
    """Reject a valid pending request without executing any action."""

    validation = validate_approval_request(approval_request)

    if validation.get("success") is not True:
        return validation

    if not _valid_text(rejected_by):
        return _error_result("rejected_by must be a non-empty string.")

    if not _valid_text(reason):
        return _error_result("Rejection reason must be non-empty.")

    if approval_request["status"] != "pending":
        return _error_result("Only pending requests can be rejected.")

    rejected_by = rejected_by.strip()
    reason = reason.strip()

    decided_at = _timestamp()
    previous_status = approval_request["status"]

    approval_request["status"] = "rejected"
    approval_request["rejected_by"] = rejected_by
    approval_request["rejection_reason"] = reason
    approval_request["decided_at"] = decided_at

    approval_request["audit_trail"].append({
        "action": "rejected",
        "performed_by": rejected_by,
        "timestamp": decided_at,
        "previous_status": previous_status,
        "new_status": "rejected",
        "reason": reason,
    })

    return {
        "success": True,
        "status": "rejected",
        "request_id": approval_request["request_id"],
        "target": approval_request["target"],
        "rejected_by": rejected_by,
        "reason": reason,
        "decided_at": decided_at,
        "executed": False,
    }
