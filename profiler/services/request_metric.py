from django.http import HttpRequest, HttpResponse
from ..models.request_metric import RequestMetric
from ..db_wrapper import get_query_log
from .n_plus_one import detect_n_plus_one
from ..conf import profiler_settings





def build_metric_payload(
    path: str,
    method: str,
    status_code: int,
    duration_ms: float,
    route: str | None = None,
    view_name: str | None = None,
    has_exception: bool = False,
    exception_type: str | None = None,
    exception_message: str | None = None,
    queries: list[dict] | None = None,
) -> dict:

    queries = queries or []

    n_plus_one_results = detect_n_plus_one(queries)
    has_n_plus_one = len(n_plus_one_results) > 0

    return {
        "path": path,
        "method": method,
        "status_code": status_code,
        "response_time_ms": duration_ms,
        "route": route,
        "view_name": view_name,
        "query_count": len(queries),
        "total_query_time_ms": sum(q["time_ms"] for q in queries),
        "has_exception": has_exception,
        "is_slow": duration_ms > profiler_settings.SLOW_REQUEST_THRESHOLD_MS,
        "exception_type": exception_type,
        "exception_message": exception_message,
        "has_n_plus_one": has_n_plus_one,
        "n_plus_one_details": n_plus_one_results if has_n_plus_one else None,
    }



def save_metric_payload(payload: dict) -> None:

    RequestMetric.objects.create(**payload)