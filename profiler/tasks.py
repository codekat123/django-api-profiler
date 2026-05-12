from celery import shared_task
from .services import (
    compute_endpoint_summaries,
    save_metric_payload
)
import logging
logger = logging.getLogger(__name__)

@shared_task
def run_aggregation() -> str:
    count = compute_endpoint_summaries()
    return f"Computed summaries for {count} endpoint(s)."


@shared_task
def ingest_request_metric(payload: dict) -> None:
    save_metric_payload(payload)


@shared_task
def fire_webhook(payload: dict) -> None:
    import requests
    from .conf import profiler_settings

    webhook_url = profiler_settings.WEBHOOK_URL

    try:
        requests.post(webhook_url,json=payload,timeout=5)
    except Exception as e:
        logger.error("failed to fire webhook: %s",str(e))