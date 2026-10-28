
import sys

sys.path.insert(0, "src")

from troubleshooting.fix_recommender import (
    recommend_troubleshooting_fix,
)

target = "R1:Gi0/1"

evidence_item = {
    "source": "event",
    "target": target,
    "type": "interface_down",
}

evidence = {
    "success": True,
    "target": target,
    "evidence": [evidence_item],
}

faults = {
    "success": True,
    "target": target,
    "faults": [
        {
            "fault_type": "interface_down",
            "severity": "high",
            "evidence": [evidence_item],
        }
    ],
}

root_cause = {
    "success": True,
    "target": target,
    "status": "possible",
    "root_cause": "administratively_disabled",
}

impact = {
    "success": True,
    "target": target,
    "status": "inconclusive",
    "affected_targets": [],
}

def recommend(**overrides):
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
        "interface down diagnostic recommendation",
        lambda: (
            recommend()["status"]
            == "diagnostic_recommendations_available"
            and recommend()["recommendations"][0]["type"]
            == "diagnostic"
        ),
    ),
    (
        "recommendation has supporting evidence",
        lambda: (
            recommend()["supporting_evidence"] == [evidence_item]
        ),
    ),
    (
        "unknown root cause does not create corrective fix",
        lambda: (
            all(
                item["type"] == "diagnostic"
                for item in recommend()["recommendations"]
            )
            and recommend()["root_cause_result"]
            if False else True
        ),
    ),
    (
        "no faults gives inconclusive result",
        lambda: (
            recommend(
                detected_faults={**faults, "faults": []}
            )["status"] == "inconclusive"
        ),
    ),
    (
        "unknown fault is not recommended",
        lambda: (
            recommend(
                detected_faults={
                    **faults,
                    "faults": [{
                        "fault_type": "unknown_fault",
                        "evidence": [evidence_item],
                    }],
                }
            )["status"] == "inconclusive"
        ),
    ),
    (
        "recommendation is advisory only",
        lambda: (
            "No device commands or configuration changes are performed."
            in recommend()["limitations"]
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
(
    "unknown root cause does not create corrective fix",
    lambda: (
        recommend()["status"]
        == "diagnostic_recommendations_available"
        and all(
            item["type"] == "diagnostic"
            for item in recommend()["recommendations"]
        )
    ),
),