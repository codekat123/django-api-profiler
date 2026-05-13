from django.test import TestCase
from ..services import build_metric_payload


class BuildMetricPayloadTests(TestCase):

    def test_marks_slow_request(self):
        payload = build_metric_payload(
            path="/api/users/",
            method="GET",
            status_code=200,
            duration_ms=2000,
        )
        self.assertTrue(payload["is_slow"])

    def test_does_not_mark_fast_request_as_slow(self):
        payload = build_metric_payload(
            path="/api/users/",
            method="GET",
            status_code=200,
            duration_ms=200,
        )
        self.assertFalse(payload["is_slow"])


    def test_marks_exception_correctly(self):
        payload = build_metric_payload(
            path="/api/users/",
            method="GET",
            status_code=500,
            duration_ms=100,
            has_exception=True,
            exception_type="ValueError",
            exception_message="something went wrong",
        )
        self.assertTrue(payload["has_exception"])
        self.assertEqual(payload["exception_type"], "ValueError")
        self.assertEqual(payload["exception_message"], "something went wrong")

    def test_n_plus_one_detected_in_payload(self):
        queries = [
            {"sql": "SELECT * FROM users WHERE id = 1", "time_ms": 1},
            {"sql": "SELECT * FROM users WHERE id = 2", "time_ms": 1},
            {"sql": "SELECT * FROM users WHERE id = 3", "time_ms": 1},
        ]
        payload = build_metric_payload(
            path="/api/users/",
            method="GET",
            status_code=200,
            duration_ms=100,
            queries=queries,
        )
        self.assertTrue(payload["has_n_plus_one"])