import sys

sys.path.append("src")

import automation.config_manager as cm


# ============================================================
# Fake SSH Client — Successful Command
# ============================================================

class FakeChannel:
    def recv_exit_status(self):
        return 0


class FakeStdout:
    channel = FakeChannel()

    def read(self):
        return (
            b"Port      Status       Protocol\n"
            b"Gi0/1     up           up        UPLINK_TO_CORE\n"
        )


class FakeStderr:
    def read(self):
        return b""


class FakeClient:
    def exec_command(self, command):
        return (
            None,
            FakeStdout(),
            FakeStderr()
        )


# ============================================================
# Fake SSH Client — Command Failure
# ============================================================

class ErrorClient:
    def exec_command(self, command):
        raise Exception("Simulated SSH command failure")


# ============================================================
# Create Clients
# ============================================================

success_client = FakeClient()
error_client = ErrorClient()


# ============================================================
# TEST 1 — VERIFICATION PASS
# ============================================================

print("========================================")
print("TEST 1: VERIFICATION PASS")
print("========================================")

pass_result = cm.verify_interface(
    success_client,
    "Gi0/1",
    "UPLINK_TO_CORE",
    "up"
)

print(pass_result)


# ============================================================
# TEST 2 — VERIFICATION FAIL
# ============================================================

print("\n========================================")
print("TEST 2: VERIFICATION FAIL")
print("========================================")

fail_result = cm.verify_interface(
    success_client,
    "Gi0/1",
    "WRONG_DESCRIPTION",
    "up"
)

print(fail_result)


# ============================================================
# TEST 3 — VERIFICATION ERROR
# ============================================================

print("\n========================================")
print("TEST 3: VERIFICATION ERROR")
print("========================================")

error_result = cm.verify_interface(
    error_client,
    "Gi0/1",
    "UPLINK_TO_CORE",
    "up"
)

print(error_result)