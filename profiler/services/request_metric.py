from django.http import HttpRequest, HttpResponse
from ..models.request_metric import RequestMetric
from ..db_wrapper import get_query_log
from .n_plus_one import detect_n_plus_one

SLOW_REQUEST_THRESHOLD_MS = 1000


def collect_request_metric(
    request: HttpRequest,
    response: HttpResponse,
    duration_ms: float,
    has_exception: bool = False,
    exception: Exception | None = None,
    route: str | None = None,
    view_name: str | None = None,
) -> None:

    queries = get_query_log()

    query_count = len(queries)
    total_query_time_ms = sum(q["time_ms"] for q in queries)

    n_plus_one_results = detect_n_plus_one(queries)
    has_n_plus_one = len(n_plus_one_results) > 0

    RequestMetric.objects.create(
        path=request.path,
        method=request.method,
        status_code=response.status_code if response else 500,
        response_time_ms=duration_ms,
        query_count=query_count,
        total_query_time_ms=total_query_time_ms,
        has_exception=has_exception,
        is_slow=duration_ms > SLOW_REQUEST_THRESHOLD_MS,
        exception_type=type(exception).__name__ if exception else None,
        exception_message=str(exception) if exception else None,
        route=route,
        view_name=view_name,
        has_n_plus_one=has_n_plus_one,
        n_plus_one_details=n_plus_one_results if has_n_plus_one else None,
    )