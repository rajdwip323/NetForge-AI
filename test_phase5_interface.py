import sys

sys.path.append("src")

from verification.interface_verifier import verify_interface_state


def print_result(test_name, result):
    print(f"\n{test_name}:")
    print(result)


# ============================================================
# TEST 1 — PASS
# Expected and actual interface state match
# ============================================================

result_1 = verify_interface_state(
    interface="Gi0/1",
    expected_description="UPLINK_TO_CORE",
    expected_status="up",
    actual_description="UPLINK_TO_CORE",
    actual_status="up"
)

print_result("TEST 1 PASS", result_1)


# ============================================================
# TEST 2 — FAIL
# Description does not match
# ============================================================

result_2 = verify_interface_state(
    interface="Gi0/1",
    expected_description="WRONG_DESCRIPTION",
    expected_status="up",
    actual_description="UPLINK_TO_CORE",
    actual_status="up"
)

print_result("TEST 2 FAIL", result_2)


# ============================================================
# TEST 3 — ERROR
# Invalid actual status
# ============================================================

result_3 = verify_interface_state(
    interface="Gi0/1",
    expected_description="UPLINK_TO_CORE",
    expected_status="up",
    actual_description="UPLINK_TO_CORE",
    actual_status="invalid"
)

print_result("TEST 3 ERROR", result_3)


print("\nPhase 5.2 interface verification tests completed.")