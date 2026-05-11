from ..conf import profiler_settings
import logging

logger = logging.getLogger(__name__)


def ingest_metric(payload: dict) -> None:
    use_async = profiler_settings.ASYNC

    if use_async:
        _ingest_async(payload)
    else:
        _ingest_sync(payload)




def _ingest_async(payload: dict) -> None:
    try:
        from ..tasks import ingest_request_metric
        ingest_request_metric.delay(payload)
    except Exception as e:
        logger.error(
            "Failed to queue metric asynchronously, falling back to sync. "
            "Error: %s",
            str(e),
        )
        _ingest_sync(payload)


def _ingest_sync(payload: dict) -> None:
    from ..services import save_metric_payload
    save_metric_payload(payload)