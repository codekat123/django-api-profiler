# Django API Profiler

![PyPI](https://img.shields.io/pypi/v/django-api-profiler)
![Python](https://img.shields.io/pypi/pyversions/django-api-profiler)
![License](https://img.shields.io/pypi/l/django-api-profiler)

Lightweight Django middleware package for API profiling, endpoint analytics, and performance monitoring with intelligent query analysis and automatic regression detection.

---

## Features

- **Request tracking** — response time, status code, HTTP method per request
- **Database query monitoring** — query count and total execution time per request
- **N+1 query detection** — automatic identification of repeated query patterns
- **Endpoint aggregation** — hourly summaries with avg, p95, min, max, error rates
- **Performance regression detection** — compares windows and flags degradation
- **Webhook alerts** — fire notifications to Slack or any URL on regression
- **Exception tracking** — complete error monitoring with type and message
- **Async processing** — optional Celery integration with automatic sync fallback
- **Django admin dashboard** — colored response times, filtering, searching

---

## Installation

```bash
pip install django-api-profiler

# With async support (recommended for production)
pip install "django-api-profiler[async]"

# With webhook alerts
pip install "django-api-profiler[webhook]"

# Everything
pip install "django-api-profiler[all]"
```

---

## Quick Start

```python
# settings.py
INSTALLED_APPS = [
    ...
    'profiler',
]

MIDDLEWARE = [
    ...
    'profiler.middleware.ApiProfilerMiddleware',
]
```

```bash
python manage.py migrate
```

Visit `/admin` to view metrics immediately. No other configuration required.

---

## ⚠️ Performance Warning

By default, metrics are written **synchronously** on every request. This adds
latency to your API because every request waits for a database write to complete
before returning a response.

For production use, enable async processing:

```bash
pip install "django-api-profiler[async]"
```

```python
# settings.py
PROFILER = {
    "ASYNC": True,
}
```

Make sure Redis and a Celery worker are running:

```bash
celery -A your_project worker --loglevel=info
```

This offloads metric writes to a Celery worker, keeping your API response
times completely unaffected by the profiler.

---

## Endpoint Aggregation

Aggregation computes hourly summaries per endpoint — enabling performance
trending over time. Each summary includes total requests, avg/p95/max/min
response times, error count, slow request count, and N+1 occurrence count.

**With Celery Beat (recommended):**

Aggregation runs automatically every hour. See Celery Beat Setup below.

**Without Celery:**

Run manually or schedule with cron:

```bash
# manually
python manage.py compute_aggregations

# via cron — runs every hour
0 * * * * cd /your/project && python manage.py compute_aggregations
```

---

## Celery Beat Setup

If you're using async mode, add the following to your `settings.py`:

```python
from celery.schedules import crontab

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_BEAT_SCHEDULE = {
    'compute-endpoint-summaries': {
        'task': 'profiler.tasks.run_aggregation',
        'schedule': crontab(minute=0),  # runs every hour
    },
}
```

Add `django_celery_beat` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_celery_beat',
    'profiler',
]
```

Create a `config/celery.py` file:

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

Update `config/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

Run migrations for Celery Beat:

```bash
python manage.py migrate
```

Then start the worker and scheduler:

```bash
# terminal 1
celery -A config worker --loglevel=info

# terminal 2
celery -A config beat --loglevel=info
```

Aggregation will now run automatically every hour.

---

## Regression Detection

After each aggregation window, the profiler automatically compares the current
window against the previous one for every route. It flags:

- Response time more than 2× the previous window average
- Error rate increase of more than 10%

Detected regressions are logged as warnings in your server logs.

**Optional webhook alerts (requires `django-api-profiler[webhook]`):**

```python
# settings.py
PROFILER = {
    "WEBHOOK_URL": "https://hooks.slack.com/services/xxx/yyy/zzz",
}
```

A POST request with regression details is fired to this URL whenever a
regression is detected. Works with Slack, Discord, or any webhook endpoint.

Example payload:

```json
{
    "type": "response_time",
    "route": "api/users/<int:pk>/",
    "previous_avg_ms": 120.5,
    "current_avg_ms": 890.3
}
```

---

## Configuration

All settings are optional. The profiler works out of the box with sensible defaults.

```python
# settings.py
PROFILER = {
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
```

| Setting | Default | Description |
|---------|---------|-------------|
| `ASYNC` | `False` | Enable Celery async metric ingestion |
| `SLOW_REQUEST_THRESHOLD_MS` | `1000` | Flag requests slower than this as slow |
| `AGGREGATION_WINDOW_MINUTES` | `60` | Size of each aggregation window |
| `IGNORED_PATHS` | `['/admin', '/static', '/favicon.ico']` | Paths to skip profiling |
| `N_PLUS_ONE_THRESHOLD` | `3` | Repeated query count to flag as N+1 |
| `SLOW_QUERY_THRESHOLD_MS` | `100` | Individual SQL query slow threshold |
| `REGRESSION_RESPONSE_TIME_FACTOR` | `2.0` | Flag if response time exceeds previous × this |
| `REGRESSION_ERROR_RATE_DELTA` | `0.1` | Flag if error rate increases by more than this |
| `WEBHOOK_URL` | `None` | Webhook URL for regression alerts |

---

## Architecture
HTTP Request
→ ApiProfilerMiddleware
→ ProfilingCursorWrapper (intercepts every SQL query)
→ build_metric_payload() (pure function, no side effects)
→ ASYNC=True  → Redis queue → Celery Worker → RequestMetric (PostgreSQL)
→ ASYNC=False → synchronous write → RequestMetric (PostgreSQL)
Celery Beat (every hour) — or management command
→ compute_endpoint_summaries()
→ EndpointSummary (PostgreSQL)
→ detect_regression()
→ logger.warning()
→ webhook POST (if WEBHOOK_URL configured)


---

## Admin Dashboard

Visit `/admin` after running migrations to access:

- **Request Metrics** — every request with color-coded response times
  (green/orange/red), filtering by method, status code, slow flag, exception flag
- **Endpoint Summaries** — aggregated statistics per route with avg, p95,
  error rates, and N+1 counts per time window
- **Exception Tracking** — complete error monitoring with exception type
  and message per request

---
