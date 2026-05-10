from celery import shared_task
from .services import compute_endpoint_summaries


@shared_task
def run_aggregation():
    count = compute_endpoint_summaries()
    return f"Computed summaries for {count} endpoint(s)."