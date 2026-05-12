from django.test import TestCase
from ..services import build_metric_payload


class BuildMetricTest(TestCase):

    def test_marks_slow_request(self):
        payload = build_metric_payload(
            path="/api/users/",
            method="GET",
            status_code=200,
            duration_ms=2000,
        )
        self.assertTrue(payload["is_slow"])