
import sys

sys.path.insert(0, "src")

from troubleshooting.dry_run_engine import run_dry_run
from troubleshooting.fix_recommender import (
    recommend_troubleshooting_fix,
)
from troubleshooting.impact_analyzer import analyze_impact


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

dependency = {
    "source": "dependency",
    "target": "R2:Gi0/0",
    "depends_on": target,
    "dependency_type": "network_link",
    "relationship": "depends_on",
}


def build_impact(dependencies=None, **overrides):
    result = analyze_impact(
        target,
        evidence,
        faults,
        root_cause,
        dependencies,
    )
    result.update(overrides)
    return result


impact = build_impact()


def build_recommendation(**overrides):
    args = {
        "target": target,
        "collected_evidence": evidence,
        "detected_faults": faults,
        "root_cause_result": root_cause,
        "impact_result": impact,
    }
    args.update(overrides)
    return recommend_troubleshooting_fix(**args)


recommendation = build_recommendation()


def run_preview(recommended_fix=None, impact_result=None, preview_target=target):
    return run_dry_run(
        preview_target,
        recommendation if recommended_fix is None else recommended_fix,
        impact if impact_result is None else impact_result,
    )


def invalid_recommendation(**changes):
    result = dict(recommendation)
    result.update(changes)
    return result


def invalid_impact(**changes):
    result = dict(impact)
    result.update(changes)
    return result


def invalid_preview(recommended_fix=None, impact_result=None, preview_target=target):
    result = run_preview(
        recommended_fix=recommended_fix,
        impact_result=impact_result,
        preview_target=preview_target,
    )
    return result["success"] is False and result["executed"] is False


cases = [
    (
        "empty target rejected",
        lambda: invalid_preview(preview_target=" "),
    ),
    (
        "non-string target rejected",
        lambda: invalid_preview(preview_target=["R1:Gi0/1"]),
    ),
    (
        "non-dictionary recommendation rejected",
        lambda: invalid_preview(recommended_fix=[]),
    ),
    (
        "unsuccessful recommendation rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(success=False)
        ),
    ),
    (
        "recommendation target mismatch rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(target="R2:Gi0/0")
        ),
    ),
    (
        "unsupported recommendation status rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(status="unknown")
        ),
    ),
    (
        "empty recommendation list rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(recommendations=[])
        ),
    ),
    (
        "empty supporting evidence rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(supporting_evidence=[])
        ),
    ),
    (
        "malformed recommendation item rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(recommendations=["invalid"])
        ),
    ),
    (
        "malformed fault type rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(
                recommendations=[
                    {
                        **recommendation["recommendations"][0],
                        "fault_type": ["interface_down"],
                    }
                ]
            )
        ),
    ),
    (
        "unsupported fault type rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(
                recommendations=[
                    {
                        **recommendation["recommendations"][0],
                        "fault_type": "unknown_fault",
                    }
                ]
            )
        ),
    ),
    (
        "empty diagnostic action rejected",
        lambda: invalid_preview(
            recommended_fix=invalid_recommendation(
                recommendations=[
                    {
                        **recommendation["recommendations"][0],
                        "action": " ",
                    }
                ]
            )
        ),
    ),
    (
        "malformed impact status rejected",
        lambda: invalid_preview(
            impact_result=invalid_impact(status=["inconclusive"])
        ),
    ),
    (
        "unsupported impact status rejected",
        lambda: invalid_preview(
            impact_result=invalid_impact(status="unknown")
        ),
    ),
    (
        "incorrect impact severity rejected",
        lambda: invalid_preview(
            impact_result=invalid_impact(impact_severity="high")
        ),
    ),
    (
        "self affected target rejected",
        lambda: invalid_preview(
            impact_result=invalid_impact(
                status="potential_impact_identified",
                affected_targets=[target],
                supporting_evidence=[dependency],
                confidence="low",
            )
        ),
    ),
    (
        "preview remains unexecuted after validation errors",
        lambda: (
            invalid_preview(recommended_fix=[])
            and run_preview()["executed"] is False
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
