"""
HeatShield AI — In-memory assessment record store

Stores completed assessment summaries so the supervisor monitoring
dashboard can aggregate cohort-level risk without an external
database. Records are kept in process memory with a bounded size;
production deployments should replace this module with a durable
store (e.g. DynamoDB) behind the same interface.
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from app.engine.monitor import normalize_assessment_record

_MAX_RECORDS = 1000

_lock = threading.Lock()
_records: list[dict[str, Any]] = []


def save_assessment(
    result: dict,
    language: str = "en",
    worker_name: str | None = None,
) -> dict[str, Any]:
    """
    Normalize one pipeline result and store its summary.

    Returns the stored summary (including ``assessment_id``), or
    ``None`` when the result cannot be normalized.
    """
    record = {
        "assessment_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "language": language,
        "worker_name": worker_name,
        "result": result,
    }

    summary = normalize_assessment_record(record)

    if summary is None:
        return None  # type: ignore[return-value]

    summary["assessment_id"] = record["assessment_id"]

    with _lock:
        _records.append(summary)
        if len(_records) > _MAX_RECORDS:
            del _records[: len(_records) - _MAX_RECORDS]

    return summary


def list_records(limit: int | None = None) -> list[dict[str, Any]]:
    """Return stored summaries, newest first."""
    with _lock:
        snapshot = list(reversed(_records))

    return snapshot[:limit] if limit else snapshot


def clear_records() -> int:
    """Remove all stored records; returns the number removed."""
    with _lock:
        count = len(_records)
        _records.clear()
    return count
