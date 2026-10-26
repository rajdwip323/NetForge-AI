import sys

sys.path.insert(0, "src")

from troubleshooting.impact_analyzer import analyze_impact


target = "R1:Gi0/1"

evidence = {
    "success": True,
    "target": target,
    "evidence": [],
}

faults = {
    "success": True,
    "target": target,
    "faults": [
        {"fault_type": "interface_down", "severity": "high"}
    ],
}

root_cause = {
    "success": True,
    "target": target,
    "status": "possible",
    "root_cause": "administratively_disabled",
}

dependency = {
    "source": "dependency",
    "target": "R2:Gi0/0",
    "depends_on": target,
    "dependency_type": "network_link",
    "relationship": "depends_on",
}


cases = [
    (
        "valid dependency",
        lambda: (
            analyze_impact(
                target, evidence, faults, root_cause, [dependency]
            )["affected_targets"] == ["R2:Gi0/0"]
        ),
    ),
    (
        "missing dependency is inconclusive",
        lambda: (
            analyze_impact(
                target, evidence, faults, root_cause
            )["status"] == "inconclusive"
        ),
    ),
    (
        "multiple dependent targets",
        lambda: (
            analyze_impact(
                target, evidence, faults, root_cause,
                [
                    dependency,
                    {
                        **dependency,
                        "target": "R3:Gi0/1",
                    },
                ],
            )["affected_targets"]
            == ["R2:Gi0/0", "R3:Gi0/1"]
        ),
    ),
    (
        "empty target rejected",
        lambda: (
            analyze_impact(
                "", evidence, faults, root_cause
            )["success"] is False
        ),
    ),
    (
        "invalid evidence rejected",
        lambda: (
            analyze_impact(
                target, [], faults, root_cause
            )["success"] is False
        ),
    ),
    (
        "target mismatch rejected",
        lambda: (
            analyze_impact(
                "R2:Gi0/1", evidence, faults, root_cause
            )["success"] is False
        ),
    ),
    (
        "malformed dependency rejected",
        lambda: (
            analyze_impact(
                target, evidence, faults, root_cause,
                [{"source": "dependency"}],
            )["success"] is False
        ),
    ),
    (
        "fault target mismatch rejected",
        lambda: (
            analyze_impact(
                target, evidence,
                {**faults, "target": "R9:Gi0/1"},
                root_cause,
            )["success"] is False
        ),
    ),
    (
        "invalid root cause result rejected",
        lambda: (
            analyze_impact(
                target, evidence, faults, {}
            )["success"] is False
        ),
    ),
    (
        "no fault does not infer impact",
        lambda: (
            analyze_impact(
                target, evidence,
                {**faults, "faults": []},
                root_cause, [dependency],
            )["affected_targets"] == []
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

print(f"\n{passed}/{len(cases)} tests passed")

if passed != len(cases):
    sys.exit(1)
