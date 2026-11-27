
"""
NETFORGE-AI
Phase 7.10.4 - Mock Deployment Executor

Responsibilities:
- Execute deployment actions in mock mode only.
- Require successful validation and safety authorization.
- Simulate action outcomes without vendor commands.
- Never connect to or modify real network devices.
- Produce a deployment result using the existing data contract.
"""

from uuid import uuid4

from deployment.deployment_models import (
    EXECUTION_MODE_MOCK,
    build_deployment_result,
)

from deployment.deployment_validator import (
    validate_deployment_plan,
)

from deployment.deployment_safety_gate import (
    evaluate_deployment_safety,
)


def _blocked_response(errors, safety_result=None):
    """
    Return a fail-closed response.

    A blocked request is not a deployment execution.
    Therefore, no deployment result is created.
    """

    return {
        "allowed": False,
        "executed": False,
        "execution_mode": EXECUTION_MODE_MOCK,
        "status": "blocked",
        "action_results": [],
        "deployment_result": None,
        "safety_result": safety_result,
        "errors": list(errors),
    }


def _validate_failure_action_ids(failure_action_ids, actions):
    """
    Validate the optional mock failure-injection input.

    Failure injection is an executor-side simulation control.
    It is never added to or stored inside the deployment plan.
    """

    if failure_action_ids is None:
        failure_action_ids = []

    if not isinstance(failure_action_ids, (list, tuple, set)):
        return False, set(), [
            "failure_action_ids must be a list, tuple, or set."
        ]

    normalized_failure_ids = set()

    for action_id in failure_action_ids:
        if not isinstance(action_id, str) or not action_id.strip():
            return False, set(), [
                "Every failure action ID must be a non-empty string."
            ]

        normalized_id = action_id.casefold()

        if normalized_id in normalized_failure_ids:
            return False, set(), [
                "Duplicate failure action IDs are not allowed."
            ]

        normalized_failure_ids.add(normalized_id)

    known_action_ids = {
        action["action_id"].casefold()
        for action in actions
    }

    unknown_ids = normalized_failure_ids - known_action_ids

    if unknown_ids:
        return False, set(), [
            "Failure injection references unknown action IDs."
        ]

    return True, normalized_failure_ids, []


def execute_mock_deployment(
    plan,
    authorization,
    current_time=None,
    failure_action_ids=None,
    deployment_id=None,
):
    """
    Safely simulate a deployment plan.

    Execution sequence:
        1. Validate deployment plan.
        2. Evaluate mandatory deployment safety gate.
        3. Validate mock failure-injection controls.
        4. Simulate each action.
        5. Build the deployment result.

    No vendor commands are generated.
    No real device connection is attempted.
    No real network configuration is changed.

    Args:
        plan (dict):
            Deployment plan created using the deployment data contract.

        authorization (dict):
            Approved deployment authorization.

        current_time (datetime, optional):
            Explicit timezone-aware time for safety evaluation.

        failure_action_ids (list, tuple, or set, optional):
            Action IDs that should simulate failure.
            This control is external to the deployment plan.

        deployment_id (str, optional):
            Caller-supplied deployment ID.
            A unique mock deployment ID is generated when omitted.

    Returns:
        dict:
            Execution decision, action results, safety result,
            deployment result, and errors.
    """

    # ---------------------------------------------------------
    # 1. Validate optional deployment ID
    # ---------------------------------------------------------

    if deployment_id is None:
        deployment_id = "MOCK-" + uuid4().hex

    if (
        not isinstance(deployment_id, str)
        or not deployment_id.strip()
    ):
        return _blocked_response([
            "deployment_id must be a non-empty string."
        ])

    # ---------------------------------------------------------
    # 2. Validate deployment plan
    # ---------------------------------------------------------

    validation_result = validate_deployment_plan(plan)

    if not validation_result["valid"]:
        return _blocked_response(
            validation_result["errors"]
        )

    # ---------------------------------------------------------
    # 3. Mandatory safety gate
    # ---------------------------------------------------------

    safety_result = evaluate_deployment_safety(
        plan,
        authorization,
        current_time=current_time,
    )

    if not safety_result["allowed"]:
        return _blocked_response(
            safety_result["errors"],
            safety_result=safety_result,
        )

    # ---------------------------------------------------------
    # 4. Validate mock failure-injection controls
    # ---------------------------------------------------------

    injection_valid, failure_ids, injection_errors = (
        _validate_failure_action_ids(
            failure_action_ids,
            plan["actions"],
        )
    )

    if not injection_valid:
        return _blocked_response(
            injection_errors,
            safety_result=safety_result,
        )

    # ---------------------------------------------------------
    # 5. Simulate actions
    # ---------------------------------------------------------

    action_results = []

    actions_applied = 0
    actions_failed = 0

    for action in plan["actions"]:

        action_id = action["action_id"]

        if action_id.casefold() in failure_ids:

            action_result = {
                "action_id": action_id,
                "resource": action["resource"],
                "operation": action["operation"],
                "status": "failed",
                "success": False,
                "error": "Simulated mock failure.",
            }

            actions_failed += 1

        else:

            action_result = {
                "action_id": action_id,
                "resource": action["resource"],
                "operation": action["operation"],
                "status": "success",
                "success": True,
                "error": None,
            }

            actions_applied += 1

        action_results.append(action_result)

    # ---------------------------------------------------------
    # 6. Determine overall deployment status
    # ---------------------------------------------------------

    if actions_failed == 0:
        deployment_status = "completed"

    elif actions_applied > 0:
        deployment_status = "partially_failed"

    else:
        deployment_status = "failed"

    # ---------------------------------------------------------
    # 7. Build existing deployment result contract
    # ---------------------------------------------------------

    deployment_result = build_deployment_result(
        deployment_id=deployment_id,
        target=plan["target"],
        status=deployment_status,
        actions_applied=actions_applied,
        actions_failed=actions_failed,
        verification_status="pending",
        error=(
            "One or more mock actions failed."
            if actions_failed > 0
            else None
        ),
    )

    # ---------------------------------------------------------
    # 8. Return execution summary
    # ---------------------------------------------------------

    return {
        "allowed": True,
        "executed": True,
        "execution_mode": EXECUTION_MODE_MOCK,
        "status": deployment_status,
        "action_results": action_results,
        "deployment_result": deployment_result,
        "safety_result": safety_result,
        "errors": [],
    }
