"""
HeatShield AI — Proactive Safety Alerts Engine

Generates deterministic, evidence-grounded precautionary
alerts from the validated weather observations and worker
exposure profile produced by the deterministic assessment
engine, localized into the worker's preferred language.

Supported languages: en (English), hi (Hindi), gu (Gujarati).

Design principles (mirrors the rest of HeatShield AI):

- No numerical heat-risk score is produced.
- No occupational heat-risk category is assigned
  (no LOW / MODERATE / HIGH / EXTREME labels).
- Apparent temperature is never used as an alert trigger
  because it is not measured WBGT and must not be used to
  infer occupational heat-stress risk.
- Every alert lists the specific observation(s) that
  triggered it, with the actual observed values.
- Alert priority describes the level of precaution warranted,
  not a risk classification:
      advisory              -> routine precautions
      heightened_precaution -> additional precautions
      critical_precaution  -> enhanced precautions and
                               close monitoring
- Emergency medical guidance is surfaced whenever a
  critical-precaution alert is present.
- Alerts are screening signals, not a medical diagnosis.
"""

from typing import Any


# --------------------------------------------------
# SUPPORTED LANGUAGES
# --------------------------------------------------

SUPPORTED_LANGUAGES = ("en", "hi", "gu")

_LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
}


def language_name(code: str) -> str:
    """Human-readable language name for a language code."""
    return _LANGUAGE_NAMES.get(code, "English")


# --------------------------------------------------
# PRIORITY ORDER
# --------------------------------------------------

_PRIORITY_RANK = {
    "advisory": 1,
    "heightened_precaution": 2,
    "critical_precaution": 3,
}


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def _is_valid_number(value: Any) -> bool:
    """True for real numeric observations (not bools or None)."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def _fmt(value: Any) -> str:
    """Format an observed value for a trigger description."""
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def _highest_priority(alerts: list[dict]) -> str:
    """Return the strongest alert priority present, or 'none'."""
    if not alerts:
        return "none"
    return max(
        alerts,
        key=lambda a: _PRIORITY_RANK.get(a["priority"], 0),
    )["priority"]


# --------------------------------------------------
# LOCALIZED STRING TABLES
# --------------------------------------------------
#
# Each alert definition uses {placeholder} tokens in its trigger
# templates that are filled with the observed values at runtime.

_STRINGS = {
    # =================================================
    # ENGLISH
    # =================================================
    "en": {
        "workload_labels": {
            "light": "Light",
            "moderate": "Moderate",
            "heavy": "Heavy",
            "very_heavy": "Very heavy",
            "unknown": "Unknown",
        },
        "emergency_guidance": (
            "If someone shows confusion, seizures, collapse, or "
            "loss of consciousness, seek immediate emergency "
            "medical assistance. Do not delay for an AI assessment."
        ),
        "no_alerts_summary": (
            "No precautionary alerts were triggered from the "
            "available observations."
        ),
        "summary_template": (
            "{count} active precaution alert(s): {critical} "
            "critical, {heightened} heightened, {advisory} advisory."
        ),
        "limitations": [
            "These alerts are precautionary screening signals, not "
            "an occupational heat-risk classification or a medical "
            "diagnosis.",
            "Environmental observations are weather-station data and "
            "may differ from actual worksite conditions.",
            "Apparent temperature is not used as a trigger and is not "
            "a substitute for measured Wet Bulb Globe Temperature "
            "(WBGT).",
            "No numerical heat-risk score is generated.",
        ],
        "alerts": {
            "extreme_environmental_heat": {
                "title": "Extreme environmental heat",
                "triggers": [
                    "Environmental air temperature is {temp} \u00b0C "
                    "(threshold: 40 \u00b0C)."
                ],
                "guidance": [
                    "Postpone non-essential outdoor physical work "
                    "during peak heat hours where possible.",
                    "Increase rest-break frequency and provide a "
                    "shaded or cooled recovery area.",
                    "Monitor workers closely for signs of heat-related "
                    "illness.",
                ],
            },
            "high_environmental_temperature": {
                "title": "High environmental temperature",
                "triggers": [
                    "Environmental air temperature is {temp} \u00b0C "
                    "(threshold: 35 \u00b0C)."
                ],
                "guidance": [
                    "Schedule strenuous outdoor tasks for cooler parts "
                    "of the day.",
                    "Ensure drinking water and shade are readily "
                    "available.",
                    "Encourage regular rest breaks out of direct sun.",
                ],
            },
            "elevated_humidity_reduced_cooling": {
                "title": "High humidity reducing cooling",
                "triggers": [
                    "Relative humidity is {humidity}% with air "
                    "temperature {temp} \u00b0C."
                ],
                "guidance": [
                    "High humidity reduces evaporative cooling; rely "
                    "more on shade, hydration and rest.",
                    "Reduce work intensity where practical and monitor "
                    "conditions.",
                ],
            },
            "elevated_humidity": {
                "title": "Elevated humidity",
                "triggers": [
                    "Relative humidity is {humidity}% with air "
                    "temperature {temp} \u00b0C."
                ],
                "guidance": [
                    "Be aware that humidity can reduce cooling "
                    "effectiveness; maintain hydration and shade "
                    "access.",
                ],
            },
            "low_wind_speed": {
                "title": "Low air movement",
                "triggers": [
                    "Wind speed is {wind} km/h with air temperature "
                    "{temp} \u00b0C."
                ],
                "guidance": [
                    "Low wind speed can reduce natural air movement; "
                    "ensure shade and ventilation at the worksite.",
                ],
            },
            "drinking_water_unavailable": {
                "title": "Drinking water unavailable",
                "triggers": [
                    "Drinking water access was reported as unavailable."
                ],
                "guidance": [
                    "Arrange accessible drinking water at the worksite "
                    "before work continues.",
                    "Provide frequent hydration opportunities.",
                ],
            },
            "not_acclimatized_heavy_outdoor_work": {
                "title": "Not acclimatized for heavy outdoor work",
                "triggers": [
                    "Worker is reported as not acclimatized.",
                    "Workload is reported as {workload}.",
                    "Direct sunlight exposure was reported.",
                ],
                "guidance": [
                    "Apply a gradual heat-acclimatization plan under "
                    "occupational safety guidance.",
                    "Reduce exposure duration and increase recovery "
                    "breaks until acclimatized.",
                ],
            },
            "very_heavy_workload": {
                "title": "Very heavy physical workload",
                "triggers": ["Workload was reported as very heavy."],
                "guidance": [
                    "Review task intensity and rotate tasks where "
                    "possible to limit sustained exertion.",
                ],
            },
            "extended_exposure_without_breaks": {
                "title": "Extended exposure without reported breaks",
                "triggers": [
                    "Continuous exposure reported as {minutes} minutes.",
                    "Recovery-break frequency was not provided.",
                ],
                "guidance": [
                    "Confirm the actual recovery-break frequency and "
                    "review an appropriate work-rest schedule using "
                    "validated occupational heat guidance.",
                ],
            },
            "no_shade_direct_sun": {
                "title": "No shade with direct sun",
                "triggers": [
                    "Shade availability was reported as none.",
                    "Direct sunlight exposure was reported.",
                ],
                "guidance": [
                    "Provide an accessible shaded or cooled recovery "
                    "area for breaks.",
                ],
            },
            "extreme_heat_with_exposure_compound": {
                "title": "Extreme heat compounded by exposure factors",
                "triggers": [
                    "Environmental air temperature is {temp} \u00b0C "
                    "(threshold: 40 \u00b0C)."
                ],
                "guidance": [
                    "Apply enhanced precautions: postpone or reduce "
                    "outdoor physical work, increase recovery breaks, "
                    "and ensure shade, cooling and drinking water are "
                    "immediately available.",
                    "Monitor workers closely for signs of heat-related "
                    "illness.",
                    "Escalate to a qualified occupational safety "
                    "professional where possible.",
                ],
            },
        },
        "aggravating": {
            "heavy_workload": "Workload is reported as {workload}.",
            "direct_sunlight": "Direct sunlight exposure was reported.",
            "not_acclimatized": (
                "Worker is reported as not acclimatized."
            ),
            "water_unavailable": (
                "Drinking water access was reported as unavailable."
            ),
        },
    },

    # =================================================
    # HINDI
    # =================================================
    "hi": {
        "workload_labels": {
            "light": "\u0939\u0932\u094d\u0915\u093e",
            "moderate": "\u092e\u0927\u094d\u092f\u092e",
            "heavy": "\u092d\u093e\u0930\u0940",
            "very_heavy": "\u092c\u0939\u0941\u0924 \u092d\u093e\u0930\u0940",
            "unknown": "\u0905\u091c\u094d\u091e\u093e\u0924",
        },
        "emergency_guidance": (
            "\u092f\u0926\u093f \u0915\u093f\u0938\u0940 \u0935\u094d\u092f\u0915\u094d\u0924\u093f "
            "\u092e\u0947\u0902 \u092d\u094d\u0930\u092e, \u0910\u0902\u0920\u0928, "
            "\u0917\u093f\u0930\u0928\u093e, \u092f\u093e \u091a\u0947\u0924\u0928\u093e "
            "\u0916\u094b\u0928\u0947 \u0915\u0947 \u0932\u0915\u094d\u0937\u0923 "
            "\u0926\u093f\u0916\u0947\u0902, \u0924\u094b \u0924\u0941\u0930\u0902\u0924 "
            "\u0906\u092a\u093e\u0924\u0915\u093e\u0932\u0940\u0928 \u091a\u093f\u0915\u093f\u0924\u094d\u0938\u093e "
            "\u0938\u0939\u093e\u092f\u0924\u093e \u092a\u094d\u0930\u093e\u092a\u094d\u0924 \u0915\u0930\u0947\u0902\u0964 "
            "AI \u092e\u0942\u0932\u094d\u092f\u093e\u0902\u0915\u0928 \u0915\u0947 \u0932\u093f\u090f "
            "\u0926\u0947\u0930\u0940 \u0928 \u0915\u0930\u0947\u0902\u0964"
        ),
        "no_alerts_summary": (
            "\u0909\u092a\u0932\u092c\u094d\u0927 \u0905\u0935\u0932\u094b\u0915\u0928\u094b\u0902 "
            "\u0938\u0947 \u0915\u094b\u0908 \u0938\u0924\u0930\u094d\u0915\u0924\u093e \u0905\u0932\u0930\u094d\u091f "
            "\u0938\u0915\u094d\u0930\u093f\u092f \u0928\u0939\u0940\u0902 \u0939\u0941\u0906\u0964"
        ),
        "summary_template": (
            "\u0938\u0915\u094d\u0930\u093f\u092f \u0938\u0924\u0930\u094d\u0915\u0924\u093e \u0905\u0932\u0930\u094d\u091f: "
            "{count} \u2014 {critical} \u0917\u0902\u092d\u0940\u0930, "
            "{heightened} \u0909\u091a\u094d\u091a, {advisory} \u0938\u093e\u092e\u093e\u0928\u094d\u092f\u0964"
        ),
        "limitations": [
            "\u092f\u0947 \u0905\u0932\u0930\u094d\u091f \u0938\u093e\u0935\u0927\u093e\u0928\u0940\u092a\u0942\u0930\u094d\u0935\u0915 "
            "\u091c\u093e\u0902\u091a \u0938\u0902\u0915\u0947\u0924 \u0939\u0948\u0902, \u0915\u093f\u0938\u0940 "
            "\u0935\u094d\u092f\u093e\u0935\u0938\u093e\u092f\u093f\u0915 \u090a\u0937\u094d\u092e\u093e-\u091c\u094b\u0916\u093f\u092e "
            "\u0935\u0930\u094d\u0917\u0940\u0915\u0930\u0923 \u092f\u093e \u091a\u093f\u0915\u093f\u0924\u094d\u0938\u093e "
            "\u0928\u093f\u0926\u093e\u0928 \u0915\u0947 \u0932\u093f\u090f \u0928\u0939\u0940\u0902 \u0939\u0948\u0902\u0964",
            "\u092a\u0930\u094d\u092f\u093e\u0935\u0930\u0923\u0940\u092f \u0905\u0935\u0932\u094b\u0915\u0928 "
            "\u092e\u094c\u0938\u092e-\u0938\u094d\u091f\u0947\u0936\u0928 \u0921\u0947\u091f\u093e \u0939\u0948\u0902 "
            "\u0914\u0930 \u0935\u093e\u0938\u094d\u0924\u0935\u093f\u0915 \u0915\u093e\u0930\u094d\u092f\u0938\u094d\u0925\u0932 "
            "\u092a\u0930\u093f\u0938\u094d\u0925\u093f\u0924\u093f\u092f\u094b\u0902 \u0938\u0947 \u092d\u093f\u0928\u094d\u0928 "
            "\u0939\u094b \u0938\u0915\u0924\u0947 \u0939\u0948\u0902\u0964",
            "\u092a\u094d\u0930\u0924\u094d\u092f\u0915\u094d\u0937 \u0924\u093e\u092a\u092e\u093e\u0928 \u0915\u094b "
            "\u091f\u094d\u0930\u093f\u0917\u0930 \u0915\u0947 \u0930\u0942\u092a \u092e\u0947\u0902 \u0909\u092a\u092f\u094b\u0917 "
            "\u0928\u0939\u0940\u0902 \u0915\u093f\u092f\u093e \u0917\u092f\u093e \u0939\u0948 \u0914\u0930 \u092f\u0939 "
            "\u092e\u093e\u092a\u093e \u0917\u092f\u093e \u0935\u0947\u091f \u092c\u0932\u094d\u092c \u0917\u094d\u0932\u094b\u092c "
            "\u0924\u093e\u092a\u092e\u093e\u0928 (WBGT) \u0915\u093e \u0935\u093f\u0915\u0932\u094d\u092a \u0928\u0939\u0940\u0902 \u0939\u0948\u0964",
            "\u0915\u094b\u0908 \u0938\u0902\u0916\u094d\u092f\u093e\u0924\u094d\u092e\u0915 \u090a\u0937\u094d\u092e\u093e-\u091c\u094b\u0916\u093f\u092e "
            "\u0938\u094d\u0915\u094b\u0930 \u0909\u0924\u094d\u092a\u0928\u094d\u0928 \u0928\u0939\u0940\u0902 \u0915\u093f\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964",
        ],
        "alerts": {
            "extreme_environmental_heat": {
                "title": "\u0905\u0924\u094d\u092f\u0927\u093f\u0915 \u092a\u0930\u094d\u092f\u093e\u0935\u0930\u0923\u0940\u092f \u0917\u0930\u094d\u092e\u0940",
                "triggers": [
                    "\u092a\u0930\u094d\u092f\u093e\u0935\u0930\u0923\u0940\u092f \u0935\u093e\u092f\u0941 \u0924\u093e\u092a\u092e\u093e\u0928 "
                    "{temp} \u00b0C \u0939\u0948 (\u0938\u0940\u092e\u093e: 40 \u00b0C)\u0964"
                ],
                "guidance": [
                    "\u091c\u0939\u093e\u0901 \u0938\u0902\u092d\u0935 \u0939\u094b, \u091a\u0930\u092e \u0917\u0930\u094d\u092e\u0940 "
                    "\u0915\u0947 \u0938\u092e\u092f \u0917\u0948\u0930-\u091c\u093c\u0930\u0942\u0930\u0940 \u092c\u093e\u0939\u0930\u0940 "
                    "\u0936\u093e\u0930\u0940\u0930\u093f\u0915 \u0915\u093e\u0930\u094d\u092f \u0938\u094d\u0925\u0917\u093f\u0924 \u0915\u0930\u0947\u0902\u0964",
                    "\u0935\u093f\u0936\u094d\u0930\u093e\u092e-\u0935\u093f\u0930\u093e\u092e \u0915\u0940 \u0906\u0935\u0943\u0924\u094d\u0924\u093f "
                    "\u092c\u0922\u093c\u093e\u090f\u0901 \u0914\u0930 \u091b\u093e\u092f\u093e\u0926\u093e\u0930 \u092f\u093e "
                    "\u0936\u0940\u0924\u0932 \u092a\u0941\u0928\u0930\u094d\u092a\u094d\u0930\u093e\u092a\u094d\u0924\u093f \u0915\u094d\u0937\u0947\u0924\u094d\u0930 "
                    "\u0909\u092a\u0932\u092c\u094d\u0927 \u0915\u0930\u093e\u090f\u0901\u0964",
                    "\u0936\u094d\u0930\u092e\u093f\u0915\u094b\u0902 \u0915\u094b \u090a\u0937\u094d\u092e\u093e-\u0938\u0902\u092c\u0927\u0940 "
                    "\u092c\u0940\u092e\u093e\u0930\u0940 \u0915\u0947 \u0938\u0902\u0915\u0947\u0924\u094b\u0902 \u0915\u0947 \u0932\u093f\u090f "
                    "\u0928\u093f\u0915\u091f \u0938\u0947 \u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u0930\u0916\u0947\u0902\u0964",
                ],
            },
            "high_environmental_temperature": {
                "title": "\u0909\u091a\u094d\u091a \u092a\u0930\u094d\u092f\u093e\u0935\u0930\u0923\u0940\u092f \u0924\u093e\u092a\u092e\u093e\u0928",
                "triggers": [
                    "\u092a\u0930\u094d\u092f\u093e\u0935\u0930\u0923\u0940\u092f \u0935\u093e\u092f\u0941 \u0924\u093e\u092a\u092e\u093e\u0928 "
                    "{temp} \u00b0C \u0939\u0948 (\u0938\u0940\u092e\u093e: 35 \u00b0C)\u0964"
                ],
                "guidance": [
                    "\u0915\u0920\u093f\u0928 \u092c\u093e\u0939\u0930\u0940 \u0915\u093e\u0930\u094d\u092f\u094b\u0902 \u0915\u094b "
                    "\u0926\u093f\u0928 \u0915\u0947 \u0920\u0902\u0921\u0947 \u0938\u092e\u092f \u092a\u0930 \u0928\u093f\u0930\u094d\u0927\u093e\u0930\u093f\u0924 "
                    "\u0915\u0930\u0947\u0902\u0964",
                    "\u0938\u0941\u0928\u093f\u0936\u094d\u091a\u093f\u0924 \u0915\u0930\u0947\u0902 \u0915\u093f \u092a\u0940\u0928\u0947 \u0915\u093e "
                    "\u092a\u093e\u0928\u0940 \u0914\u0930 \u091b\u093e\u092f\u093e \u0938\u0939\u091c \u0909\u092a\u0932\u092c\u094d\u0927 \u0939\u094b\u0964",
                    "\u0938\u0940\u0927\u0947 \u0927\u0942\u092a \u0938\u0947 \u092c\u093e\u0939\u0930 \u0928\u093f\u092f\u092e\u093f\u0924 "
                    "\u0935\u093f\u0936\u094d\u0930\u093e\u092e-\u0935\u093f\u0930\u093e\u092e \u0915\u0947 \u0932\u093f\u090f "
                    "\u092a\u094d\u0930\u094b\u0924\u094d\u0938\u093e\u0939\u093f\u0924 \u0915\u0930\u0947\u0902\u0964",
                ],
            },
            "elevated_humidity_reduced_cooling": {
                "title": "\u0909\u091a\u094d\u091a \u0906\u0930\u094d\u0926\u094d\u0930\u0924\u093e \u0938\u0947 \u0936\u0940\u0924\u0932\u0928 \u0915\u092e \u0939\u094b \u0930\u0939\u093e \u0939\u0948",
                "triggers": [
                    "\u0938\u093e\u092a\u0947\u0915\u094d\u0937 \u0906\u0930\u094d\u0926\u094d\u0930\u0924\u093e {humidity}% \u0939\u0948 "
                    "\u0914\u0930 \u0935\u093e\u092f\u0941 \u0924\u093e\u092a\u092e\u093e\u0928 {temp} \u00b0C \u0939\u0948\u0964"
                ],
                "guidance": [
                    "\u0909\u091a\u094d\u091a \u0906\u0930\u094d\u0926\u094d\u0930\u0924\u093e \u0935\u093e\u0937\u094d\u092a\u0940\u092f \u0936\u0940\u0924\u0932\u0928 "
                    "\u0915\u094b \u0915\u092e \u0915\u0930\u0924\u0940 \u0939\u0948; \u0905\u0927\u093f\u0915 \u091b\u093e\u092f\u093e, "
                    "\u091c\u0932\u092f\u094b\u091c\u0928 \u0914\u0930 \u0935\u093f\u0936\u094d\u0930\u093e\u092e \u092a\u0930 \u0928\u093f\u0930\u094d\u092d\u0930 "
                    "\u0930\u0939\u0947\u0902\u0964",
                    "\u091c\u0939\u093e\u0901 \u0935\u094d\u092f\u093e\u0935\u0939\u093e\u0930\u093f\u0915 \u0939\u094b \u0915\u093e\u0930\u094d\u092f "
                    "\u0924\u0940\u0935\u094d\u0930\u0924\u093e \u0915\u092e \u0915\u0930\u0947\u0902 \u0914\u0930 \u092a\u0930\u093f\u0938\u094d\u0925\u093f\u0924\u093f\u092f\u094b\u0902 "
                    "\u0915\u0940 \u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u0930\u0916\u0947\u0902\u0964",
                ],
            },
            "elevated_humidity": {
                "title": "\u092c\u0922\u093c\u0940 \u0939\u0941\u0908 \u0906\u0930\u094d\u0926\u094d\u0930\u0924\u093e",
                "triggers": [
                    "\u0938\u093e\u092a\u0947\u0915\u094d\u0937 \u0906\u0930\u094d\u0926\u094d\u0930\u0924\u093e {humidity}% \u0939\u0948 "
                    "\u0914\u0930 \u0935\u093e\u092f\u0941 \u0924\u093e\u092a\u092e\u093e\u0928 {temp} \u00b0C \u0939\u0948\u0964"
                ],
                "guidance": [
                    "\u0927\u094d\u092f\u093e\u0928 \u0930\u0916\u0947\u0902 \u0915\u093f \u0906\u0930\u094d\u0926\u094d\u0930\u0924\u093e "
                    "\u0936\u0940\u0924\u0932\u0928 \u0915\u0940 \u092a\u094d\u0930\u092d\u093e\u0935\u0936\u0940\u0932\u0924\u093e \u0915\u092e "
                    "\u0915\u0930 \u0938\u0915\u0924\u0940 \u0939\u0948; \u091c\u0932\u092f\u094b\u091c\u0928 \u0914\u0930 \u091b\u093e\u092f\u093e "
                    "\u0909\u092a\u0932\u092c\u094d\u0927\u0924\u093e \u092c\u0928\u093e\u090f \u0930\u0916\u0947\u0902\u0964",
                ],
            },
            "low_wind_speed": {
                "title": "\u0915\u092e \u0935\u093e\u092f\u0941 \u092a\u094d\u0930\u0935\u093e\u0939",
                "triggers": [
                    "\u0939\u0935\u093e \u0915\u0940 \u0917\u0924\u093f {wind} \u0915\u093f\u092e\u0940/\u0918\u0902\u091f\u093e \u0939\u0948 "
                    "\u0914\u0930 \u0935\u093e\u092f\u0941 \u0924\u093e\u092a\u092e\u093e\u0928 {temp} \u00b0C \u0939\u0948\u0964"
                ],
                "guidance": [
                    "\u0915\u092e \u0939\u0935\u093e \u0915\u0940 \u0917\u0924\u093f \u092a\u094d\u0930\u093e\u0915\u0943\u0924\u093f\u0915 \u0935\u093e\u092f\u0941 "
                    "\u092a\u094d\u0930\u0935\u093e\u0939 \u0915\u094b \u0915\u092e \u0915\u0930 \u0938\u0915\u0924\u0940 \u0939\u0948; "
                    "\u0915\u093e\u0930\u094d\u092f\u0938\u094d\u0925\u0932 \u092a\u0930 \u091b\u093e\u092f\u093e \u0914\u0930 \u0935\u093e\u092f\u0941-"
                    "\u0938\u0902\u091a\u093e\u0930 \u0938\u0941\u0928\u093f\u0936\u094d\u091a\u093f\u0924 \u0915\u0930\u0947\u0902\u0964",
                ],
            },
            "drinking_water_unavailable": {
                "title": "\u092a\u0940\u0928\u0947 \u0915\u093e \u092a\u093e\u0928\u0940 \u0905\u0928\u0941\u092a\u0932\u092c\u094d\u0927",
                "triggers": [
                    "\u092a\u0940\u0928\u0947 \u0915\u093e \u092a\u093e\u0928\u0940 \u0909\u092a\u0932\u092c\u094d\u0927 \u0928\u0939\u0940\u0902 "
                    "\u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964"
                ],
                "guidance": [
                    "\u0915\u093e\u0930\u094d\u092f \u091c\u093e\u0930\u0940 \u0930\u0916\u0928\u0947 \u0938\u0947 \u092a\u0939\u0932\u0947 "
                    "\u0915\u093e\u0930\u094d\u092f\u0938\u094d\u0925\u0932 \u092a\u0930 \u0938\u0941\u0932\u092d \u092a\u0940\u0928\u0947 \u0915\u093e "
                    "\u092a\u093e\u0928\u0940 \u0935\u094d\u092f\u0935\u0938\u094d\u0925\u093f\u0924 \u0915\u0930\u0947\u0902\u0964",
                    "\u092c\u093e\u0930-\u092c\u093e\u0930 \u091c\u0932\u092f\u094b\u091c\u0928 \u0915\u0947 \u0905\u0935\u0938\u0930 \u092a\u094d\u0930\u0926\u093e\u0928 "
                    "\u0915\u0930\u0947\u0902\u0964",
                ],
            },
            "not_acclimatized_heavy_outdoor_work": {
                "title": "\u092d\u093e\u0930\u0940 \u092c\u093e\u0939\u0930\u0940 \u0915\u093e\u0930\u094d\u092f \u0915\u0947 \u0932\u093f\u090f \u0905\u0928\u0941\u0915\u0942\u0932\u093f\u0924 \u0928\u0939\u0940\u0902",
                "triggers": [
                    "\u0936\u094d\u0930\u092e\u093f\u0915 \u0915\u094b \u090a\u0937\u094d\u092e\u093e-\u0905\u0928\u0941\u0915\u0942\u0932\u093f\u0924 "
                    "\u0928\u0939\u0940\u0902 \u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964",
                    "\u0915\u093e\u0930\u094d\u092f\u092d\u093e\u0930 {workload} \u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964",
                    "\u0938\u0940\u0927\u0940 \u0927\u0942\u092a \u092e\u0947\u0902 \u0915\u093e\u0930\u094d\u092f \u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964",
                ],
                "guidance": [
                    "\u0935\u094d\u092f\u093e\u0935\u0938\u093e\u092f\u093f\u0915 \u0938\u0941\u0930\u0915\u094d\u0937\u093e \u092e\u093e\u0930\u094d\u0917\u0926\u0930\u094d\u0936\u0928 "
                    "\u092e\u0947\u0902 \u0915\u094d\u0930\u092e\u093f\u0915 \u090a\u0937\u094d\u092e\u093e-\u0905\u0928\u0941\u0915\u0942\u0932\u0928 "
                    "\u092f\u094b\u091c\u0928\u093e \u0932\u093e\u0917\u0942 \u0915\u0930\u0947\u0902\u0964",
                    "\u0905\u0928\u0941\u0915\u0942\u0932\u093f\u0924 \u0939\u094b\u0928\u0947 \u0924\u0915 \u0905\u0935\u0927\u093f \u0915\u092e "
                    "\u0915\u0930\u0947\u0902 \u0914\u0930 \u092a\u0941\u0928\u0930\u094d\u092a\u094d\u0930\u093e\u092a\u094d\u0924\u093f \u0935\u093f\u0936\u094d\u0930\u093e\u092e "
                    "\u092c\u0922\u093c\u093e\u090f\u0901\u0964",
                ],
            },
            "very_heavy_workload": {
                "title": "\u0905\u0924\u094d\u092f\u0902\u0924 \u092d\u093e\u0930\u0940 \u0936\u093e\u0930\u0940\u0930\u093f\u0915 \u0915\u093e\u0930\u094d\u092f\u092d\u093e\u0930",
                "triggers": [
                    "\u0915\u093e\u0930\u094d\u092f\u092d\u093e\u0930 \u0905\u0924\u094d\u092f\u0902\u0924 \u092d\u093e\u0930\u0940 "
                    "\u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964"
                ],
                "guidance": [
                    "\u0915\u093e\u0930\u094d\u092f \u0924\u0940\u0935\u094d\u0930\u0924\u093e \u0938\u092e\u0940\u0915\u094d\u0937\u093f\u0924 "
                    "\u0915\u0930\u0947\u0902 \u0914\u0930 \u0928\u093f\u0930\u0902\u0924\u0930 \u092a\u0930\u093f\u0936\u094d\u0930\u092e \u0938\u0940\u092e\u093f\u0924 "
                    "\u0915\u0930\u0928\u0947 \u0939\u0947\u0924\u0941 \u091c\u0939\u093e\u0901 \u0938\u0902\u092d\u0935 \u0939\u094b \u0915\u093e\u0930\u094d\u092f\u094b\u0902 "
                    "\u0915\u093e \u0906\u0935\u0930\u094d\u0924\u0928 \u0915\u0930\u0947\u0902\u0964",
                ],
            },
            "extended_exposure_without_breaks": {
                "title": "\u092c\u093f\u0928\u093e \u092c\u0924\u093e\u090f \u0917\u090f \u0935\u093f\u0930\u093e\u092e \u0915\u0947 \u0935\u093f\u0938\u094d\u0924\u093e\u0930\u093f\u0924 \u0905\u0928\u093e\u0935\u0930\u0923",
                "triggers": [
                    "\u0938\u0924\u0924 \u0905\u0928\u093e\u0935\u0930\u0923 {minutes} \u092e\u093f\u0928\u091f \u092c\u0924\u093e\u092f\u093e "
                    "\u0917\u092f\u093e \u0939\u0948\u0964",
                    "\u092a\u0941\u0928\u0930\u094d\u092a\u094d\u0930\u093e\u092a\u094d\u0924\u093f-\u0935\u093f\u0930\u093e\u092e \u0906\u0935\u0943\u0924\u094d\u0924\u093f "
                    "\u0928\u0939\u0940\u0902 \u0926\u0940 \u0917\u0908 \u0939\u0948\u0964",
                ],
                "guidance": [
                    "\u0935\u093e\u0938\u094d\u0924\u0935\u093f\u0915 \u092a\u0941\u0928\u0930\u094d\u092a\u094d\u0930\u093e\u092a\u094d\u0924\u093f-\u0935\u093f\u0930\u093e\u092e "
                    "\u0906\u0935\u0943\u0924\u094d\u0924\u093f \u0915\u0940 \u092a\u0941\u0937\u094d\u091f\u093f \u0915\u0930\u0947\u0902 \u0914\u0930 "
                    "\u092a\u094d\u0930\u092e\u093e\u0923\u093f\u0924 \u0935\u094d\u092f\u093e\u0935\u0938\u093e\u092f\u093f\u0915 \u090a\u0937\u094d\u092e\u093e "
                    "\u092e\u093e\u0930\u094d\u0917\u0926\u0930\u094d\u0936\u0928 \u0938\u0947 \u0909\u092a\u092f\u0941\u0915\u094d\u0924 \u0915\u093e\u0930\u094d\u092f-"
                    "\u0935\u093f\u0936\u094d\u0930\u093e\u092e \u0915\u093e\u0930\u094d\u092f\u0915\u094d\u0930\u092e \u0915\u0940 \u0938\u092e\u0940\u0915\u094d\u0937\u093e "
                    "\u0915\u0930\u0947\u0902\u0964",
                ],
            },
            "no_shade_direct_sun": {
                "title": "\u0938\u0940\u0927\u0940 \u0927\u0942\u092a \u0914\u0930 \u091b\u093e\u092f\u093e \u0905\u0928\u0941\u092a\u0932\u092c\u094d\u0927",
                "triggers": [
                    "\u091b\u093e\u092f\u093e \u0909\u092a\u0932\u092c\u094d\u0927\u0924\u093e \u0928\u0939\u0940\u0902 \u092c\u0924\u093e\u0908 "
                    "\u0917\u0908 \u0939\u0948\u0964",
                    "\u0938\u0940\u0927\u0940 \u0927\u0942\u092a \u092e\u0947\u0902 \u0915\u093e\u0930\u094d\u092f \u092c\u0924\u093e\u092f\u093e "
                    "\u0917\u092f\u093e \u0939\u0948\u0964",
                ],
                "guidance": [
                    "\u0935\u093f\u0936\u094d\u0930\u093e\u092e \u0915\u0947 \u0932\u093f\u090f \u0938\u0941\u0932\u092d \u091b\u093e\u092f\u093e\u0926\u093e\u0930 "
                    "\u092f\u093e \u0936\u0940\u0924\u0932 \u092a\u0941\u0928\u0930\u094d\u092a\u094d\u0930\u093e\u092a\u094d\u0924\u093f \u0915\u094d\u0937\u0947\u0924\u094d\u0930 "
                    "\u0909\u092a\u0932\u092c\u094d\u0927 \u0915\u0930\u093e\u090f\u0901\u0964",
                ],
            },
            "extreme_heat_with_exposure_compound": {
                "title": "\u0905\u0928\u093e\u0935\u0930\u0923 \u0915\u093e\u0930\u0915\u094b\u0902 \u0938\u0947 \u092c\u0922\u093c\u0940 \u0905\u0924\u094d\u092f\u0927\u093f\u0915 \u0917\u0930\u094d\u092e\u0940",
                "triggers": [
                    "\u092a\u0930\u094d\u092f\u093e\u0935\u0930\u0923\u0940\u092f \u0935\u093e\u092f\u0941 \u0924\u093e\u092a\u092e\u093e\u0928 "
                    "{temp} \u00b0C \u0939\u0948 (\u0938\u0940\u092e\u093e: 40 \u00b0C)\u0964"
                ],
                "guidance": [
                    "\u092c\u0922\u093c\u0940 \u0939\u0941\u0908 \u0938\u093e\u0935\u0927\u093e\u0928\u0940 \u0932\u093e\u0917\u0942 \u0915\u0930\u0947\u0902: "
                    "\u092c\u093e\u0939\u0930\u0940 \u0936\u093e\u0930\u0940\u0930\u093f\u0915 \u0915\u093e\u0930\u094d\u092f \u0938\u094d\u0925\u0917\u093f\u0924 "
                    "\u092f\u093e \u0918\u091f\u093e\u090f\u0901, \u092a\u0941\u0928\u0930\u094d\u092a\u094d\u0930\u093e\u092a\u094d\u0924\u093f \u0935\u093f\u0936\u094d\u0930\u093e\u092e "
                    "\u092c\u0922\u093c\u093e\u090f\u0901, \u0914\u0930 \u0938\u0941\u0928\u093f\u0936\u094d\u091a\u093f\u0924 \u0915\u0930\u0947\u0902 \u0915\u093f "
                    "\u091b\u093e\u092f\u093e, \u0936\u0940\u0924\u0932\u0928 \u0924\u0925\u093e \u092a\u0940\u0928\u0947 \u0915\u093e \u092a\u093e\u0928\u0940 "
                    "\u0924\u0924\u094d\u0915\u093e\u0932 \u0909\u092a\u0932\u092c\u094d\u0927 \u0939\u094b\u0964",
                    "\u0936\u094d\u0930\u092e\u093f\u0915\u094b\u0902 \u0915\u094b \u090a\u0937\u094d\u092e\u093e-\u0938\u0902\u092c\u0927\u0940 "
                    "\u092c\u0940\u092e\u093e\u0930\u0940 \u0915\u0947 \u0938\u0902\u0915\u0947\u0924\u094b\u0902 \u0915\u0947 \u0932\u093f\u090f "
                    "\u0928\u093f\u0915\u091f \u0938\u0947 \u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u0930\u0916\u0947\u0902\u0964",
                    "\u091c\u0939\u093e\u0901 \u0938\u0902\u092d\u0935 \u0939\u094b \u0915\u093f\u0938\u0940 \u092f\u094b\u0917\u094d\u092f "
                    "\u0935\u094d\u092f\u093e\u0935\u0938\u093e\u092f\u093f\u0915 \u0938\u0941\u0930\u0915\u094d\u0937\u093e \u092a\u0947\u0936\u0947\u0935\u0930 "
                    "\u0938\u0947 \u092c\u093e\u0924 \u0915\u0930\u0947\u0902\u0964",
                ],
            },
        },
        "aggravating": {
            "heavy_workload": "\u0915\u093e\u0930\u094d\u092f\u092d\u093e\u0930 {workload} \u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964",
            "direct_sunlight": "\u0938\u0940\u0927\u0940 \u0927\u0942\u092a \u092e\u0947\u0902 \u0915\u093e\u0930\u094d\u092f \u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964",
            "not_acclimatized": "\u0936\u094d\u0930\u092e\u093f\u0915 \u0915\u094b \u090a\u0937\u094d\u092e\u093e-\u0905\u0928\u0941\u0915\u0942\u0932\u093f\u0924 \u0928\u0939\u0940\u0902 \u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964",
            "water_unavailable": "\u092a\u0940\u0928\u0947 \u0915\u093e \u092a\u093e\u0928\u0940 \u0909\u092a\u0932\u092c\u094d\u0927 \u0928\u0939\u0940\u0902 \u092c\u0924\u093e\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964",
        },
    },

    # =================================================
    # GUJARATI
    # =================================================
    "gu": {
        "workload_labels": {
            "light": "\u0ab9\u0ab3\u0ab5\u0ac1\u0a82",
            "moderate": "\u0aae\u0aa7\u0acd\u0aaf\u0aae",
            "heavy": "\u0aad\u0abe\u0ab0\u0ac7",
            "very_heavy": "\u0a96\u0ac2\u0aac \u0aad\u0abe\u0ab0\u0ac7",
            "unknown": "\u0a85\u0a9c\u0acd\u0a9e\u0abe\u0aa4",
        },
        "emergency_guidance": (
            "\u0a9c\u0acb \u0a95\u0acb\u0a88\u0aa8\u0ac7 \u0a97\u0ac2\u0a82\u0a9a\u0ab5\u0abe\u0a88 \u0a9c\u0ab5\u0ac1\u0a82, "
            "\u0a9d\u0abe\u0a82\u0aaa\u0abe \u0a86\u0ab5\u0ab5\u0abe, \u0aaa\u0aa1\u0ac0 \u0a9c\u0ab5\u0ac1\u0a82 "
            "\u0a85\u0aa5\u0ab5\u0abe \u0aae\u0ac2\u0ab0\u0acd\u0a9b\u0abe \u0a86\u0ab5\u0ab5\u0abe \u0a9c\u0ac7\u0ab5\u0abe "
            "\u0ab2\u0a95\u0acd\u0ab7\u0aa3\u0acb \u0aa6\u0ac7\u0a96\u0abe\u0aaf, \u0aa4\u0acb \u0aa4\u0abe\u0aa4\u0acd\u0a95\u0abe\u0ab2\u0abf\u0a95 "
            "\u0a95\u0a9f\u0acb\u0a95\u0a9f\u0acb \u0aa4\u0aac\u0ac0\u0aac\u0ac0 \u0ab8\u0ab9\u0abe\u0aaf \u0ab2\u0acb. "
            "AI \u0aae\u0ac2\u0ab2\u0acd\u0aaf\u0abe\u0a82\u0a95\u0aa8 \u0aae\u0abe\u0a9f\u0ac7 \u0ab5\u0abf\u0ab2\u0a82\u0aac \u0aa8 \u0a95\u0ab0\u0acb."
        ),
        "no_alerts_summary": (
            "\u0a89\u0aaa\u0ab2\u0aac\u0acd\u0aa7 \u0aa8\u0abf\u0ab0\u0ac0\u0a95\u0acd\u0ab7\u0aa3\u0acb\u0aae\u0abe\u0a82\u0aa5\u0ac0 "
            "\u0a95\u0acb\u0a88 \u0ab8\u0abe\u0ab5\u0aa7\u0abe\u0aa8\u0ac0 \u0a85\u0ab2\u0ab0\u0acd\u0a9f \u0ab8\u0a95\u0acd\u0ab0\u0abf\u0aaf "
            "\u0aa5\u0aaf\u0abe \u0aa8\u0aa5\u0ac0."
        ),
        "summary_template": (
            "\u0ab8\u0a95\u0acd\u0ab0\u0abf\u0aaf \u0ab8\u0abe\u0ab5\u0aa7\u0abe\u0aa8\u0ac0 \u0a85\u0ab2\u0ab0\u0acd\u0a9f: "
            "{count} \u2014 {critical} \u0a97\u0a82\u0aad\u0ac0\u0ab0, "
            "{heightened} \u0a8a\u0a82\u0a9a\u0abe, {advisory} \u0ab8\u0abe\u0aae\u0abe\u0aa8\u0acd\u0aaf."
        ),
        "limitations": [
            "\u0a86 \u0a85\u0ab2\u0ab0\u0acd\u0a9f \u0ab8\u0abe\u0ab5\u0aa7\u0abe\u0aa8\u0ac0\u0aaa\u0ac2\u0ab0\u0acd\u0ab5\u0a95 "
            "\u0a9c\u0abe\u0a82\u0a9a \u0ab8\u0a82\u0a95\u0ac7\u0aa4\u0acb \u0a9b\u0ac7, \u0ab5\u0acd\u0aaf\u0ab5\u0ab8\u0abe\u0aaf\u0abf\u0a95 "
            "\u0a97\u0ab0\u0aae\u0ac0-\u0a9c\u0acb\u0a96\u0aae \u0ab5\u0ab0\u0acd\u0a97\u0ac0\u0a95\u0ab0\u0aa3 \u0a95\u0ac7 "
            "\u0aa4\u0aac\u0ac0\u0aac\u0ac0 \u0aa8\u0abf\u0aa6\u0abe\u0aa8 \u0aae\u0abe\u0a9f\u0ac7 \u0aa8\u0aa5\u0ac0.",
            "\u0aaa\u0ab0\u0acd\u0aaf\u0abe\u0ab5\u0ab0\u0aa3\u0ac0\u0aaf \u0aa8\u0abf\u0ab0\u0ac0\u0a95\u0acd\u0ab7\u0aa3\u0acb "
            "\u0ab9\u0ab5\u0abe\u0aae\u0abe\u0aa8 \u0ab8\u0acd\u0a9f\u0ac7\u0ab6\u0aa8\u0aa8\u0acb \u0aa1\u0ac7\u0a9f\u0abe \u0a9b\u0ac7 "
            "\u0a85\u0aa8\u0ac7 \u0ab5\u0abe\u0ab8\u0acd\u0aa4\u0ab5\u0abf\u0a95 \u0a95\u0abe\u0ab0\u0acd\u0aaf\u0ab8\u0acd\u0aa5\u0ab3\u0aa8\u0ac0 "
            "\u0ab8\u0acd\u0aa5\u0abf\u0aa4\u0abf\u0a93\u0aa5\u0ac0 \u0a85\u0ab2\u0a97 \u0ab9\u0acb\u0a88 \u0ab6\u0a95\u0ac7 \u0a9b\u0ac7.",
            "\u0a86\u0aad\u0abe\u0ab8\u0ac0 \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8\u0aa8\u0acb \u0a9f\u0acd\u0ab0\u0abf\u0a97\u0ab0 \u0aa4\u0ab0\u0ac0\u0a95\u0ac7 "
            "\u0a89\u0aaa\u0aaf\u0acb\u0a97 \u0aa5\u0aaf\u0acb \u0aa8\u0aa5\u0ac0 \u0a85\u0aa8\u0ac7 \u0aa4\u0ac7 \u0aae\u0abe\u0aaa\u0ac7\u0ab2\u0abe "
            "\u0ab5\u0ac7\u0a9f \u0aac\u0ab2\u0acd\u0aac \u0a97\u0acd\u0ab2\u0acb\u0aac \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8 (WBGT) \u0aa8\u0acb "
            "\u0ab5\u0abf\u0a95\u0ab2\u0acd\u0aaa \u0aa8\u0aa5\u0ac0.",
            "\u0a95\u0acb\u0a88 \u0a86\u0a82\u0a95\u0aa1\u0abe\u0a95\u0ac0\u0aaf \u0a97\u0ab0\u0aae\u0ac0-\u0a9c\u0acb\u0a96\u0aae \u0ab8\u0acd\u0a95\u0acb\u0ab0 "
            "\u0aac\u0aa8\u0abe\u0ab5\u0abe\u0aaf\u0acb \u0aa8\u0aa5\u0ac0.",
        ],
        "alerts": {
            "extreme_environmental_heat": {
                "title": "\u0a85\u0aa4\u0acd\u0aaf\u0a82\u0aa4 \u0aaa\u0ab0\u0acd\u0aaf\u0abe\u0ab5\u0ab0\u0aa3\u0ac0\u0aaf \u0a97\u0ab0\u0aae\u0ac0",
                "triggers": [
                    "\u0aaa\u0ab0\u0acd\u0aaf\u0abe\u0ab5\u0ab0\u0aa3\u0ac0\u0aaf \u0ab9\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8 "
                    "{temp} \u00b0C \u0a9b\u0ac7 (\u0ab8\u0ac0\u0aae\u0abe: 40 \u00b0C)\u0964"
                ],
                "guidance": [
                    "\u0a9c\u0acd\u0aaf\u0abe\u0a82 \u0ab6\u0a95\u0acd\u0aaf \u0ab9\u0acb\u0aaf \u0aa4\u0acd\u0aaf\u0abe\u0a82, \u0ab5\u0aa7\u0ac1 "
                    "\u0a97\u0ab0\u0aae\u0ac0\u0aa8\u0abe \u0ab8\u0aae\u0aaf\u0ac7 \u0aac\u0abf\u0aa8-\u0a9c\u0ab0\u0ac2\u0ab0\u0ac0 "
                    "\u0aac\u0ab9\u0abe\u0ab0\u0aa8\u0abe \u0ab6\u0abe\u0ab0\u0ac0\u0ab0\u0abf\u0a95 \u0a95\u0abe\u0ab0\u0acd\u0aaf\u0aa8\u0ac7 "
                    "\u0aae\u0ac1\u0ab2\u0aa4\u0ab5\u0ac0 \u0a95\u0ab0\u0acb\u0964",
                    "\u0a86\u0ab0\u0abe\u0aae-\u0ab5\u0abf\u0ab0\u0abe\u0aae\u0aa8\u0ac0 \u0ab5\u0abe\u0ab0\u0a82\u0ab5\u0abe\u0ab0\u0aa4\u0abe "
                    "\u0ab5\u0aa7\u0abe\u0ab0\u0acb \u0a85\u0aa8\u0ac7 \u0a9b\u0abe\u0aaf\u0abe\u0ab5\u0abe\u0ab3\u0ac1\u0a82 \u0a95\u0ac7 "
                    "\u0aa0\u0a82\u0aa1\u0ac1\u0a82 \u0aaa\u0ac1\u0aa8\u0a83\u0aaa\u0acd\u0ab0\u0abe\u0aaa\u0acd\u0aa4\u0abf \u0ab5\u0abf\u0ab8\u0acd\u0aa4\u0abe\u0ab0 "
                    "\u0aaa\u0ac2\u0ab0\u0ac1\u0a82 \u0aaa\u0abe\u0aa1\u0acb\u0964",
                    "\u0a95\u0abe\u0aae\u0aa6\u0abe\u0ab0\u0acb\u0aa8\u0ac7 \u0a97\u0ab0\u0aae\u0ac0\u0aa8\u0ac7 \u0ab2\u0a97\u0aa4\u0ac0 "
                    "\u0aac\u0ac0\u0aae\u0abe\u0ab0\u0ac0\u0aa8\u0abe \u0ab8\u0a82\u0a95\u0ac7\u0aa4\u0acb \u0aae\u0abe\u0a9f\u0ac7 \u0aa8\u0a9c\u0ac0\u0a95\u0aa5\u0ac0 "
                    "\u0aa6\u0ac7\u0a96\u0ab0\u0ac7\u0a96 \u0ab0\u0abe\u0a96\u0acb\u0964",
                ],
            },
            "high_environmental_temperature": {
                "title": "\u0a8a\u0a82\u0a9a\u0ac1\u0a82 \u0aaa\u0ab0\u0acd\u0aaf\u0abe\u0ab5\u0ab0\u0aa3\u0ac0\u0aaf \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8",
                "triggers": [
                    "\u0aaa\u0ab0\u0acd\u0aaf\u0abe\u0ab5\u0ab0\u0aa3\u0ac0\u0aaf \u0ab9\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8 "
                    "{temp} \u00b0C \u0a9b\u0ac7 (\u0ab8\u0ac0\u0aae\u0abe: 35 \u00b0C)\u0964"
                ],
                "guidance": [
                    "\u0a95\u0aa0\u0abf\u0aa8 \u0aac\u0ab9\u0abe\u0ab0\u0aa8\u0abe \u0a95\u0abe\u0ab0\u0acd\u0aaf\u0acb\u0aa8\u0ac7 \u0aa6\u0abf\u0ab5\u0ab8\u0aa8\u0abe "
                    "\u0aa0\u0a82\u0aa1\u0abe \u0ab8\u0aae\u0aaf\u0ac7 \u0aa8\u0abf\u0ab0\u0acd\u0aa7\u0abe\u0ab0\u0abf\u0aa4 \u0a95\u0ab0\u0acb\u0964",
                    "\u0a96\u0abe\u0aa4\u0ab0\u0ac0 \u0a95\u0ab0\u0acb \u0a95\u0ac7 \u0aaa\u0ac0\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aaa\u0abe\u0aa3\u0ac0 "
                    "\u0a85\u0aa8\u0ac7 \u0a9b\u0abe\u0aaf\u0abe \u0ab8\u0ab0\u0ab3\u0aa4\u0abe\u0aa5\u0ac0 \u0a89\u0aaa\u0ab2\u0aac\u0acd\u0aa7 \u0ab9\u0acb\u0aaf\u0964",
                    "\u0ab8\u0ac0\u0aa7\u0ac0 \u0aa7\u0abe\u0aac\u0abe\u0aa5\u0ac0 \u0aac\u0ab9\u0abe\u0ab0 \u0aa8\u0abf\u0aaf\u0aae\u0abf\u0aa4 "
                    "\u0a86\u0ab0\u0abe\u0aae-\u0ab5\u0abf\u0ab0\u0abe\u0aae \u0aae\u0abe\u0a9f\u0ac7 \u0aaa\u0acd\u0ab0\u0acb\u0aa4\u0acd\u0ab8\u0abe\u0ab9\u0abf\u0aa4 "
                    "\u0a95\u0ab0\u0acb\u0964",
                ],
            },
            "elevated_humidity_reduced_cooling": {
                "title": "\u0a8a\u0a82\u0a9a\u0ac0 \u0aad\u0ac7\u0a9c\u0aa5\u0ac0 \u0a20\u0a82\u0aa1\u0a95 \u0a98\u0a9f\u0ac0 \u0ab0\u0ab9\u0ac0 \u0a9b\u0ac7",
                "triggers": [
                    "\u0ab8\u0abe\u0aaa\u0ac7\u0a95\u0acd\u0ab7 \u0aad\u0ac7\u0a9c {humidity}% \u0a9b\u0ac7 \u0a85\u0aa8\u0ac7 "
                    "\u0ab9\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8 {temp} \u00b0C \u0a9b\u0ac7\u0964"
                ],
                "guidance": [
                    "\u0a8a\u0a82\u0a9a\u0acb \u0aad\u0ac7\u0a9c \u0aac\u0abe\u0ab7\u0acd\u0aaa\u0ac0\u0aaf \u0a20\u0a82\u0aa1\u0a95 \u0a98\u0a9f\u0abe\u0aa1\u0ac7 \u0a9b\u0ac7; "
                    "\u0ab5\u0aa7\u0ac1 \u0a9b\u0abe\u0aaf\u0abe, \u0a9c\u0ab3\u0aaf\u0acb\u0a9c\u0aa8 \u0a85\u0aa8\u0ac7 \u0a86\u0ab0\u0abe\u0aae \u0aaa\u0ab0 "
                    "\u0a86\u0aa7\u0abe\u0ab0 \u0ab0\u0abe\u0a96\u0acb\u0964",
                    "\u0a9c\u0acd\u0aaf\u0abe\u0a82 \u0ab5\u0acd\u0aaf\u0ab5\u0ab9\u0abe\u0ab0\u0ac1 \u0ab9\u0acb\u0aaf \u0aa4\u0acd\u0aaf\u0abe\u0a82 "
                    "\u0a95\u0abe\u0ab0\u0acd\u0aaf \u0aa4\u0ac0\u0ab5\u0acd\u0ab0\u0aa4\u0abe \u0a98\u0a9f\u0abe\u0aa1\u0acb \u0a85\u0aa8\u0ac7 "
                    "\u0ab8\u0acd\u0aa5\u0abf\u0aa4\u0abf\u0a93\u0aa8\u0ac0 \u0aa6\u0ac7\u0a96\u0ab0\u0ac7\u0a96 \u0ab0\u0abe\u0a96\u0acb\u0964",
                ],
            },
            "elevated_humidity": {
                "title": "\u0ab5\u0aa7\u0ac7\u0ab2\u0acb \u0aad\u0ac7\u0a9c",
                "triggers": [
                    "\u0ab8\u0abe\u0aaa\u0ac7\u0a95\u0acd\u0ab7 \u0aad\u0ac7\u0a9c {humidity}% \u0a9b\u0ac7 \u0a85\u0aa8\u0ac7 "
                    "\u0ab9\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8 {temp} \u00b0C \u0a9b\u0ac7\u0964"
                ],
                "guidance": [
                    "\u0aa7\u0acd\u0aaf\u0abe\u0aa8 \u0ab0\u0abe\u0a96\u0acb \u0a95\u0ac7 \u0aad\u0ac7\u0a9c \u0a20\u0a82\u0aa1\u0a95\u0aa8\u0ac0 "
                    "\u0a85\u0ab8\u0ab0\u0a95\u0abe\u0ab0\u0aa4\u0abe \u0a98\u0a9f\u0abe\u0aa1\u0ac0 \u0ab6\u0a95\u0ac7 \u0a9b\u0ac7; "
                    "\u0a9c\u0ab3\u0aaf\u0acb\u0a9c\u0aa8 \u0a85\u0aa8\u0ac7 \u0a9b\u0abe\u0aaf\u0abe \u0a89\u0aaa\u0ab2\u0aac\u0acd\u0aa7\u0aa4\u0abe \u0a9c\u0abe\u0ab3\u0ab5\u0ac0 "
                    "\u0ab0\u0abe\u0a96\u0acb\u0964",
                ],
            },
            "low_wind_speed": {
                "title": "\u0a93\u0a9b\u0acb \u0ab9\u0ab5\u0abe \u0aaa\u0acd\u0ab0\u0ab5\u0abe\u0ab9",
                "triggers": [
                    "\u0ab9\u0ab5\u0abe\u0aa8\u0ac0 \u0a97\u0aa4\u0abf {wind} \u0a95\u0abf\u0aae\u0ac0/\u0a95\u0ab2\u0abe\u0a95 \u0a9b\u0ac7 "
                    "\u0a85\u0aa8\u0ac7 \u0ab9\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8 {temp} \u00b0C \u0a9b\u0ac7\u0964"
                ],
                "guidance": [
                    "\u0a93\u0a9b\u0ac0 \u0ab9\u0ab5\u0abe\u0aa8\u0ac0 \u0a97\u0aa4\u0abf \u0aaa\u0acd\u0ab0\u0abe\u0a95\u0ac3\u0aa4\u0abf\u0a95 \u0ab9\u0ab5\u0abe "
                    "\u0aaa\u0acd\u0ab0\u0ab5\u0abe\u0ab9 \u0a98\u0a9f\u0abe\u0aa1\u0ac0 \u0ab6\u0a95\u0ac7 \u0a9b\u0ac7; "
                    "\u0a95\u0abe\u0ab0\u0acd\u0aaf\u0ab8\u0acd\u0aa5\u0ab3\u0ac7 \u0a9b\u0abe\u0aaf\u0abe \u0a85\u0aa8\u0ac7 \u0ab5\u0abe\u0aaf\u0ac1-\u0ab8\u0a82\u0a9a\u0abe\u0ab0 "
                    "\u0a96\u0abe\u0aa4\u0ab0\u0ac0 \u0a95\u0ab0\u0acb\u0964",
                ],
            },
            "drinking_water_unavailable": {
                "title": "\u0aaa\u0ac0\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aaa\u0abe\u0aa3\u0ac0 \u0a85\u0aa8\u0ac1\u0aaa\u0ab2\u0aac\u0acd\u0aa7",
                "triggers": [
                    "\u0aaa\u0ac0\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aaa\u0abe\u0aa3\u0ac0 \u0a89\u0aaa\u0ab2\u0aac\u0acd\u0aa7 \u0aa8\u0ab9\u0ac0\u0a82 "
                    "\u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964"
                ],
                "guidance": [
                    "\u0a95\u0abe\u0aae \u0a9a\u0abe\u0ab2\u0ac1\u0a82 \u0ab0\u0abe\u0a96\u0ab5\u0abe\u0aa8\u0abe \u0aaa\u0ab9\u0ac7\u0ab2\u0abe\u0a82 "
                    "\u0a95\u0abe\u0ab0\u0acd\u0aaf\u0ab8\u0acd\u0aa5\u0ab3\u0ac7 \u0ab8\u0ac1\u0ab2\u0aad \u0aaa\u0ac0\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aaa\u0abe\u0aa3\u0ac0 "
                    "\u0a97\u0acb\u0aa0\u0ab5\u0acb\u0964",
                    "\u0ab5\u0abe\u0ab0\u0a82\u0ab5\u0abe\u0ab0 \u0a9c\u0ab3\u0aaf\u0acb\u0a9c\u0aa8\u0aa8\u0ac0 \u0aa4\u0a95\u0acb \u0aaa\u0ac2\u0ab0\u0ac0 \u0aaa\u0abe\u0aa1\u0acb\u0964",
                ],
            },
            "not_acclimatized_heavy_outdoor_work": {
                "title": "\u0aad\u0abe\u0ab0\u0ac7 \u0aac\u0ab9\u0abe\u0ab0\u0aa8\u0abe \u0a95\u0abe\u0aae \u0aae\u0abe\u0a9f\u0ac7 \u0a9f\u0ac7\u0ab5\u0abe\u0aaf\u0ac7\u0ab2 \u0aa8\u0aa5\u0ac0",
                "triggers": [
                    "\u0a95\u0abe\u0aae\u0aa6\u0abe\u0ab0 \u0a97\u0ab0\u0aae\u0ac0-\u0a9f\u0ac7\u0ab5\u0abe\u0aaf\u0ac7\u0ab2 \u0aa8\u0aa5\u0ac0 "
                    "\u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
                    "\u0a95\u0abe\u0ab0\u0acd\u0aaf\u0aad\u0abe\u0ab0 {workload} \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
                    "\u0ab8\u0ac0\u0aa7\u0ac0 \u0aa7\u0abe\u0aac\u0abe\u0aae\u0abe\u0a82 \u0a95\u0abe\u0aae \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
                ],
                "guidance": [
                    "\u0ab5\u0acd\u0aaf\u0ab5\u0ab8\u0abe\u0aaf\u0abf\u0a95 \u0ab8\u0ac1\u0ab0\u0a95\u0acd\u0ab7\u0abe \u0aae\u0abe\u0ab0\u0acd\u0a97\u0aa6\u0ab0\u0acd\u0ab6\u0aa8 "
                    "\u0ab9\u0ac7\u0aa0\u0ab3\u0abe \u0a95\u0acd\u0ab0\u0aae\u0abf\u0a95 \u0a97\u0ab0\u0aae\u0ac0-\u0a9f\u0ac7\u0a95\u0abe\u0ab5\u0ab5\u0abe\u0aa8\u0ac0 "
                    "\u0aaf\u0acb\u0a9c\u0aa8\u0abe \u0ab2\u0abe\u0a97\u0ac1 \u0a95\u0ab0\u0acb\u0964",
                    "\u0a9f\u0ac7\u0ab5\u0abe\u0aaf\u0abe\u0aa4\u0abe \u0ab8\u0ac1\u0aa7\u0ac0 \u0a85\u0ab5\u0aa7\u0abf \u0a98\u0a9f\u0abe\u0aa1\u0acb "
                    "\u0a85\u0aa8\u0ac7 \u0aaa\u0ac1\u0aa8\u0a83\u0aaa\u0acd\u0ab0\u0abe\u0aaa\u0acd\u0aa4\u0abf \u0a86\u0ab0\u0abe\u0aae \u0ab5\u0aa7\u0abe\u0ab0\u0acb\u0964",
                ],
            },
            "very_heavy_workload": {
                "title": "\u0a85\u0aa4\u0acd\u0aaf\u0a82\u0aa4 \u0aad\u0abe\u0ab0\u0ac7 \u0ab6\u0abe\u0ab0\u0ac0\u0ab0\u0abf\u0a95 \u0a95\u0abe\u0ab0\u0acd\u0aaf\u0aad\u0abe\u0ab0",
                "triggers": [
                    "\u0a95\u0abe\u0ab0\u0acd\u0aaf\u0aad\u0abe\u0ab0 \u0a85\u0aa4\u0acd\u0aaf\u0a82\u0aa4 \u0aad\u0abe\u0ab0\u0ac7 "
                    "\u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964"
                ],
                "guidance": [
                    "\u0a95\u0abe\u0ab0\u0acd\u0aaf \u0aa4\u0ac0\u0ab5\u0acd\u0ab0\u0aa4\u0abe\u0aa8\u0ac0 \u0ab8\u0aae\u0ac0\u0a95\u0acd\u0ab7\u0abe \u0a95\u0ab0\u0acb "
                    "\u0a85\u0aa8\u0ac7 \u0ab8\u0ab3\u0a82\u0a97 \u0aaa\u0ab0\u0abf\u0ab6\u0acd\u0ab0\u0aae \u0aae\u0ab0\u0acd\u0aaf\u0abe\u0aa6\u0abf\u0aa4 \u0a95\u0ab0\u0ab5\u0abe "
                    "\u0a9c\u0acd\u0aaf\u0abe\u0a82 \u0ab6\u0a95\u0acd\u0aaf \u0ab9\u0acb\u0aaf \u0aa4\u0acd\u0aaf\u0abe\u0a82 \u0a95\u0abe\u0ab0\u0acd\u0aaf\u0acb\u0aa8\u0ac1\u0a82 "
                    "\u0aab\u0ac7\u0ab0\u0aab\u0abe\u0ab0 \u0a95\u0ab0\u0acb\u0964",
                ],
            },
            "extended_exposure_without_breaks": {
                "title": "\u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac7\u0ab2 \u0ab5\u0abf\u0ab0\u0abe\u0aae \u0ab5\u0abf\u0aa8\u0abe \u0ab5\u0abf\u0ab8\u0acd\u0aa4\u0ac3\u0aa4 \u0ab8\u0a82\u0aaa\u0ab0\u0acd\u0a95",
                "triggers": [
                    "\u0ab8\u0ab3\u0a82\u0a97 \u0ab8\u0a82\u0aaa\u0ab0\u0acd\u0a95 {minutes} \u0aae\u0abf\u0aa8\u0abf\u0a9f \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
                    "\u0aaa\u0ac1\u0aa8\u0a83\u0aaa\u0acd\u0ab0\u0abe\u0aaa\u0acd\u0aa4\u0abf-\u0ab5\u0abf\u0ab0\u0abe\u0aae\u0aa8\u0ac0 \u0ab5\u0abe\u0ab0\u0a82\u0ab5\u0abe\u0ab0\u0aa4\u0abe "
                    "\u0a86\u0aaa\u0ab5\u0abe\u0aae\u0abe\u0a82 \u0aa8\u0aa5\u0ac0\u0964",
                ],
                "guidance": [
                    "\u0ab5\u0abe\u0ab8\u0acd\u0aa4\u0ab5\u0abf\u0a95 \u0aaa\u0ac1\u0aa8\u0a83\u0aaa\u0acd\u0ab0\u0abe\u0aaa\u0acd\u0aa4\u0abf-\u0ab5\u0abf\u0ab0\u0abe\u0aae\u0aa8\u0ac0 "
                    "\u0ab5\u0abe\u0ab0\u0a82\u0ab5\u0abe\u0ab0\u0aa4\u0abe\u0aa8\u0ac0 \u0a96\u0abe\u0aa4\u0ab0\u0ac0 \u0a95\u0ab0\u0acb \u0a85\u0aa8\u0ac7 "
                    "\u0aaa\u0acd\u0ab0\u0aae\u0abe\u0aa3\u0abf\u0aa4 \u0ab5\u0acd\u0aaf\u0ab5\u0ab8\u0abe\u0aaf\u0abf\u0a95 \u0a97\u0ab0\u0aae\u0ac0 \u0aae\u0abe\u0ab0\u0acd\u0a97\u0aa6\u0ab0\u0acd\u0ab6\u0aa8\u0aa5\u0ac0 "
                    "\u0aaf\u0acb\u0a97\u0acd\u0aaf \u0a95\u0abe\u0ab0\u0acd\u0aaf-\u0a86\u0ab0\u0abe\u0aae \u0a95\u0abe\u0ab0\u0acd\u0aaf\u0a95\u0acd\u0ab0\u0aae\u0aa8\u0ac0 \u0ab8\u0aae\u0ac0\u0a95\u0acd\u0ab7\u0abe \u0a95\u0ab0\u0acb\u0964",
                ],
            },
            "no_shade_direct_sun": {
                "title": "\u0ab8\u0ac0\u0aa7\u0ac0 \u0aa7\u0abe\u0aac\u0acb \u0a85\u0aa8\u0ac7 \u0a9b\u0abe\u0aaf\u0abe \u0a85\u0aa8\u0ac1\u0aaa\u0ab2\u0aac\u0acd\u0aa7",
                "triggers": [
                    "\u0a9b\u0abe\u0aaf\u0abe \u0a89\u0aaa\u0ab2\u0aac\u0acd\u0aa7\u0aa4\u0abe \u0aa8\u0ab9\u0ac0\u0a82 \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0a88 \u0a9b\u0ac7\u0964",
                    "\u0ab8\u0ac0\u0aa7\u0ac0 \u0aa7\u0abe\u0aac\u0abe\u0aae\u0abe\u0a82 \u0a95\u0abe\u0aae \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
                ],
                "guidance": [
                    "\u0a86\u0ab0\u0abe\u0aae \u0aae\u0abe\u0a9f\u0ac7 \u0ab8\u0ac1\u0ab2\u0aad \u0a9b\u0abe\u0aaf\u0abe\u0ab5\u0abe\u0ab3\u0ac1\u0a82 \u0a95\u0ac7 "
                    "\u0aa0\u0a82\u0aa1\u0ac1\u0a82 \u0aaa\u0ac1\u0aa8\u0a83\u0aaa\u0acd\u0ab0\u0abe\u0aaa\u0acd\u0aa4\u0abf \u0ab5\u0abf\u0ab8\u0acd\u0aa4\u0abe\u0ab0 "
                    "\u0aaa\u0ac2\u0ab0\u0ac1\u0a82 \u0aaa\u0abe\u0aa1\u0acb\u0964",
                ],
            },
            "extreme_heat_with_exposure_compound": {
                "title": "\u0a85\u0aa8\u0abe\u0ab5\u0ab0\u0aa3 \u0aaa\u0ab0\u0abf\u0aac\u0abe\u0ab3\u0acb\u0aa5\u0ac0 \u0ab5\u0aa7\u0ac7\u0ab2\u0ac0 \u0a85\u0aa4\u0acd\u0aaf\u0a82\u0aa4 \u0a97\u0ab0\u0aae\u0ac0",
                "triggers": [
                    "\u0aaa\u0ab0\u0acd\u0aaf\u0abe\u0ab5\u0ab0\u0aa3\u0ac0\u0aaf \u0ab9\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aa4\u0abe\u0aaa\u0aae\u0abe\u0aa8 "
                    "{temp} \u00b0C \u0a9b\u0ac7 (\u0ab8\u0ac0\u0aae\u0abe: 40 \u00b0C)\u0964"
                ],
                "guidance": [
                    "\u0ab5\u0aa7\u0ac7\u0ab2\u0ac0 \u0ab8\u0abe\u0ab5\u0aa7\u0abe\u0aa8\u0ac0 \u0ab2\u0abe\u0a97\u0ac1 \u0a95\u0ab0\u0acb: "
                    "\u0aac\u0ab9\u0abe\u0ab0\u0aa8\u0abe \u0ab6\u0abe\u0ab0\u0ac0\u0ab0\u0abf\u0a95 \u0a95\u0abe\u0aae\u0aa8\u0ac7 \u0aae\u0ac1\u0ab2\u0aa4\u0ab5\u0ac0 \u0a95\u0ab0\u0acb \u0a95\u0ac7 "
                    "\u0a98\u0a9f\u0abe\u0aa1\u0acb, \u0aaa\u0ac1\u0aa8\u0a83\u0aaa\u0acd\u0ab0\u0abe\u0aaa\u0acd\u0aa4\u0abf \u0a86\u0ab0\u0abe\u0aae \u0ab5\u0aa7\u0abe\u0ab0\u0acb, "
                    "\u0a85\u0aa8\u0ac7 \u0a96\u0abe\u0aa4\u0ab0\u0ac0 \u0a95\u0ab0\u0acb \u0a95\u0ac7 \u0a9b\u0abe\u0aaf\u0abe, \u0aa0\u0a82\u0aa1\u0a95 \u0a85\u0aa8\u0ac7 "
                    "\u0aaa\u0ac0\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aaa\u0abe\u0aa3\u0ac0 \u0aa4\u0abe\u0aa4\u0acd\u0a95\u0abe\u0ab2\u0abf\u0a95 \u0a89\u0aaa\u0ab2\u0aac\u0acd\u0aa7 \u0ab9\u0acb\u0aaf\u0964",
                    "\u0a95\u0abe\u0aae\u0aa6\u0abe\u0ab0\u0acb\u0aa8\u0ac7 \u0a97\u0ab0\u0aae\u0ac0\u0aa8\u0ac7 \u0ab2\u0a97\u0aa4\u0ac0 \u0aac\u0ac0\u0aae\u0abe\u0ab0\u0ac0\u0aa8\u0abe "
                    "\u0ab8\u0a82\u0a95\u0ac7\u0aa4\u0acb \u0aae\u0abe\u0a9f\u0ac7 \u0aa8\u0a9c\u0ac0\u0a95\u0aa5\u0ac0 \u0aa6\u0ac7\u0a96\u0ab0\u0ac7\u0a96 \u0ab0\u0abe\u0a96\u0acb\u0964",
                    "\u0a9c\u0acd\u0aaf\u0abe\u0a82 \u0ab6\u0a95\u0acd\u0aaf \u0ab9\u0acb\u0aaf \u0a95\u0acb\u0a88 \u0ab2\u0abe\u0aaf\u0a95 \u0ab5\u0acd\u0aaf\u0ab5\u0ab8\u0abe\u0aaf\u0abf\u0a95 "
                    "\u0ab8\u0ac1\u0ab0\u0a95\u0acd\u0ab7\u0abe \u0ab5\u0acd\u0aaf\u0ab5\u0ab8\u0abe\u0aaf\u0ac0\u0aa8\u0ac7 \u0aae\u0ab3\u0acb\u0964",
                ],
            },
        },
        "aggravating": {
            "heavy_workload": "\u0a95\u0abe\u0ab0\u0acd\u0aaf\u0aad\u0abe\u0ab0 {workload} \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
            "direct_sunlight": "\u0ab8\u0ac0\u0aa7\u0ac0 \u0aa7\u0abe\u0aac\u0abe\u0aae\u0abe\u0a82 \u0a95\u0abe\u0aae \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
            "not_acclimatized": "\u0a95\u0abe\u0aae\u0aa6\u0abe\u0ab0 \u0a97\u0ab0\u0aae\u0ac0-\u0a9f\u0ac7\u0ab5\u0abe\u0aaf\u0ac7\u0ab2 \u0aa8\u0aa5\u0ac0 \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
            "water_unavailable": "\u0aaa\u0ac0\u0ab5\u0abe\u0aa8\u0ac1\u0a82 \u0aaa\u0abe\u0aa3\u0ac0 \u0a89\u0aaa\u0ab2\u0aac\u0acd\u0aa7 \u0aa8\u0ab9\u0ac0\u0a82 \u0a9c\u0aa3\u0abe\u0ab5\u0abe\u0aaf\u0ac1\u0a82 \u0a9b\u0ac7\u0964",
        },
    },
}


def _strings_for(language: str) -> dict:
    """Return the localized string table for a language (falls back to en)."""
    return _STRINGS.get(language, _STRINGS["en"])


def _build_alert(s, alert_id, priority, basis, values=None):
    """Build one localized alert from its string-table definition."""
    definition = s["alerts"][alert_id]
    values = values or {}
    triggers = [template.format(**values) for template in definition["triggers"]]
    return {
        "id": alert_id,
        "priority": priority,
        "title": definition["title"],
        "basis": basis,
        "triggers": triggers,
        "guidance": list(definition["guidance"]),
    }


# --------------------------------------------------
# INDIVIDUAL ALERT BUILDERS
# --------------------------------------------------

def _environmental_alerts(weather_summary: dict, s) -> list[dict]:
    """Build alerts grounded in environmental observations only."""
    alerts: list[dict] = []

    temperature = weather_summary.get("temperature_c")
    humidity = weather_summary.get("humidity_percent")
    wind_speed = weather_summary.get("wind_speed_kmh")

    # Extreme environmental heat (>= 40 deg C).
    if _is_valid_number(temperature) and temperature >= 40:
        alerts.append(_build_alert(
            s, "extreme_environmental_heat",
            "critical_precaution", "environmental_observation",
            {"temp": _fmt(temperature)},
        ))

    # High environmental temperature (35-39.9 deg C).
    elif _is_valid_number(temperature) and temperature >= 35:
        alerts.append(_build_alert(
            s, "high_environmental_temperature",
            "heightened_precaution", "environmental_observation",
            {"temp": _fmt(temperature)},
        ))

    # Elevated humidity reducing evaporative cooling.
    if (
        _is_valid_number(humidity)
        and _is_valid_number(temperature)
        and temperature >= 30
    ):
        if humidity >= 70:
            alerts.append(_build_alert(
                s, "elevated_humidity_reduced_cooling",
                "heightened_precaution", "environmental_observation",
                {"humidity": _fmt(humidity), "temp": _fmt(temperature)},
            ))
        elif humidity >= 60:
            alerts.append(_build_alert(
                s, "elevated_humidity",
                "advisory", "environmental_observation",
                {"humidity": _fmt(humidity), "temp": _fmt(temperature)},
            ))

    # Low wind (minor environmental advisory, only with heat present).
    if (
        _is_valid_number(wind_speed)
        and wind_speed < 5
        and _is_valid_number(temperature)
        and temperature >= 30
    ):
        alerts.append(_build_alert(
            s, "low_wind_speed",
            "advisory", "environmental_observation",
            {"wind": _fmt(wind_speed), "temp": _fmt(temperature)},
        ))

    return alerts


def _worker_alerts(worker: dict, s) -> list[dict]:
    """Build alerts grounded in reported worker exposure factors."""
    alerts: list[dict] = []

    workload = worker.get("workload")
    direct_sunlight = worker.get("direct_sunlight")
    shade = worker.get("shade_availability")
    water_access = worker.get("water_access")
    acclimatization = worker.get("acclimatization")
    continuous = worker.get("continuous_exposure_minutes")
    break_frequency = worker.get("break_frequency_minutes")

    workload_label = s["workload_labels"].get(workload, str(workload))

    # Drinking water unavailable -> critical, concrete action.
    if water_access is False:
        alerts.append(_build_alert(
            s, "drinking_water_unavailable",
            "critical_precaution", "worker_exposure_factor",
        ))

    # Not acclimatized + heavy outdoor work.
    if (
        acclimatization == "not_acclimatized"
        and workload in ("heavy", "very_heavy")
        and direct_sunlight is True
    ):
        alerts.append(_build_alert(
            s, "not_acclimatized_heavy_outdoor_work",
            "heightened_precaution", "worker_exposure_factor",
            {"workload": workload_label},
        ))

    # Very heavy workload.
    if workload == "very_heavy":
        alerts.append(_build_alert(
            s, "very_heavy_workload",
            "advisory", "worker_exposure_factor",
        ))

    # Extended exposure without reported breaks.
    if (
        _is_valid_number(continuous)
        and continuous >= 150
        and break_frequency is None
    ):
        alerts.append(_build_alert(
            s, "extended_exposure_without_breaks",
            "heightened_precaution", "worker_exposure_factor",
            {"minutes": _fmt(continuous)},
        ))

    # No shade with direct sun.
    if shade == "none" and direct_sunlight is True:
        alerts.append(_build_alert(
            s, "no_shade_direct_sun",
            "advisory", "worker_exposure_factor",
        ))

    return alerts


def _combined_alerts(weather_summary: dict, worker: dict, s) -> list[dict]:
    """Build alerts from environmental + exposure factors compounding."""
    alerts: list[dict] = []

    temperature = weather_summary.get("temperature_c")
    workload = worker.get("workload")
    direct_sunlight = worker.get("direct_sunlight")
    water_access = worker.get("water_access")
    acclimatization = worker.get("acclimatization")

    if not (_is_valid_number(temperature) and temperature >= 40):
        return alerts

    workload_label = s["workload_labels"].get(workload, str(workload))
    aggravating = []

    if workload in ("heavy", "very_heavy"):
        aggravating.append(
            s["aggravating"]["heavy_workload"].format(workload=workload_label)
        )
    if direct_sunlight is True:
        aggravating.append(s["aggravating"]["direct_sunlight"])
    if acclimatization == "not_acclimatized":
        aggravating.append(s["aggravating"]["not_acclimatized"])
    if water_access is False:
        aggravating.append(s["aggravating"]["water_unavailable"])

    # Only emit a combined alert when extreme heat is compounded by
    # at least one aggravating exposure factor.
    if not aggravating:
        return alerts

    definition = s["alerts"]["extreme_heat_with_exposure_compound"]
    triggers = [
        definition["triggers"][0].format(temp=_fmt(temperature)),
        *aggravating,
    ]

    alerts.append({
        "id": "extreme_heat_with_exposure_compound",
        "priority": "critical_precaution",
        "title": definition["title"],
        "basis": "combined",
        "triggers": triggers,
        "guidance": list(definition["guidance"]),
    })

    return alerts


# --------------------------------------------------
# PUBLIC API
# --------------------------------------------------

def generate_safety_alerts(
    assessment: dict,
    worker: dict,
    language: str = "en",
) -> dict:
    """
    Produce proactive, deterministic safety alerts from a completed
    deterministic assessment and validated worker profile, localized
    into the worker's preferred language.

    Args:
        assessment: The result of ``assess_heat_exposure``.
        worker: The validated worker profile dict.
        language: One of SUPPORTED_LANGUAGES (default "en").

    Returns:
        A structured, localized ``safety_alerts`` object.
    """

    if not isinstance(assessment, dict) or not assessment.get("success"):
        return {
            "success": False,
            "error": "A successful deterministic assessment is required.",
        }

    if not isinstance(worker, dict):
        return {
            "success": False,
            "error": "A valid worker profile is required.",
        }

    s = _strings_for(language)

    weather_summary = assessment.get("weather_summary") or {}

    environmental = _environmental_alerts(weather_summary, s)
    worker_alerts = _worker_alerts(worker, s)
    combined = _combined_alerts(weather_summary, worker, s)

    # When the combined extreme-heat alert fires, drop the standalone
    # extreme environmental heat alert to avoid repeating the same
    # threshold twice at the same priority.
    has_combined = any(
        a["id"] == "extreme_heat_with_exposure_compound" for a in combined
    )

    if has_combined:
        environmental = [
            a for a in environmental
            if a["id"] != "extreme_environmental_heat"
        ]

    alerts = environmental + worker_alerts + combined

    # Stable ordering: critical first, then heightened, then advisory.
    alerts.sort(
        key=lambda a: _PRIORITY_RANK.get(a["priority"], 0),
        reverse=True,
    )

    highest = _highest_priority(alerts)
    has_critical = any(a["priority"] == "critical_precaution" for a in alerts)

    counts = {
        "critical_precaution": sum(
            1 for a in alerts if a["priority"] == "critical_precaution"
        ),
        "heightened_precaution": sum(
            1 for a in alerts if a["priority"] == "heightened_precaution"
        ),
        "advisory": sum(1 for a in alerts if a["priority"] == "advisory"),
    }

    if not alerts:
        summary = s["no_alerts_summary"]
    else:
        summary = s["summary_template"].format(
            count=len(alerts),
            critical=counts["critical_precaution"],
            heightened=counts["heightened_precaution"],
            advisory=counts["advisory"],
        )

    return {
        "success": True,
        "language": language if language in SUPPORTED_LANGUAGES else "en",
        "alerts": alerts,
        "alert_count": len(alerts),
        "counts": counts,
        "highest_priority": highest,
        "has_critical_precaution": has_critical,
        "emergency_guidance": s["emergency_guidance"] if has_critical else "",
        "summary": summary,
        "limitations": list(s["limitations"]),
    }
