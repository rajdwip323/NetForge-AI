
import sys
from copy import deepcopy

sys.path.insert(0, "src")

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


def build_preview():
    return {
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


def create_request():
    return create_approval_request(
        target,
        build_preview(),
        "engineer_1",
    )


def approved_request():
    request = create_request()
    approve_request(request, "engineer_2")
    return request


def rejected_request():
    request = create_request()
    reject_request(
        request,
        "engineer_2",
        "Maintenance rejected.",
    )
    return request


def cases_for_security():
    return [
        (
            "valid pending request passes security validation",
            lambda: (
                validate_approval_request(
                    create_request()
                )["success"] is True
            ),
        ),
        (
            "valid approved request passes security validation",
            lambda: (
                validate_approval_request(
                    approved_request()
                )["success"] is True
            ),
        ),
        (
            "valid rejected request passes security validation",
            lambda: (
                validate_approval_request(
                    rejected_request()
                )["success"] is True
            ),
        ),
        (
            "malformed audit event is rejected",
            lambda: (
                (
                    lambda request: (
                        request["audit_trail"].append("invalid")
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(create_request())
            ),
        ),
        (
            "audit event missing actor is rejected",
            lambda: (
                (
                    lambda request: (
                        request["audit_trail"][0].update(
                            {"performed_by": None}
                        )
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(create_request())
            ),
        ),
        (
            "audit event missing timestamp is rejected",
            lambda: (
                (
                    lambda request: (
                        request["audit_trail"][0].update(
                            {"timestamp": ""}
                        )
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(create_request())
            ),
        ),
        (
            "pending request cannot contain approved actor",
            lambda: (
                validate_approval_request(
                    dict(
                        create_request(),
                        approved_by="engineer_2",
                    )
                )["success"] is False
            ),
        ),
        (
            "approved request requires approved actor",
            lambda: (
                (
                    lambda request: (
                        request.update({"approved_by": None})
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(approved_request())
            ),
        ),
        (
            "approved request requires decision timestamp",
            lambda: (
                (
                    lambda request: (
                        request.update({"decided_at": None})
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(approved_request())
            ),
        ),
        (
            "approved request requires approved audit event",
            lambda: (
                (
                    lambda request: (
                        request.update({
                            "audit_trail": request["audit_trail"][:1]
                        })
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(approved_request())
            ),
        ),
        (
            "approved actor must match audit actor",
            lambda: (
                (
                    lambda request: (
                        request.update({
                            "approved_by": "engineer_3"
                        })
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(approved_request())
            ),
        ),
        (
            "rejected request requires rejected actor",
            lambda: (
                (
                    lambda request: (
                        request.update({"rejected_by": None})
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(rejected_request())
            ),
        ),
        (
            "rejected request requires rejection reason",
            lambda: (
                (
                    lambda request: (
                        request.update({"rejection_reason": None})
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(rejected_request())
            ),
        ),
        (
            "rejected request requires rejected audit event",
            lambda: (
                (
                    lambda request: (
                        request.update({
                            "audit_trail": request["audit_trail"][:1]
                        })
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(rejected_request())
            ),
        ),
        (
            "rejected actor must match audit actor",
            lambda: (
                (
                    lambda request: (
                        request.update({
                            "rejected_by": "engineer_3"
                        })
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(rejected_request())
            ),
        ),
        (
            "rejection reason must match audit event",
            lambda: (
                (
                    lambda request: (
                        request.update({
                            "rejection_reason": "Different reason."
                        })
                        or validate_approval_request(
                            request
                        )["success"] is False
                    )
                )(rejected_request())
            ),
        ),
    ]


cases = cases_for_security()

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

print(f"\n{passed}/{len(cases)} security tests passed")

if passed != len(cases):
    sys.exit(1)
