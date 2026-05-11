import time
from django.urls import resolve, Resolver404
from .db_wrapper import reset_query_log ,get_query_log
from .services import build_metric_payload
from .tasks import ingest_request_metric
from .conf import profiler_settings
from .utils import ingest_metric

class ApiProfilerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if any(request.path.startswith(path) for path in profiler_settings.IGNORED_PATHS):
            return self.get_response(request)

        try:
            url_match = resolve(request.path)
            route = url_match.route
            view_name = url_match.view_name
        except Resolver404:
            route = request.path
            view_name = None

        reset_query_log()
        start_time = time.perf_counter()

        try:
            response = self.get_response(request)
            has_exception = False
            exception = None

        except Exception as e:
            response = None
            has_exception = True
            exception = e
            raise

        finally:

            payload = build_metric_payload(
                path=request.path,
                method=request.method,
                status_code=response.status_code if response else 500,
                duration_ms= (time.perf_counter() - start_time) * 1000,
                route=route,
                view_name=view_name,
                has_exception=has_exception,
                exception_type=type(exception).__name__ if exception else None,
                exception_message=str(exception) if exception else None,
                queries=get_query_log(),
            )

            ingest_metric(payload)

        return response