from datetime import datetime
from typing import Any


def _is_valid_number(value: Any) -> bool:
    """Check whether a value is a valid numeric observation."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def _normalize_weather(weather: dict) -> dict:
    """
    Normalize weather fields from either the existing normalized
    schema or the raw Open-Meteo response.

    Supported schemas:
        current_weather.temperature_c
        current.temperature_2m
    """

    raw_current = (
        weather.get("current_weather")
        or weather.get("current")
        or {}
    )

    current = {
        **raw_current,

        "temperature_c": raw_current.get(
            "temperature_c",
            raw_current.get("temperature_2m"),
        ),

        "humidity_percent": raw_current.get(
            "humidity_percent",
            raw_current.get("relative_humidity_2m"),
        ),

        "apparent_temperature_c": raw_current.get(
            "apparent_temperature_c",
            raw_current.get("apparent_temperature"),
        ),

        "wind_speed_kmh": raw_current.get(
            "wind_speed_kmh",
            raw_current.get("wind_speed_10m"),
        ),

        "precipitation_mm": raw_current.get(
            "precipitation_mm",
            raw_current.get("precipitation"),
        ),

        "cloud_cover_percent": raw_current.get(
            "cloud_cover_percent",
            raw_current.get("cloud_cover"),
        ),
    }

    return {
        "current": current,
        "location": weather.get("location", {}),
        "source": weather.get("source", "Unknown"),
    }


def _validate_wbgt(
    measured_wbgt_c: float | None,
    wbgt_source: str | None,
    wbgt_measured_at: str | None,
) -> dict:
    """
    Validate the presence and basic format of optional WBGT metadata.

    This does not verify instrument calibration, measurement accuracy,
    or the authenticity of the measurement source.
    """

    if measured_wbgt_c is None:
        return {
            "available": False,
            "value_c": None,
            "source": None,
            "measured_at": None,
            "validation_status": "not_provided",
        }

    if not _is_valid_number(measured_wbgt_c):
        return {
            "available": False,
            "value_c": None,
            "source": None,
            "measured_at": None,
            "validation_status": "invalid_value",
        }

    if not -10 <= measured_wbgt_c <= 60:
        return {
            "available": False,
            "value_c": None,
            "source": None,
            "measured_at": None,
            "validation_status": "value_out_of_supported_range",
        }

    if not isinstance(wbgt_source, str) or not wbgt_source.strip():
        return {
            "available": False,
            "value_c": None,
            "source": None,
            "measured_at": None,
            "validation_status": "source_missing",
        }

    if not isinstance(wbgt_measured_at, str):
        return {
            "available": False,
            "value_c": None,
            "source": None,
            "measured_at": None,
            "validation_status": "measurement_timestamp_missing",
        }

    try:
        datetime.fromisoformat(
            wbgt_measured_at.replace("Z", "+00:00")
        )
    except ValueError:
        return {
            "available": False,
            "value_c": None,
            "source": None,
            "measured_at": None,
            "validation_status": "invalid_timestamp",
        }

    return {
        "available": True,
        "value_c": float(measured_wbgt_c),
        "source": wbgt_source.strip(),
        "measured_at": wbgt_measured_at,
        "validation_status": "metadata_format_valid",
    }


def assess_heat_exposure(
    weather: dict,
    worker: dict,
    measured_wbgt_c: float | None = None,
    wbgt_source: str | None = None,
    wbgt_measured_at: str | None = None,
) -> dict:
    """
    Deterministic environmental and occupational exposure screening.

    Important:
        - Does not diagnose heat-related illness.
        - Does not calculate an unsupported occupational risk score.
        - Does not assign an occupational risk category.
        - Does not treat apparent temperature as WBGT.
        - Does not invent work-rest schedules.
        - Uses actual worksite WBGT only when measurement metadata
          is supplied and passes basic format checks.
    """

    concerns = []
    controls = []
    missing_information = []
    limitations = []

    # ------------------------------------------------
    # 1. Validate input
    # ------------------------------------------------

    if not isinstance(weather, dict) or not weather.get("success"):
        return {
            "success": False,
            "assessment_status": "incomplete",
            "error": "Valid weather data is required.",
        }

    if not isinstance(worker, dict):
        return {
            "success": False,
            "assessment_status": "incomplete",
            "error": "A valid worker profile is required.",
        }

    normalized = _normalize_weather(weather)

    current = normalized["current"]
    location = normalized["location"]

    if not current:
        return {
            "success": False,
            "assessment_status": "incomplete",
            "error": "Current weather observations are missing.",
        }

    # ------------------------------------------------
    # 2. Validate weather observations
    # ------------------------------------------------

    required_weather = [
        "temperature_c",
        "humidity_percent",
        "wind_speed_kmh",
    ]

    for field in required_weather:
        value = current.get(field)

        if not _is_valid_number(value):
            missing_information.append(f"weather.{field}")

    # ------------------------------------------------
    # 3. Validate worker profile
    # ------------------------------------------------

    required_worker = [
        "occupation",
        "workload",
        "shift_hours",
        "direct_sunlight",
        "shade_availability",
        "water_access",
        "acclimatization",
        "ppe_items",
    ]

    for field in required_worker:
        if worker.get(field) is None:
            missing_information.append(f"worker.{field}")

    optional_but_important = [
        "continuous_exposure_minutes",
        "break_frequency_minutes",
        "work_area",
    ]

    for field in optional_but_important:
        if worker.get(field) is None:
            missing_information.append(f"worker.{field}")

    # ------------------------------------------------
    # 4. Identify environmental observations
    # ------------------------------------------------

    temperature = current.get("temperature_c")
    humidity = current.get("humidity_percent")
    apparent_temperature = current.get(
        "apparent_temperature_c"
    )
    wind_speed = current.get("wind_speed_kmh")

    if (
        _is_valid_number(temperature)
        and _is_valid_number(humidity)
    ):
        if temperature >= 35:
            concerns.append({
                "factor": "high_environmental_temperature",
                "observation": temperature,
                "unit": "°C",
                "description": (
                    "The reported environmental temperature "
                    "is elevated."
                ),
            })

        if humidity >= 60:
            concerns.append({
                "factor": "elevated_relative_humidity",
                "observation": humidity,
                "unit": "%",
                "description": (
                    "Elevated humidity can reduce the effectiveness "
                    "of evaporative cooling."
                ),
            })

    if _is_valid_number(wind_speed) and wind_speed < 5:
        concerns.append({
            "factor": "low_wind_speed",
            "observation": wind_speed,
            "unit": "km/h",
            "description": (
                "Low wind speed may reduce environmental air movement."
            ),
        })

    # ------------------------------------------------
    # 5. Identify worker exposure factors
    # ------------------------------------------------

    workload = worker.get("workload")

    if workload in ("heavy", "very_heavy"):
        concerns.append({
            "factor": "high_physical_workload",
            "observation": workload,
            "description": (
                "Heavy physical activity can increase internal "
                "heat production."
            ),
        })

        controls.append(
            "Review task intensity and opportunities for recovery."
        )

    if worker.get("direct_sunlight") is True:
        concerns.append({
            "factor": "direct_sunlight",
            "observation": True,
            "description": (
                "Direct sunlight increases radiant heat exposure."
            ),
        })

    shade = worker.get("shade_availability")

    if shade == "none":
        concerns.append({
            "factor": "no_shade_available",
            "observation": shade,
            "description": (
                "No shade has been reported at the worksite."
            ),
        })

    elif shade == "partial":
        concerns.append({
            "factor": "partial_shade_available",
            "observation": shade,
            "description": (
                "Shade is available only in some areas."
            ),
        })

    if worker.get("water_access") is False:
        concerns.append({
            "factor": "drinking_water_unavailable",
            "observation": False,
            "description": (
                "Drinking water access has not been reported "
                "as available."
            ),
        })

    if worker.get("acclimatization") == "not_acclimatized":
        concerns.append({
            "factor": "not_acclimatized",
            "observation": "not_acclimatized",
            "description": (
                "The worker has not been acclimatized to the "
                "current heat exposure conditions."
            ),
        })

    ppe_items = worker.get("ppe_items", [])

    if ppe_items:
        concerns.append({
            "factor": "personal_protective_equipment",
            "observation": ppe_items,
            "description": (
                "Protective clothing and equipment may influence "
                "heat dissipation. Their thermal characteristics "
                "need to be reviewed."
            ),
        })

    # ------------------------------------------------
    # 6. Generate deterministic control suggestions
    # ------------------------------------------------

    if worker.get("direct_sunlight") is True or shade in (
        "none",
        "partial",
    ):
        controls.append(
            "Provide accessible shaded or cooled recovery areas."
        )

    if worker.get("water_access") is True:
        controls.append(
            "Maintain access to drinking water throughout the shift."
        )

    elif worker.get("water_access") is False:
        controls.append(
            "Arrange accessible drinking water at the worksite."
        )

    if worker.get("acclimatization") == "not_acclimatized":
        controls.append(
            "Apply an appropriate heat-acclimatization programme "
            "under occupational safety guidance."
        )

    if ppe_items:
        controls.append(
            "Review PPE suitability and thermal burden with "
            "the occupational safety team."
        )

    if worker.get("break_frequency_minutes") is None:
        controls.append(
            "Confirm the actual recovery-break frequency and "
            "review an appropriate work-rest schedule using "
            "validated occupational heat guidance."
        )

    if worker.get("continuous_exposure_minutes") is None:
        controls.append(
            "Record continuous exposure duration for the worker."
        )

    if not controls:
        controls.append(
            "Continue monitoring environmental conditions and "
            "maintain established workplace heat-safety controls."
        )

    # ------------------------------------------------
    # 7. Validate optional WBGT measurement
    # ------------------------------------------------

    wbgt = _validate_wbgt(
        measured_wbgt_c=measured_wbgt_c,
        wbgt_source=wbgt_source,
        wbgt_measured_at=wbgt_measured_at,
    )

    # ------------------------------------------------
    # 8. Determine assessment completeness
    # ------------------------------------------------

    if missing_information:
        assessment_status = "incomplete"

    elif wbgt["available"]:
        assessment_status = "wbgt_requires_professional_review"

    else:
        assessment_status = "screening_only"

    # ------------------------------------------------
    # 9. Document assessment limitations
    # ------------------------------------------------

    limitations.extend([
        "This assessment is an informational screening tool "
        "and is not a medical diagnosis.",

        "Weather-station observations may differ from actual "
        "worksite environmental conditions.",

        "Apparent temperature is not measured Wet Bulb Globe "
        "Temperature (WBGT).",

        "A complete occupational heat assessment requires "
        "appropriate worksite measurements and professional "
        "interpretation.",

        "Workload, clothing, PPE, radiant heat, exposure duration "
        "and recovery arrangements influence occupational heat "
        "exposure.",

        "This engine does not independently verify WBGT instrument "
        "calibration or measurement authenticity.",
    ])

    if not wbgt["available"]:
        limitations.append(
            "No validated worksite WBGT measurement is available "
            "for this assessment."
        )

    # ------------------------------------------------
    # 10. Build weather summary
    # ------------------------------------------------

    weather_summary = {
        "location": location.get("name", "Unknown"),
        "country": location.get("country", "Unknown"),
        "temperature_c": temperature,
        "humidity_percent": humidity,
        "apparent_temperature_c": apparent_temperature,
        "wind_speed_kmh": wind_speed,
        "precipitation_mm": current.get("precipitation_mm"),
        "cloud_cover_percent": current.get(
            "cloud_cover_percent"
        ),
        "timestamp": current.get("time"),
        "source": normalized["source"],
        "data_note": (
            "Environmental weather observations only. "
            "Apparent temperature must not be interpreted "
            "as measured WBGT."
        ),
    }

    # ------------------------------------------------
    # 11. Build worker summary
    # ------------------------------------------------

    worker_summary = {
        "occupation": worker.get("occupation"),
        "workload": worker.get("workload"),
        "shift_hours": worker.get("shift_hours"),
        "direct_sunlight": worker.get("direct_sunlight"),
        "shade_availability": worker.get("shade_availability"),
        "water_access": worker.get("water_access"),
        "acclimatization": worker.get("acclimatization"),
        "ppe_items": ppe_items,
        "continuous_exposure_minutes": worker.get(
            "continuous_exposure_minutes"
        ),
        "break_frequency_minutes": worker.get(
            "break_frequency_minutes"
        ),
        "work_area": worker.get("work_area"),
    }

    # ------------------------------------------------
    # 12. Final deterministic assessment
    # ------------------------------------------------

    return {
        "success": True,

        "assessment_status": assessment_status,

        # No unsupported occupational risk classification.
        "occupational_risk_category": "not_assigned",

        "weather_summary": weather_summary,

        "worker_summary": worker_summary,

        "exposure_concerns": concerns,

        "recommended_controls": controls,

        "missing_information": missing_information,

        "wbgt_measurement": wbgt,

        "assessment_metadata": {
            "engine": "HeatShield AI Deterministic Assessment Engine",
            "assessment_type": "environmental_and_worker_exposure_screening",
            "risk_score_generated": False,
            "occupational_risk_category_assigned": False,
            "medical_diagnosis_generated": False,
        },

        "limitations": limitations,
    }