import time
from django.urls import resolve, Resolver404
from .services import collect_request_metric
from .db_wrapper import reset_query_log


IGNORED_PATHS = [
    "/admin",
    "/static",
    "/favicon.ico",
]


class ApiProfilerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if any(request.path.startswith(path) for path in IGNORED_PATHS):
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
            duration_ms = (time.perf_counter() - start_time) * 1000

            collect_request_metric(
                request=request,
                response=response,
                duration_ms=duration_ms,
                has_exception=has_exception,
                exception=exception,
                route=route,
                view_name=view_name,
            )

        return response