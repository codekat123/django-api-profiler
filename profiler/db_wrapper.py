from django.db.backends.utils import CursorWrapper
import threading

_local = threading.local()

def reset_query_log():
    _local.queries = []

def get_query_log():
    return list(getattr(_local, "queries", []))

class ProfilingCursorWrapper(CursorWrapper):
    def execute(self, sql, params=None):
        import time
        start = time.perf_counter()
        try:
            return super().execute(sql, params)
        finally:
            duration = (time.perf_counter() - start) * 1000
            if not hasattr(_local, "queries"):
                _local.queries = []
            _local.queries.append({"sql": sql, "time_ms": duration})

    def executemany(self, sql, param_list):
        import time
        start = time.perf_counter()
        try:
            return super().executemany(sql, param_list)
        finally:
            duration = (time.perf_counter() - start) * 1000
            if not hasattr(_local, "queries"):
                _local.queries = []
            _local.queries.append({"sql": sql, "time_ms": duration})