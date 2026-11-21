
import sys
import unittest

sys.path.insert(0, "src")

from deployment.deployment_models import (
    build_deployment_authorization,
)


class TestPhase7101Security(unittest.TestCase):

    def _build_authorization(self, **overrides):
        data = {
            "authorization_id": "AUTH-001",
            "plan_id": "PLAN-001",
            "target": "R1",
            "plan_fingerprint": "abc123",
            "requested_by": "engineer_1",
            "approved_by": "approver_1",
            "status": "approved",
            "issued_at": "2026-11-21T10:00:00+00:00",
            "expires_at": "2026-11-21T11:00:00+00:00",
        }
        data.update(overrides)

        return build_deployment_authorization(**data)

    def test_requester_cannot_approve_own_request(self):
        with self.assertRaises(ValueError):
            self._build_authorization(
                approved_by="engineer_1"
            )

    def test_requester_approver_comparison_is_case_insensitive(self):
        with self.assertRaises(ValueError):
            self._build_authorization(
                requested_by="Engineer_1",
                approved_by="engineer_1",
            )

    def test_timezone_missing_from_issued_at_rejected(self):
        with self.assertRaises(ValueError):
            self._build_authorization(
                issued_at="2026-11-21T10:00:00"
            )

    def test_invalid_expiry_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            self._build_authorization(
                expires_at="not-a-timestamp"
            )

    def test_expiry_before_issue_time_rejected(self):
        with self.assertRaises(ValueError):
            self._build_authorization(
                issued_at="2026-11-21T12:00:00+00:00",
                expires_at="2026-11-21T11:00:00+00:00",
            )

    def test_expiry_equal_to_issue_time_rejected(self):
        with self.assertRaises(ValueError):
            self._build_authorization(
                issued_at="2026-11-21T10:00:00+00:00",
                expires_at="2026-11-21T10:00:00+00:00",
            )

    def test_valid_separate_approver_and_expiry_accepted(self):
        result = self._build_authorization()

        self.assertEqual(result["requested_by"], "engineer_1")
        self.assertEqual(result["approved_by"], "approver_1")
        self.assertEqual(result["status"], "approved")


if __name__ == "__main__":
    unittest.main()
