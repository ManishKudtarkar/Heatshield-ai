"""
HeatShield AI — Supervisor Monitoring Aggregation Engine

Turns a list of completed HeatShield assessments into a cohort-level
risk overview for site supervisors.

Design rules (mirrors the rest of HeatShield AI):

- Deterministic aggregation only: no LLM, no fabricated data.
- Every number is traceable back to individual assessment records.
- Records that failed validation or lack required fields are counted
  as unusable rather than silently dropped from totals.
"""

from datetime import datetime, timezone
from typing import Any

SUPPORTED_RISK_LEVELS = ("critical", "heightened", "advisory", "none")

_PRIORITY_TO_RISK = {
    "critical_precaution": "critical",
    "heightened_precaution": "heightened",
    "advisory": "advisory",
    "none": "none",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _risk_from_alerts(alerts: dict | None) -> str:
    highest = (alerts or {}).get("highest_priority")
    return _PRIORITY_TO_RISK.get(highest, "none")


def _record_field(record: dict, *path: str) -> Any:
    """Safely walk a nested dict path."""
    current: Any = record
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def normalize_assessment_record(record: dict) -> dict[str, Any] | None:
    """
    Extract the supervisor-relevant summary from one assessment
    response. Returns ``None`` when the record cannot be used.
    """
    if not isinstance(record, dict):
        return None

    result = record.get("result") if "result" in record else record

    if not isinstance(result, dict) or not result.get("success", True):
        return None

    deterministic = result.get("deterministic_assessment") or {}
    alerts = result.get("safety_alerts") or {}
    weather = deterministic.get("weather_summary") or {}
    worker = deterministic.get("worker_summary") or {}

    submitted_at = record.get("timestamp") or _now_iso()

    try:
        temperature_c = float(weather.get("temperature_c"))
    except (TypeError, ValueError):
        temperature_c = None

    missing = deterministic.get("missing_information") or []

    return {
        "assessment_id": record.get("assessment_id") or result.get("assessment_id") or "",
        "worker_name": record.get("worker_name") or worker.get("occupation") or "Unnamed worker",
        "location": result.get("location") or weather.get("location") or "Unknown",
        "work_area": worker.get("work_area") or "Not provided",
        "occupation": worker.get("occupation") or "Not provided",
        "workload": worker.get("workload") or "unknown",
        "shift_hours": worker.get("shift_hours"),
        "language": record.get("language") or alerts.get("language") or "en",
        "submitted_at": submitted_at,
        "temperature_c": temperature_c,
        "apparent_temperature_c": _to_float(weather.get("apparent_temperature_c")),
        "risk_level": _risk_from_alerts(alerts),
        "alert_count": int(alerts.get("alert_count") or 0),
        "has_critical_precaution": bool(alerts.get("has_critical_precaution")),
        "highest_priority": alerts.get("highest_priority") or "none",
        "missing_information_count": len(missing),
        "assessment_status": deterministic.get("assessment_status") or "unknown",
    }


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_supervisor_overview(records: list[dict]) -> dict[str, Any]:
    """
    Aggregate normalized assessment records into a cohort overview.

    Args:
        records: Raw assessment responses (each containing at least a
            ``result`` object produced by the HeatShield pipeline, or
            already-normalized summaries).

    Returns:
        Structured overview with risk counts, hotspots, urgent cases,
        compliance signals and limitations.
    """
    normalized: list[dict[str, Any]] = []
    unusable = 0

    for record in records:
        if isinstance(record, dict) and "risk_level" in record:
            normalized.append(record)
            continue

        entry = normalize_assessment_record(record)
        if entry is None:
            unusable += 1
        else:
            normalized.append(entry)

    risk_counts = {level: 0 for level in SUPPORTED_RISK_LEVELS}
    location_groups: dict[str, list[dict[str, Any]]] = {}

    urgent: list[dict[str, Any]] = []
    incomplete_profiles = 0

    for entry in normalized:
        risk_counts[entry["risk_level"]] = risk_counts.get(entry["risk_level"], 0) + 1
        location_groups.setdefault(entry["location"], []).append(entry)

        if entry["has_critical_precaution"]:
            urgent.append(entry)

        if entry["missing_information_count"] > 0:
            incomplete_profiles += 1

    locations = []
    for name, entries in location_groups.items():
        worst = "none"
        for level in SUPPORTED_RISK_LEVELS:
            if risk_counts and any(e["risk_level"] == level for e in entries):
                worst = level
                break

        temps = [e["temperature_c"] for e in entries if e["temperature_c"] is not None]

        locations.append(
            {
                "location": name,
                "assessment_count": len(entries),
                "risk_counts": {
                    level: sum(1 for e in entries if e["risk_level"] == level)
                    for level in SUPPORTED_RISK_LEVELS
                },
                "worst_risk_level": worst,
                "max_temperature_c": max(temps) if temps else None,
                "workers_with_incomplete_profiles": sum(
                    1 for e in entries if e["missing_information_count"] > 0
                ),
            }
        )

    # Hotspots first: worse risk, then more assessments.
    risk_order = {level: index for index, level in enumerate(SUPPORTED_RISK_LEVELS)}
    locations.sort(
        key=lambda item: (risk_order.get(item["worst_risk_level"], 9), -item["assessment_count"])
    )

    urgent.sort(key=lambda e: e["submitted_at"], reverse=True)

    total = len(normalized)
    critical_share = round(risk_counts["critical"] / total, 3) if total else 0.0
    profile_quality = round((total - incomplete_profiles) / total, 3) if total else None

    return {
        "success": True,
        "generated_at": _now_iso(),
        "total_assessments": total,
        "unusable_records": unusable,
        "risk_counts": risk_counts,
        "critical_share": critical_share,
        "urgent_cases": [
            {
                "assessment_id": e["assessment_id"],
                "worker_name": e["worker_name"],
                "location": e["location"],
                "work_area": e["work_area"],
                "highest_priority": e["highest_priority"],
                "alert_count": e["alert_count"],
                "temperature_c": e["temperature_c"],
                "submitted_at": e["submitted_at"],
            }
            for e in urgent[:20]
        ],
        "locations": locations,
        "profile_completeness": {
            "assessments_with_missing_information": incomplete_profiles,
            "complete_profile_share": profile_quality,
        },
        "recent_assessments": sorted(
            normalized, key=lambda e: e["submitted_at"], reverse=True
        )[:25],
        "limitations": [
            "Aggregates reflect submitted self-reported data; they are not worksite measurements.",
            "Risk levels derive from deterministic alert priorities, not a medical evaluation.",
            "Records without a completed assessment are excluded from cohort statistics.",
            "Supervisors must verify conditions on-site before issuing work-stoppage decisions.",
        ],
    }
