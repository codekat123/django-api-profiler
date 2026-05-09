from django.db import connection
from django.http import HttpRequest , HttpResponse
from ..models import RequestMetric

SLOW_REQUEST_THRESHOLD_MS = 1000

def collect_request_metric(
    request: HttpRequest,
    response: HttpResponse,
    duration_ms,
    has_exception=False,
    exception=None,
) -> None:

    query_count = len(connection.queries)

    total_query_time_ms = sum(
        float(query["time"]) * 1000
        for query in connection.queries
    )

    RequestMetric.objects.create(
        path=request.path,
        method=request.method,

        status_code=response.status_code if response else 500,

        response_time_ms=duration_ms,

        query_count=query_count,
        total_query_time_ms=total_query_time_ms,

        has_exception=has_exception,
        is_slow=duration_ms > SLOW_REQUEST_THRESHOLD_MS,
        exception_type=(
            type(exception).__name__
            if exception
            else None
        ),

        exception_message=(
            str(exception)
            if exception
            else None
        ),
    )