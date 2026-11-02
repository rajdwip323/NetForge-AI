
import sys

sys.path.insert(0, "src")

from troubleshooting.approval_manager import (
    create_approval_request,
    validate_approval_request,
    approve_request,
    reject_request,
)


target = "R1:Gi0/1"

proposed_action = {
    "fault_type": "interface_down",
    "type": "diagnostic",
    "action": (
        "Inspect interface operational status "
        "and administrative state."
    ),
    "confidence": "low",
}


def build_preview(**overrides):
    preview = {
        "success": True,
        "status": "preview_ready",
        "target": target,
        "preview": {
            "type": "read_only_diagnostic",
            "summary": "Diagnostic preview prepared.",
        },
        "proposed_actions": [proposed_action.copy()],
        "executed": False,
        "timestamp": "2026-10-28T10:00:00+00:00",
    }

    preview.update(overrides)
    return preview


def create_request(
    preview=None,
    request_target=target,
    requested_by="engineer_1",
):
    return create_approval_request(
        request_target,
        build_preview() if preview is None else preview,
        requested_by,
    )


def create_valid_request():
    return create_request()


cases = [
    (
        "valid preview creates approval request",
        lambda: create_request()["success"] is True,
    ),
    (
        "new approval request starts as pending",
        lambda: create_request()["status"] == "pending",
    ),
    (
        "approval request preserves target",
        lambda: create_request()["target"] == target,
    ),
    (
        "requester identity is preserved",
        lambda: (
            create_request()["requested_by"] == "engineer_1"
        ),
    ),
    (
        "decision fields start empty",
        lambda: (
            create_request()["approved_by"] is None
            and create_request()["rejected_by"] is None
            and create_request()["decided_at"] is None
        ),
    ),
    (
        "proposed actions are preserved",
        lambda: (
            create_request()["proposed_actions"]
            == [proposed_action]
        ),
    ),
    (
        "action snapshot is created",
        lambda: (
            create_request()["proposed_actions_snapshot"]
            == [proposed_action]
        ),
    ),
    (
        "action fingerprint is generated",
        lambda: (
            isinstance(
                create_request()["action_fingerprint"],
                str,
            )
            and bool(create_request()["action_fingerprint"])
        ),
    ),
    (
        "creation event is recorded in audit trail",
        lambda: (
            len(create_request()["audit_trail"]) >= 1
        ),
    ),
    (
        "executed preview is rejected",
        lambda: (
            create_request(
                preview=build_preview(executed=True)
            )["success"] is False
        ),
    ),
    (
        "failed preview is rejected",
        lambda: (
            create_request(
                preview=build_preview(success=False)
            )["success"] is False
        ),
    ),
    (
        "wrong preview status is rejected",
        lambda: (
            create_request(
                preview=build_preview(status="error")
            )["success"] is False
        ),
    ),
    (
        "valid approval request passes validation",
        lambda: (
            validate_approval_request(
                create_valid_request()
            )["success"] is True
        ),
    ),
    (
        "pending request can be approved",
        lambda: (
            approve_request(
                create_valid_request(),
                "engineer_2",
            )["status"] == "approved"
        ),
    ),
    (
        "approval records approver identity",
        lambda: (
            (
                lambda request: (
                    approve_request(request, "engineer_2")
                    ["success"] is True
                    and request["approved_by"] == "engineer_2"
                )
            )(create_valid_request())
        ),
    ),
    (
        "approval decision is recorded in audit trail",
        lambda: (
            (
                lambda request: (
                    approve_request(request, "engineer_2")
                    ["success"] is True
                    and request["audit_trail"][-1]["action"]
                    == "approved"
                )
            )(create_valid_request())
        ),
    ),
    (
        "approval never executes device actions",
        lambda: (
            approve_request(
                create_valid_request(),
                "engineer_2",
            )["executed"] is False
        ),
    ),
    (
        "approved request cannot be approved again",
        lambda: (
            (
                lambda request: (
                    approve_request(request, "engineer_2")
                    ["success"] is True
                    and approve_request(
                        request, "engineer_3"
                    )["success"] is False
                )
            )(create_valid_request())
        ),
    ),
    (
        "pending request can be rejected",
        lambda: (
            reject_request(
                create_valid_request(),
                "engineer_2",
                "Insufficient maintenance evidence.",
            )["status"] == "rejected"
        ),
    ),
    (
        "rejection records actor and reason",
        lambda: (
            (
                lambda request: (
                    reject_request(
                        request,
                        "engineer_2",
                        "Insufficient maintenance evidence.",
                    )["success"] is True
                    and request["rejected_by"] == "engineer_2"
                    and request["rejection_reason"]
                    == "Insufficient maintenance evidence."
                )
            )(create_valid_request())
        ),
    ),
    (
        "rejection decision is recorded in audit trail",
        lambda: (
            (
                lambda request: (
                    reject_request(
                        request,
                        "engineer_2",
                        "Insufficient maintenance evidence.",
                    )["success"] is True
                    and request["audit_trail"][-1]["action"]
                    == "rejected"
                )
            )(create_valid_request())
        ),
    ),
    (
        "rejection never executes device actions",
        lambda: (
            reject_request(
                create_valid_request(),
                "engineer_2",
                "Maintenance not approved.",
            )["executed"] is False
        ),
    ),
    (
        "rejected request cannot be approved",
        lambda: (
            (
                lambda request: (
                    reject_request(
                        request,
                        "engineer_2",
                        "Not approved.",
                    )["success"] is True
                    and approve_request(
                        request, "engineer_3"
                    )["success"] is False
                )
            )(create_valid_request())
        ),
    ),
    (
        "approved request cannot be rejected",
        lambda: (
            (
                lambda request: (
                    approve_request(request, "engineer_2")
                    ["success"] is True
                    and reject_request(
                        request,
                        "engineer_3",
                        "Late rejection.",
                    )["success"] is False
                )
            )(create_valid_request())
        ),
    ),
    (
        "modified proposed actions invalidate request",
        lambda: (
            (
                lambda request: (
                    request["proposed_actions"][0].update(
                        {"action": "Change the proposed action."}
                    )
                    or validate_approval_request(
                        request
                    )["success"] is False
                )
            )(create_valid_request())
        ),
    ),
    (
        "modified target invalidates fingerprint",
        lambda: (
            (
                lambda request: (
                    request.update({"target": "R2:Gi0/0"})
                    or validate_approval_request(
                        request
                    )["success"] is False
                )
            )(create_valid_request())
        ),
    ),
]


passed = 0

for name, check in cases:
    try:
        ok = check()
    except Exception as exc:
        ok = False
        print(f"{name}: ERROR - {exc}")

    print(f"{name}: {'PASS' if ok else 'FAIL'}")

    if ok:
        passed += 1

print(f"\n{passed}/{len(cases)} functional tests passed")

if passed != len(cases):
    sys.exit(1)
