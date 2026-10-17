
import sys

sys.path.append("src")

from troubleshooting.fault_detector import detect_network_faults

target = "R1:Gi0/1"

valid_evidence = {
    "success": True,
    "target": target,
    "evidence": [{
        "target": target,
        "type": "interface_down",
        "severity": "high",
    }],
}

cases = [
    (
        "empty target",
        detect_network_faults("", valid_evidence),
        False,
    ),
    (
        "invalid evidence object",
        detect_network_faults(target, None),
        False,
    ),
    (
        "evidence target mismatch",
        detect_network_faults(
            target,
            {**valid_evidence, "target": "R2"},
        ),
        False,
    ),
    (
        "malformed evidence item",
        detect_network_faults(
            target,
            {**valid_evidence, "evidence": ["invalid"]},
        ),
        False,
    ),
    (
        "unrelated target is ignored",
        detect_network_faults(
            target,
            {
                **valid_evidence,
                "evidence": [{
                    "target": "R2",
                    "type": "interface_down",
                    "severity": "high",
                }],
            },
        ),
        True,
    ),
]

passed = 0

for name, result, expected_success in cases:
    ok = result["success"] is expected_success

    if name == "unrelated target is ignored":
        ok = ok and result["fault_count"] == 0

    print(f"{name}: {'PASS' if ok else 'FAIL'}")

    if not ok:
        print(result)
    else:
        passed += 1

print(f"\n{passed}/{len(cases)} edge-case tests passed")

if passed != len(cases):
    sys.exit(1)
