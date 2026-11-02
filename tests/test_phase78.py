
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
recommendation = build_recommendation()


def run_preview(
    recommended_fix=None,
    impact_result=None,
    preview_target=target,
):
    return run_dry_run(
        preview_target,
        recommendation if recommended_fix is None else recommended_fix,
        impact if impact_result is None else impact_result,
    )


cases = [
    (
        "valid diagnostic preview",
        lambda: (
            run_preview()["success"] is True
            and run_preview()["status"] == "preview_ready"
        ),
    ),
    (
        "preview target is preserved",
        lambda: run_preview()["target"] == target,
    ),
    (
        "diagnostic recommendation is included",
        lambda: (
            run_preview()["proposed_actions"][0]["fault_type"]
            == "interface_down"
            and run_preview()["proposed_actions"][0]["type"]
            == "diagnostic"
        ),
    ),
    (
        "supporting evidence is validated",
        lambda: (
            run_preview()["success"] is True
            and run_preview()["proposed_actions"]
        ),
    ),
    (
        "inconclusive impact is preserved",
        lambda: (
            run_preview()["impact"]["status"] == "inconclusive"
            and run_preview()["impact"]["confidence"] == "none"
        ),
    ),
    (
        "potential impact is preserved",
        lambda: (
            run_preview(
                impact_result=build_impact([dependency])
            )["impact"]["affected_targets"] == ["R2:Gi0/0"]
        ),
    ),
    (
        "impact severity remains unknown",
        lambda: (
            run_preview()["impact"]["impact_severity"] == "unknown"
        ),
    ),
    (
        "risk remains unknown without risk evidence",
        lambda: run_preview()["risk"] == "unknown",
    ),
    (
        "preview is never executed",
        lambda: run_preview()["executed"] is False,
    ),
    (
        "no device commands are generated",
        lambda: (
            "No device commands are generated or executed."
            in run_preview()["limitations"]
        ),
    ),
    (
        "inconclusive root cause permits diagnostic preview",
        lambda: (
            run_preview(
                recommended_fix=build_recommendation(
                    root_cause_result={
                        **root_cause,
                        "status": "inconclusive",
                    }
                )
            )["status"] == "preview_ready"
        ),
    ),
    (
        "multiple diagnostic recommendations are preserved",
        lambda: (
            run_preview(
                recommended_fix={
                    **recommendation,
                    "recommendations": (
                        recommendation["recommendations"]
                        + [{
                            "fault_type": "interface_down",
                            "type": "diagnostic",
                            "action": "Review interface operational state.",
                            "confidence": "low",
                        }]
                    ),
                }
            )["success"] is True
            and len(
                run_preview(
                    recommended_fix={
                        **recommendation,
                        "recommendations": (
                            recommendation["recommendations"]
                            + [{
                                "fault_type": "interface_down",
                                "type": "diagnostic",
                                "action": "Review interface operational state.",
                                "confidence": "low",
                            }]
                        ),
                    }
                )["proposed_actions"]
            ) == 2
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
