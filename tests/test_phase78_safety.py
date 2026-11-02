
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
}

impact = analyze_impact(
    target, evidence, faults, root_cause
)

recommendation = recommend_troubleshooting_fix(
    target,
    evidence,
    faults,
    root_cause,
    impact,
)


def run_preview(
    preview_target=target,
    recommended_fix=None,
    impact_result=None,
):
    return run_dry_run(
        preview_target,
        recommendation if recommended_fix is None else recommended_fix,
        impact if impact_result is None else impact_result,
    )


valid_result = run_preview()
error_result = run_preview(preview_target="")


cases = [
    (
        "successful preview is never executed",
        lambda: valid_result["executed"] is False,
    ),
    (
        "error result is never executed",
        lambda: error_result["executed"] is False,
    ),
    (
        "successful preview generates no device commands",
        lambda: (
            "No device commands are generated or executed."
            in valid_result["limitations"]
        ),
    ),
    (
        "preview does not change device configuration",
        lambda: (
            "No device configuration is changed."
            in valid_result["limitations"]
        ),
    ),
    (
        "preview remains read-only",
        lambda: (
            valid_result["preview"]["type"]
            == "read_only_diagnostic"
        ),
    ),
    (
        "risk is not falsely estimated",
        lambda: valid_result["risk"] == "unknown",
    ),
    (
        "error result preserves safety limitations",
        lambda: (
            error_result["success"] is False
            and "No device commands were executed."
            in error_result["limitations"]
            and "No device configuration was changed."
            in error_result["limitations"]
        ),
    ),
    (
        "execution cannot be enabled through input",
        lambda: (
            run_preview(
                recommended_fix={
                    **recommendation,
                    "executed": True,
                },
                impact_result={
                    **impact,
                    "executed": True,
                },
            )["executed"] is False
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

print(f"\n{passed}/{len(cases)} safety tests passed")

if passed != len(cases):
    sys.exit(1)
