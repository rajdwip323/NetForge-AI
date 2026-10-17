
import sys

sys.path.append("src")

from troubleshooting.evidence_collector import (
    collect_troubleshooting_evidence,
)
from troubleshooting.fault_detector import detect_network_faults


target = "R1:Gi0/1"

cases = [
    (
        "interface_down",
        [{
            "success": True,
            "target": target,
            "event_type": "interface_down",
            "severity": "high",
            "message": "Interface is down",
            "timestamp": "test",
            "error": None,
        }],
        None,
        "interface_down",
    ),
    (
        "device_down",
        [{
            "success": True,
            "target": target,
            "event_type": "device_down",
            "severity": "critical",
            "message": "Device is down",
            "timestamp": "test",
            "error": None,
        }],
        None,
        "device_down",
    ),
    (
        "connectivity_lost",
        [{
            "success": True,
            "target": target,
            "event_type": "connectivity_lost",
            "severity": "high",
            "message": "Connectivity lost",
            "timestamp": "test",
            "error": None,
        }],
        None,
        "connectivity_lost",
    ),
    (
        "verification_mismatch",
        None,
        {
            "results": [{
                "success": False,
                "verified": False,
                "target": target,
                "expected": "up",
                "actual": "down",
                "error": "State mismatch",
            }]
        },
        "verification_mismatch",
    ),
    ("no_fault", [], None, None),
]

passed = 0

for name, events, report, expected in cases:
    evidence = collect_troubleshooting_evidence(
        target=target,
        verification_report=report,
        events=events,
    )

    result = detect_network_faults(target, evidence)

    actual = (
        result["faults"][0]["fault_type"]
        if result["faults"]
        else None
    )

    ok = result["success"] and actual == expected

    print(f"{name}: {'PASS' if ok else 'FAIL'} (detected={actual})")

    if not ok:
        print("  Evidence collection:", evidence)
        print("  Fault detection:", result)
    else:
        passed += 1

print(f"\n{passed}/5 tests passed")

if passed != len(cases):
    sys.exit(1)
