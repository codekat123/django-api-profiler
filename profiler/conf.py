from django.conf import settings

_DEFAULTS = {
    "ASYNC": False,
    "SLOW_REQUEST_THRESHOLD_MS": 1000,
    "AGGREGATION_WINDOW_MINUTES": 60,
    "IGNORED_PATHS": ["/admin", "/static", "/favicon.ico"],
    "N_PLUS_ONE_THRESHOLD": 3,
    "SLOW_QUERY_THRESHOLD_MS": 100,
    "REGRESSION_RESPONSE_TIME_FACTOR": 2.0,
    "REGRESSION_ERROR_RATE_DELTA": 0.1,
    "WEBHOOK_URL": None,
}


class ProfilerSettings:

    def __init__(self):
        self._user_settings = getattr(settings, "PROFILER", {})

    def __getattr__(self, name):
        if name not in _DEFAULTS:
            raise AttributeError(f"Invalid profiler setting: '{name}'")
        
        default = _DEFAULTS[name]
        user_value = self._user_settings.get(name, default)

        return user_value
    


profiler_settings = ProfilerSettings()