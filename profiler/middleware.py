from .services import collect_request_metric

import time


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

            end_time = time.perf_counter()

            duration_ms = (end_time - start_time) * 1000

            collect_request_metric(
                request=request,
                response=response,
                duration_ms=duration_ms,
                has_exception=has_exception,
                exception=exception,
            )

        return response