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
        "unsuccessful evidence rejected",
        lambda: analyze_impact(
            target, {**evidence, "success": False},
            faults, root_cause, [dependency]
        )["success"] is False,
    ),
    (
        "RCA target mismatch rejected",
        lambda: analyze_impact(
            target, evidence, faults,
            {**root_cause, "target": "R9:Gi0/1"},
            [dependency],
        )["success"] is False,
    ),
    (
        "invalid dependency relationship rejected",
        lambda: analyze_impact(
            target, evidence, faults, root_cause,
            [{**dependency, "relationship": "connected_to"}],
        )["success"] is False,
    ),
    (
        "invalid dependency source rejected",
        lambda: analyze_impact(
            target, evidence, faults, root_cause,
            [{**dependency, "source": "unknown"}],
        )["success"] is False,
    ),
    (
        "duplicate dependency target appears once",
        lambda: analyze_impact(
            target, evidence, faults, root_cause,
            [dependency, dependency],
        )["affected_targets"] == ["R2:Gi0/0"],
    ),
    (
        "whitespace-normalized dependency matches",
        lambda: analyze_impact(
            target, evidence, faults, root_cause,
            [{**dependency, "depends_on": f"  {target}  "}],
        )["affected_targets"] == ["R2:Gi0/0"],
    ),
    (
        "self-dependency is not an affected target",
        lambda: analyze_impact(
            target, evidence, faults, root_cause,
            [{**dependency, "target": target}],
        )["affected_targets"] == [],
    ),
    (
        "inconclusive RCA does not block evidence-based impact",
        lambda: analyze_impact(
            target, evidence, faults,
            {**root_cause, "status": "inconclusive", "root_cause": None},
            [dependency],
        )["affected_targets"] == ["R2:Gi0/0"],
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
