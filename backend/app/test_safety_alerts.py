"""
HeatShield AI — Proactive Safety Alerts Engine Test

Runs entirely offline (no AWS Bedrock, no network) by feeding
mock weather observations into the deterministic assessment
engine, then generating proactive safety alerts.

Covers the critical, heightened, advisory and no-alert tiers.
"""

import json

from app.engine.heat_assessment import assess_heat_exposure
from app.engine.safety_alerts import generate_safety_alerts


def _mock_weather(
    temperature_c,
    humidity_percent,
    wind_speed_kmh=8,
    apparent_temperature_c=None,
):
    """Build a weather payload shaped like the Open-Meteo tool output."""
    return {
        "success": True,
        "source": "Open-Meteo (mock)",
        "location": {
            "name": "Vadodara",
            "country": "India",
            "latitude": 22.31,
            "longitude": 73.18,
            "timezone": "Asia/Kolkata",
        },
        "current_weather": {
            "temperature_c": temperature_c,
            "humidity_percent": humidity_percent,
            "apparent_temperature_c": apparent_temperature_c,
            "wind_speed_kmh": wind_speed_kmh,
            "precipitation_mm": 0,
            "cloud_cover_percent": 10,
            "observed_at": "2026-11-02T12:00",
        },
        "hourly_forecast": [],
        "units": {},
        "data_note": "Mock weather for offline testing.",
    }


def _worker(**overrides):
    base = {
        "occupation": "Construction worker",
        "workload": "heavy",
        "shift_hours": 8,
        "direct_sunlight": True,
        "shade_availability": "partial",
        "water_access": True,
        "acclimatization": "not_acclimatized",
        "ppe_items": ["Safety helmet", "Safety boots"],
        "continuous_exposure_minutes": 120,
        "break_frequency_minutes": None,
        "work_area": "Outdoor construction site",
    }
    base.update(overrides)
    return base


def _run(temperature_c, humidity_percent, worker, language=None):
    weather = _mock_weather(temperature_c, humidity_percent)
    assessment = assess_heat_exposure(
        weather=weather,
        worker=worker,
    )
    assert assessment["success"], assessment
    if language is not None:
        return generate_safety_alerts(
            assessment=assessment, worker=worker, language=language,
        )
    return generate_safety_alerts(assessment=assessment, worker=worker)


def test_critical_compound():
    """Extreme heat + aggravating exposure factors -> critical + emergency."""
    worker = _worker(water_access=False)
    alerts = _run(41.5, 64, worker)

    assert alerts["success"], alerts
    assert alerts["has_critical_precaution"] is True
    assert alerts["highest_priority"] == "critical_precaution"
    assert alerts["emergency_guidance"], "Emergency guidance must be present"
    assert alerts["counts"]["critical_precaution"] >= 1

    ids = {a["id"] for a in alerts["alerts"]}
    # The combined compound alert should fire ...
    assert "extreme_heat_with_exposure_compound" in ids
    # ... and the standalone extreme environmental heat alert is suppressed.
    assert "extreme_environmental_heat" not in ids
    # Drinking water unavailable is independently critical.
    assert "drinking_water_unavailable" in ids

    # No numerical risk score or occupational risk category.
    blob = json.dumps(alerts)
    assert "risk_score" not in blob
    assert "occupational_risk_category" not in blob
    print("[PASS] critical_compound")


def test_heightened_environmental():
    """35-39.9 degC + high humidity -> heightened, no critical."""
    worker = _worker(water_access=True)
    alerts = _run(36.0, 75, worker)

    assert alerts["success"], alerts
    assert alerts["has_critical_precaution"] is False
    assert alerts["highest_priority"] == "heightened_precaution"

    ids = {a["id"] for a in alerts["alerts"]}
    assert "high_environmental_temperature" in ids
    assert "elevated_humidity_reduced_cooling" in ids
    print("[PASS] heightened_environmental")


def test_advisory_tier():
    """Warm, elevated humidity, very heavy workload -> advisory alerts."""
    worker = _worker(
        workload="very_heavy",
        shade_availability="none",
        acclimatization="acclimatized",
        break_frequency_minutes=45,
    )
    alerts = _run(31.0, 62, worker)

    assert alerts["success"], alerts
    assert alerts["has_critical_precaution"] is False

    ids = {a["id"] for a in alerts["alerts"]}
    assert "elevated_humidity" in ids
    assert "very_heavy_workload" in ids
    assert "no_shade_direct_sun" in ids
    print("[PASS] advisory_tier")


def test_no_alerts():
    """Mild conditions and a complete profile -> no alerts."""
    worker = _worker(
        workload="light",
        direct_sunlight=False,
        shade_availability="full",
        water_access=True,
        acclimatization="acclimatized",
        continuous_exposure_minutes=60,
        break_frequency_minutes=30,
    )
    alerts = _run(24.0, 40, worker)

    assert alerts["success"], alerts
    assert alerts["alert_count"] == 0
    assert alerts["highest_priority"] == "none"
    assert alerts["emergency_guidance"] == ""
    print("[PASS] no_alerts")


def test_limits_principles():
    """Every alert carries transparent triggers and a stated basis."""
    worker = _worker(water_access=False)
    alerts = _run(42.0, 68, worker)

    assert alerts["success"], alerts
    assert alerts["limitations"], "Limitations must be documented"
    for alert in alerts["alerts"]:
        assert alert["triggers"], f"Alert {alert['id']} has no triggers"
        assert alert["basis"] in (
            "environmental_observation",
            "worker_exposure_factor",
            "combined",
        )
    print("[PASS] limits_principles")


def _contains_script(text, start, end):
    """True if any character of text is in the given Unicode code-point range."""
    return any(start <= ord(ch) <= end for ch in text)


def test_localization_hindi():
    """Hindi output contains Devanagari text and no English leakage."""
    worker = _worker(water_access=False)
    alerts = _run(41.5, 64, worker, language="hi")

    assert alerts["success"], alerts
    assert alerts["language"] == "hi"
    # Devanagari block: U+0900 .. U+097F
    assert _contains_script(alerts["emergency_guidance"], 0x0900, 0x097F)

    titles = {a["id"]: a["title"] for a in alerts["alerts"]}
    assert _contains_script(titles["drinking_water_unavailable"], 0x0900, 0x097F)
    assert "unavailable" not in titles["drinking_water_unavailable"].lower()

    dw = next(a for a in alerts["alerts"] if a["id"] == "drinking_water_unavailable")
    assert _contains_script(dw["triggers"][0], 0x0900, 0x097F)
    print("[PASS] localization_hindi")


def test_localization_gujarati():
    """Gujarati output contains Gujarati script and no English leakage."""
    worker = _worker()
    alerts = _run(36.0, 75, worker, language="gu")

    assert alerts["success"], alerts
    assert alerts["language"] == "gu"
    # Gujarati block: U+0A80 .. U+0AFF
    assert _contains_script(alerts["summary"], 0x0A80, 0x0AFF)

    ht = next(a for a in alerts["alerts"] if a["id"] == "high_environmental_temperature")
    assert _contains_script(ht["title"], 0x0A80, 0x0AFF)
    assert "temperature" not in ht["title"].lower()
    print("[PASS] localization_gujarati")


def test_unsupported_language_fallback():
    """An unknown language code falls back to English."""
    worker = _worker(water_access=False)
    alerts = _run(41.5, 64, worker, language="fr")

    assert alerts["success"], alerts
    assert alerts["language"] == "en"
    dw = next(a for a in alerts["alerts"] if a["id"] == "drinking_water_unavailable")
    assert "unavailable" in dw["title"].lower()
    print("[PASS] unsupported_language_fallback")


def main():
    print("\nHEATSHIELD AI — PROACTIVE SAFETY ALERTS TEST")
    print("=" * 60)

    test_critical_compound()
    test_heightened_environmental()
    test_advisory_tier()
    test_no_alerts()
    test_limits_principles()
    test_localization_hindi()
    test_localization_gujarati()
    test_unsupported_language_fallback()

    print("\n" + "=" * 60)
    print("ALL SAFETY ALERTS TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
