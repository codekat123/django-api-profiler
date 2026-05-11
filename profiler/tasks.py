from celery import shared_task
from .services import (
    compute_endpoint_summaries,
    save_metric_payload
)

@shared_task
def run_aggregation() -> str:
    count = compute_endpoint_summaries()
    return f"Computed summaries for {count} endpoint(s)."


@shared_task
def ingest_request_metric(payload: dict) -> None:
    save_metric_payload(payload)
    