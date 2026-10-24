import sys

sys.path.insert(0, "src")

from troubleshooting.fault_detector import detect_network_faults
from troubleshooting.root_cause_analyzer import analyze_root_cause


target = "R1:Gi0/1"

valid_evidence = {
    "success": True,
    "target": target,
    "evidence": [
        {
            "source": "diagnostic",
            "target": target,
            "cause_candidate": "administratively_disabled",
            "related_fault_type": "interface_down",
        }
    ],
}

valid_faults = {
    "success": True,
    "target": target,
    "faults": [
        {
            "fault_type": "interface_down",
            "severity": "high",
            "detection_strength": "high",
            "evidence": [],
        }
    ],
    "fault_count": 1,
}

cases = [
    (
        "valid root cause candidate",
        lambda: (
            analyze_root_cause(
                target, valid_evidence, valid_faults
            )["status"] == "possible"
        ),
    ),
    (
        "candidate without detected fault",
        lambda: (
            analyze_root_cause(
                target,
                valid_evidence,
                {
                    "success": True,
                    "target": target,
                    "faults": [],
                    "fault_count": 0,
                },
            )["status"] == "inconclusive"
            and analyze_root_cause(
                target,
                valid_evidence,
                {
                    "success": True,
                    "target": target,
                    "faults": [],
                    "fault_count": 0,
                },
            )["root_cause"] is None
        ),
    ),
    (
        "multiple candidates inconclusive",
        lambda: (
            analyze_root_cause(
                target,
                {
                    "success": True,
                    "target": target,
                    "evidence": [
                        {
                            "source": "diagnostic",
                            "target": target,
                            "cause_candidate": "cause_a",
                            "related_fault_type": "interface_down",
                        },
                        {
                            "source": "diagnostic",
                            "target": target,
                            "cause_candidate": "cause_b",
                            "related_fault_type": "interface_down",
                        },
                    ],
                },
                valid_faults,
            )["status"] == "inconclusive"
        ),
    ),
    (
        "mismatched fault type rejected",
        lambda: (
            analyze_root_cause(
                target,
                {
                    "success": True,
                    "target": target,
                    "evidence": [
                        {
                            "source": "diagnostic",
                            "target": target,
                            "cause_candidate": "administratively_disabled",
                            "related_fault_type": "device_down",
                        }
                    ],
                },
                {
                    "success": True,
                    "target": target,
                    "faults": [
                        {"fault_type": "interface_down"}
                    ],
                    "fault_count": 1,
                },
            )["status"] == "inconclusive"
            and analyze_root_cause(
                target,
                {
                    "success": True,
                    "target": target,
                    "evidence": [
                        {
                            "source": "diagnostic",
                            "target": target,
                            "cause_candidate": "administratively_disabled",
                            "related_fault_type": "device_down",
                        }
                    ],
                },
                {
                    "success": True,
                    "target": target,
                    "faults": [
                        {"fault_type": "interface_down"}
                    ],
                    "fault_count": 1,
                },
            )["root_cause"] is None
        ),
    ),
    (
        "target mismatch",
        lambda: (
            analyze_root_cause(
                "R2:Gi0/1", valid_evidence, valid_faults
            )["success"] is False
        ),
    ),
    (
        "invalid evidence object",
        lambda: (
            analyze_root_cause(
                target, [], valid_faults
            )["success"] is False
        ),
    ),
    (
        "missing evidence list",
        lambda: (
            analyze_root_cause(
                target,
                {"success": True, "target": target},
                valid_faults,
            )["success"] is False
        ),
    ),
    (
        "malformed evidence item",
        lambda: (
            analyze_root_cause(
                target,
                {
                    "success": True,
                    "target": target,
                    "evidence": ["invalid"],
                },
                valid_faults,
            )["success"] is False
        ),
    ),
    (
        "invalid fault result",
        lambda: (
            analyze_root_cause(
                target, valid_evidence, {}
            )["success"] is False
        ),
    ),
    (
        "fault detection and RCA integration",
        lambda: integration_test(),
    ),
]


def integration_test():
    evidence = {
        "success": True,
        "target": target,
        "evidence": [
            {
                "source": "events",
                "target": target,
                "type": "interface_down",
            },
            {
                "source": "diagnostic",
                "target": target,
                "cause_candidate": "administratively_disabled",
                "related_fault_type": "interface_down",
            },
        ],
    }

    faults = detect_network_faults(target, evidence)

    if not faults["success"] or faults["fault_count"] != 1:
        return False

    result = analyze_root_cause(target, evidence, faults)

    return (
        result["success"]
        and result["status"] == "possible"
        and result["root_cause"] == "administratively_disabled"
        and result["confidence"] == "low"
    )


passed = 0

for name, check in cases:
    try:
        ok = check()
    except Exception as exc:
        ok = False
        print(f"{name}: ERROR - {exc}")

    if ok:
        print(f"{name}: PASS")
        passed += 1
    else:
        print(f"{name}: FAIL")

print(f"\n{passed}/{len(cases)} tests passed")

if passed != len(cases):
    sys.exit(1)
