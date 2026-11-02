
import sys

sys.path.insert(0, "src")

from copy import deepcopy

from troubleshooting.approval_manager import (
    create_approval_request,
    validate_approval_request,
    approve_request,
    reject_request,
)


target = "R1:Gi0/1"

action = {
    "fault_type": "interface_down",
    "type": "diagnostic",
    "action": "Inspect interface operational status.",
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
        "proposed_actions": [deepcopy(action)],
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


def invalid_request(**changes):
    request = create_request()
    request.update(changes)
    return request


def rejected_request():
    request = create_request()
    reject_request(request, "engineer_2", "Maintenance rejected.")
    return request


def approved_request():
    request = create_request()
    approve_request(request, "engineer_2")
    return request


def cases_for_invalid_creation():
    return [
        (
            "empty target rejected",
            lambda: (
                create_request(request_target=" ")["success"] is False
            ),
        ),
        (
            "non-string target rejected",
            lambda: (
                create_request(request_target=["R1"])["success"] is False
            ),
        ),
        (
            "empty requester rejected",
            lambda: (
                create_request(requested_by=" ")["success"] is False
            ),
        ),
        (
            "non-string requester rejected",
            lambda: (
                create_request(requested_by=123)["success"] is False
            ),
        ),
        (
            "non-dictionary preview rejected",
            lambda: (
                create_request(preview=[])["success"] is False
            ),
        ),
        (
            "preview target mismatch rejected",
            lambda: (
                create_request(
                    preview=build_preview(target="R2:Gi0/0")
                )["success"] is False
            ),
        ),
        (
            "missing preview metadata rejected",
            lambda: (
                create_request(
                    preview=build_preview(preview=None)
                )["success"] is False
            ),
        ),
        (
            "unsupported preview type rejected",
            lambda: (
                create_request(
                    preview=build_preview(
                        preview={"type": "configuration_change"}
                    )
                )["success"] is False
            ),
        ),
        (
            "missing proposed actions rejected",
            lambda: (
                create_request(
                    preview=build_preview(proposed_actions=None)
                )["success"] is False
            ),
        ),
        (
            "empty proposed actions rejected",
            lambda: (
                create_request(
                    preview=build_preview(proposed_actions=[])
                )["success"] is False
            ),
        ),
        (
            "malformed proposed action rejected",
            lambda: (
                create_request(
                    preview=build_preview(
                        proposed_actions=["invalid"]
                    )
                )["success"] is False
            ),
        ),
        (
            "missing action fault type rejected",
            lambda: (
                create_request(
                    preview=build_preview(
                        proposed_actions=[
                            {
                                "type": "diagnostic",
                                "action": "Inspect interface.",
                                "confidence": "low",
                            }
                        ]
                    )
                )["success"] is False
            ),
        ),
        (
            "unsupported action type rejected",
            lambda: (
                create_request(
                    preview=build_preview(
                        proposed_actions=[
                            {
                                **action,
                                "type": "configuration_change",
                            }
                        ]
                    )
                )["success"] is False
            ),
        ),
        (
            "unsupported action confidence rejected",
            lambda: (
                create_request(
                    preview=build_preview(
                        proposed_actions=[
                            {**action, "confidence": "high"}
                        ]
                    )
                )["success"] is False
            ),
        ),
        (
            "empty preview timestamp rejected",
            lambda: (
                create_request(
                    preview=build_preview(timestamp=" ")
                )["success"] is False
            ),
        ),
    ]


cases = cases_for_invalid_creation() + [
    (
        "non-dictionary approval request rejected",
        lambda: (
            validate_approval_request([])["success"] is False
        ),
    ),
    (
        "missing request ID rejected",
        lambda: (
            validate_approval_request(
                invalid_request(request_id=None)
            )["success"] is False
        ),
    ),
    (
        "invalid approval status rejected",
        lambda: (
            validate_approval_request(
                invalid_request(status="unknown")
            )["success"] is False
        ),
    ),
    (
        "malformed status rejected",
        lambda: (
            validate_approval_request(
                invalid_request(status=["pending"])
            )["success"] is False
        ),
    ),
    (
        "missing action snapshot rejected",
        lambda: (
            validate_approval_request(
                invalid_request(proposed_actions_snapshot=None)
            )["success"] is False
        ),
    ),
    (
        "modified action snapshot rejected",
        lambda: (
            (
                lambda request: (
                    request["proposed_actions_snapshot"][0].update(
                        {"action": "Tampered snapshot."}
                    )
                    or validate_approval_request(
                        request
                    )["success"] is False
                )
            )(create_request())
        ),
    ),
    (
        "modified fingerprint rejected",
        lambda: (
            validate_approval_request(
                invalid_request(
                    action_fingerprint="invalid-fingerprint"
                )
            )["success"] is False
        ),
    ),
    (
        "missing audit trail rejected",
        lambda: (
            validate_approval_request(
                invalid_request(audit_trail=None)
            )["success"] is False
        ),
    ),
    (
        "empty audit trail rejected",
        lambda: (
            validate_approval_request(
                invalid_request(audit_trail=[])
            )["success"] is False
        ),
    ),
    (
        "invalid audit trail type rejected",
        lambda: (
            validate_approval_request(
                invalid_request(audit_trail="invalid")
            )["success"] is False
        ),
    ),
    (
        "empty approver rejected",
        lambda: (
            approve_request(create_request(), " ")["success"] is False
        ),
    ),
    (
        "non-string approver rejected",
        lambda: (
            approve_request(create_request(), 123)["success"] is False
        ),
    ),
    (
        "empty rejector rejected",
        lambda: (
            reject_request(
                create_request(),
                " ",
                "Not approved.",
            )["success"] is False
        ),
    ),
    (
        "empty rejection reason rejected",
        lambda: (
            reject_request(
                create_request(),
                "engineer_2",
                " ",
            )["success"] is False
        ),
    ),
    (
        "non-string rejection reason rejected",
        lambda: (
            reject_request(
                create_request(),
                "engineer_2",
                123,
            )["success"] is False
        ),
    ),
    (
        "rejected request remains rejected",
        lambda: rejected_request()["status"] == "rejected",
    ),
    (
        "approved request remains approved",
        lambda: approved_request()["status"] == "approved",
    ),
    (
        "decision does not change proposed actions",
        lambda: (
            (
                lambda request: (
                    approve_request(request, "engineer_2")
                    ["success"] is True
                    and request["proposed_actions"]
                    == request["proposed_actions_snapshot"]
                )
            )(create_request())
        ),
    ),
    (
        "decision does not execute device actions",
        lambda: (
            (
                lambda request: (
                    approve_request(request, "engineer_2")
                    ["executed"] is False
                )
            )(create_request())
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

print(f"\n{passed}/{len(cases)} edge tests passed")

if passed != len(cases):
    sys.exit(1)
