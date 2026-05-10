from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Avg, Max, Min, Q
from datetime import timedelta
from ..models import RequestMetric, EndpointSummary


def _get_window_minutes() -> int:
    profiler_settings = getattr(settings, "PROFILER", {})
    return profiler_settings.get("AGGREGATION_WINDOW_MINUTES", 60)


def _get_last_completed_window() -> tuple:
    now = timezone.now()
    window_minutes = _get_window_minutes()

    minutes_since_epoch = int(now.timestamp() // 60)
    window_start_minutes = (minutes_since_epoch // window_minutes) * window_minutes
    window_start = timezone.datetime.fromtimestamp(
        window_start_minutes * 60,
        tz=timezone.utc
    )

    window_end = window_start
    window_start = window_end - timedelta(minutes=window_minutes)

    return window_start, window_end


def _calculate_p95(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * 0.95)
    return sorted_values[min(index, len(sorted_values) - 1)]


def compute_endpoint_summaries() -> int:

    window_start, window_end = _get_last_completed_window()

    metrics_in_window = RequestMetric.objects.filter(
        created_at__gte=window_start,
        created_at__lt=window_end,
    )

    if not metrics_in_window.exists():
        return 0

    routes = metrics_in_window.values_list("route", flat=True).distinct()

    count = 0

    for route in routes:
        route_metrics = metrics_in_window.filter(route=route)

        response_times = list(
            route_metrics.values_list("response_time_ms", flat=True)
        )


        aggregates = route_metrics.aggregate(
            total_requests=Count("id"),
            avg_response_ms=Avg("response_time_ms"),
            max_response_ms=Max("response_time_ms"),
            min_response_ms=Min("response_time_ms"),
            error_count=Count("id", filter=Q(status_code__gte=400)),
            slow_count=Count("id", filter=Q(is_slow=True)),
            n_plus_one_count=Count("id", filter=Q(has_n_plus_one=True)),
        )

        EndpointSummary.objects.update_or_create(
            route=route,
            window_start=window_start,
            defaults={
                "window_end": window_end,
                "p95_response_ms": _calculate_p95(response_times),
                **aggregates,
            }
        )

        count += 1

    return count