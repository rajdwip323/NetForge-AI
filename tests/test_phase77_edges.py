
import sys

sys.path.insert(0, "src")

from troubleshooting.fix_recommender import (
    recommend_troubleshooting_fix,
)

target = "R1:Gi0/1"

item = {
    "source": "event",
    "target": target,
    "type": "interface_down",
}

evidence = {
    "success": True,
    "target": target,
    "evidence": [item],
}

faults = {
    "success": True,
    "target": target,
    "faults": [
        {
            "fault_type": "interface_down",
            "severity": "high",
            "evidence": [item],
        }
    ],
}

root_cause = {
    "success": True,
    "target": target,
    "status": "possible",
}

impact = {
    "success": True,
    "target": target,
    "status": "inconclusive",
}


def run(**overrides):
    args = {
        "target": target,
        "collected_evidence": evidence,
        "detected_faults": faults,
        "root_cause_result": root_cause,
        "impact_result": impact,
    }
    args.update(overrides)
    return recommend_troubleshooting_fix(**args)


cases = [
    (
        "empty target rejected",
        lambda: run(target="")["success"] is False,
    ),
    (
        "evidence must be a dictionary",
        lambda: run(collected_evidence=[])["success"] is False,
    ),
    (
        "failed evidence rejected",
        lambda: run(
            collected_evidence={**evidence, "success": False}
        )["success"] is False,
    ),
    (
        "fault target mismatch rejected",
        lambda: run(
            detected_faults={**faults, "target": "R9:Gi0/1"}
        )["success"] is False,
    ),
    (
        "root cause target mismatch rejected",
        lambda: run(
            root_cause_result={
                **root_cause,
                "target": "R9:Gi0/1",
            }
        )["success"] is False,
    ),
    (
        "impact target mismatch rejected",
        lambda: run(
            impact_result={
                **impact,
                "target": "R9:Gi0/1",
            }
        )["success"] is False,
    ),
    (
        "malformed evidence item rejected",
        lambda: run(
            collected_evidence={
                **evidence,
                "evidence": ["invalid"],
            }
        )["success"] is False,
    ),
    (
        "unsupported root cause status rejected",
        lambda: run(
            root_cause_result={
                **root_cause,
                "status": "confirmed",
            }
        )["success"] is False,
    ),
    (
        "unsupported impact status rejected",
        lambda: run(
            impact_result={
                **impact,
                "status": "critical",
            }
        )["success"] is False,
    ),
    (
        "fault without matching evidence gives no recommendation",
        lambda: run(
            detected_faults={
                **faults,
                "faults": [
                    {
                        "fault_type": "interface_down",
                        "evidence": [
                            {
                                "target": "R9:Gi0/1",
                                "type": "interface_down",
                            }
                        ],
                    }
                ],
            }
        )["status"] == "inconclusive",
    ),
    (
        "uncollected evidence cannot support recommendation",
        lambda: run(
            detected_faults={
                **faults,
                "faults": [
                    {
                        "fault_type": "interface_down",
                        "evidence": [
                            {
                                "source": "event",
                                "target": target,
                                "type": "interface_down",
                                "extra": "not in collected evidence",
                            }
                        ],
                    }
                ],
            }
        )["status"] == "inconclusive",
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
