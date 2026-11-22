
import sys
import unittest

sys.path.insert(0, "src")

from deployment.deployment_models import (
    build_deployment_result,
    EXECUTION_MODE_MOCK,
)


class TestPhase7101Consistency(unittest.TestCase):

    def test_all_statuses_have_correct_flags(self):
        cases = [
            ("pending", 0, 0, False, False),
            ("running", 0, 0, False, False),
            ("completed", 1, 0, True, True),
            ("partially_failed", 1, 1, False, True),
            ("failed", 0, 1, False, True),
            ("cancelled", 0, 0, False, False),
        ]

        for status, applied, failed, success, executed in cases:
            with self.subTest(status=status):
                result = build_deployment_result(
                    "D1", "R1",
                    status=status,
                    actions_applied=applied,
                    actions_failed=failed,
                )
                self.assertEqual(result["success"], success)
                self.assertEqual(result["executed"], executed)

    def test_success_only_for_completed(self):
        for status in (
            "pending", "running", "partially_failed",
            "failed", "cancelled"
        ):
            result = build_deployment_result(
                "D1", "R1", status=status,
                actions_applied=1 if status == "partially_failed" else 0,
                actions_failed=1 if status in ("partially_failed", "failed") else 0,
            )
            self.assertFalse(result["success"])

    def test_executed_statuses(self):
        for status, applied, failed in (
            ("completed", 1, 0),
            ("partially_failed", 1, 1),
            ("failed", 0, 1),
        ):
            result = build_deployment_result(
                "D1", "R1", status=status,
                actions_applied=applied,
                actions_failed=failed,
            )
            self.assertTrue(result["executed"])

    def test_non_executed_statuses(self):
        for status in ("pending", "running", "cancelled"):
            result = build_deployment_result(
                "D1", "R1", status=status
            )
            self.assertFalse(result["executed"])

    def test_zero_action_counts_preserved(self):
        result = build_deployment_result(
            "D1", "R1", status="completed"
        )
        self.assertEqual(result["actions_applied"], 0)
        self.assertEqual(result["actions_failed"], 0)

    def test_positive_action_counts_preserved(self):
        result = build_deployment_result(
            "D1", "R1", status="completed",
            actions_applied=5,
        )
        self.assertEqual(result["actions_applied"], 5)
        self.assertEqual(result["actions_failed"], 0)

    def test_mixed_action_counts_preserved(self):
        result = build_deployment_result(
            "D1", "R1", status="partially_failed",
            actions_applied=3, actions_failed=2,
        )
        self.assertEqual(result["actions_applied"], 3)
        self.assertEqual(result["actions_failed"], 2)

    def test_action_counts_do_not_change_completed_flags(self):
        result = build_deployment_result(
            "D1", "R1", status="completed",
            actions_applied=0, actions_failed=0,
        )
        self.assertTrue(result["success"])
        self.assertTrue(result["executed"])

    def test_completed_rejects_failed_actions(self):
        with self.assertRaises(ValueError):
            build_deployment_result(
                "D1", "R1", status="completed",
                actions_applied=4, actions_failed=2,
            )

    def test_partially_failed_requires_both_counts(self):
        invalid_cases = [
            (0, 2),
            (3, 0),
            (0, 0),
        ]

        for applied, failed in invalid_cases:
            with self.subTest(applied=applied, failed=failed):
                with self.assertRaises(ValueError):
                    build_deployment_result(
                        "D1", "R1",
                        status="partially_failed",
                        actions_applied=applied,
                        actions_failed=failed,
                    )

    def test_valid_partially_failed_accepted(self):
        result = build_deployment_result(
            "D1", "R1",
            status="partially_failed",
            actions_applied=3,
            actions_failed=2,
        )
        self.assertFalse(result["success"])
        self.assertTrue(result["executed"])

    def test_pending_verification_does_not_change_execution(self):
        result = build_deployment_result(
            "D1", "R1", status="completed",
            actions_applied=2,
            verification_status="pending",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["verification_status"], "pending")

    def test_failed_verification_is_independent(self):
        result = build_deployment_result(
            "D1", "R1", status="completed",
            actions_applied=2,
            verification_status="failed",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["verification_status"], "failed")

    def test_mismatch_verification_preserved(self):
        result = build_deployment_result(
            "D1", "R1",
            verification_status="mismatch",
        )
        self.assertEqual(result["verification_status"], "mismatch")

    def test_unavailable_verification_preserved(self):
        result = build_deployment_result(
            "D1", "R1",
            verification_status="unavailable",
        )
        self.assertEqual(result["verification_status"], "unavailable")

    def test_all_results_use_mock_execution_mode(self):
        result = build_deployment_result(
            "D1", "R1", status="completed"
        )
        self.assertEqual(
            result["execution_mode"], EXECUTION_MODE_MOCK
        )

    def test_required_contract_fields_present(self):
        result = build_deployment_result("D1", "R1")

        required_fields = {
            "schema_version",
            "deployment_id",
            "target",
            "status",
            "success",
            "executed",
            "execution_mode",
            "actions_applied",
            "actions_failed",
            "verification_status",
            "error",
            "created_at",
        }

        self.assertTrue(required_fields.issubset(result.keys()))


if __name__ == "__main__":
    unittest.main()
