"""
HeatShield AI — Supervisor Monitoring Store

A lightweight, in-memory aggregation of completed assessments that
powers the supervisor monitoring dashboard endpoints.

Design principles:

- Stores only the minimum supervisory summary of an assessment
  (precaution level, alert counts, missing information) — never
  replaces the full assessment record.
- Bounded size: the oldest records are evicted once the cap is reached.
- Screening data only: no medical records, no personal identifiers
  beyond what the worker voluntarily supplied in their profile.
"""

from datetime import datetime, timezone
from threading import Lock


MAX_RECORDS = 200

_records: list[dict] = []
_lock = Lock()


def record_assessment(result: dict) -> dict:
    """
    Extract a supervisory summary from a completed HeatShield result
    and store it for the monitoring dashboard.
    """

    deterministic = result.get("deterministic_assessment") or {}
    alerts = result.get("safety_alerts") or {}
    weather = deterministic.get("weather_summary") or {}
    worker = deterministic.get("worker_summary") or {}

    record = {
        "id": f"assessment-{len(_records) + 1}-{datetime.now(timezone.utc).timestamp().hex}",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "location": result.get("location"),
        "language": result.get("language", "en"),
        "occupation": worker.get("occupation"),
        "workload": worker.get("workload"),
        "work_area": worker.get("work_area"),
        "assessment_status": deterministic.get("assessment_status"),
        "highest_priority": alerts.get("highest_priority", "none"),
        "alert_count": alerts.get("alert_count", 0),
        "priority_counts": alerts.get("counts", {}),
        "has_critical_precaution": bool(
            alerts.get("has_critical_precaution", False)
        ),
        "missing_information": deterministic.get("missing_information", []),
        "observed_temperature_c": weather.get("temperature_c"),
        "observed_humidity_percent": weather.get("humidity_percent"),
        "water_access": worker.get("water_access"),
        "shade_availability": worker.get("shade_availability"),
        "acclimatization": worker.get("acclimatization"),
    }

    with _lock:
        _records.append(record)
        if len(_records) > MAX_RECORDS:
            del _records[: len(_records) - MAX_RECORDS]

    return record


def list_records() -> list[dict]:
    """Return stored assessment summaries, newest first."""

    with _lock:
        return list(reversed(_records))


def clear_records() -> None:
    """Clear all stored records (useful for testing)."""

    with _lock:
        _records.clear()
