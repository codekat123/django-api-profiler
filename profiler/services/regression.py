import logging
from datetime import timedelta
from ..models import EndpointSummary
from ..conf import profiler_settings

logger = logging.getLogger(__name__)


def detect_regression(route: str, window_start, window_end) -> list[dict]:
    from ..tasks import fire_webhook

    previous_window_start = window_start - timedelta(
        minutes=profiler_settings.AGGREGATION_WINDOW_MINUTES
    )

    previous_summary = EndpointSummary.objects.filter(
        route=route,
        window_start=previous_window_start,
    ).first()

    current_summary = EndpointSummary.objects.filter(
        route=route,
        window_start=window_start,
    ).first()

    if not previous_summary or not current_summary:
        return []

    if current_summary.total_requests == 0 or previous_summary.total_requests == 0:
        return []

    regressions = []

    if current_summary.avg_response_ms > previous_summary.avg_response_ms * profiler_settings.REGRESSION_RESPONSE_TIME_FACTOR:
        payload = {
            "type": "response_time",
            "route": route,
            "previous_avg_ms": previous_summary.avg_response_ms,
            "current_avg_ms": current_summary.avg_response_ms,
        }
        regressions.append(payload)
        fire_webhook.delay(payload)
        logger.warning(
            "Response time regression on %s: %.2fms → %.2fms",
            route,
            previous_summary.avg_response_ms,
            current_summary.avg_response_ms,
        )

    current_error_rate = current_summary.error_count / current_summary.total_requests
    previous_error_rate = previous_summary.error_count / previous_summary.total_requests

    if current_error_rate > previous_error_rate + profiler_settings.REGRESSION_ERROR_RATE_DELTA:
        payload = {
            "type": "error_rate",
            "route": route,
            "previous_rate": round(previous_error_rate, 4),
            "current_rate": round(current_error_rate, 4),
        }
        regressions.append(payload)
        fire_webhook.delay(payload)
        logger.warning(
            "Error rate regression on %s: %.1f%% → %.1f%%",
            route,
            previous_error_rate * 100,
            current_error_rate * 100,
        )

    return regressions