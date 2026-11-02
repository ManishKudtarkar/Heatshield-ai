"""
HEATSHIELD AI — Multi-Agent Orchestrator

Coordinates:
1. Climate Intelligence Agent
2. Worker Exposure Agent
3. Deterministic Heat Assessment Engine
4. Safety Advisory Agent

Model: Amazon Nova Lite
Region: ap-south-1
"""

import json
import re

from app.tools.weather_tool import get_weather
from app.tools.exposure_tool import assess_worker_exposure_data
from app.tools.cooling_resources import discover_cooling_resources

from app.schemas.worker import WorkerProfile

from app.agents.climate_agent import climate_agent
from app.agents.exposure_agent import exposure_agent
from app.agents.safety_agent import generate_safety_advisory

from app.engine.heat_assessment import assess_heat_exposure
from app.engine.safety_alerts import generate_safety_alerts
from app.engine.knowledge_base import retrieve_knowledge


# ==================================================
# SUPPORTED LANGUAGES
# ==================================================

_LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
}


# ==================================================
# OUTPUT CLEANING
# ==================================================

def clean_agent_output(response) -> str:
    """Clean agent output for presentation."""

    text = str(response)

    text = re.sub(
        r"<thinking>.*?</thinking>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ==================================================
# MAIN ORCHESTRATOR
# ==================================================

def run_heatshield(
    location: str,
    worker_data: dict,
    language: str = "en",
    response_language: str | None = None,
) -> dict:
    """
    Execute the complete HeatShield AI workflow.

    The ``language`` code localizes the deterministic safety alerts
    and instructs the advisory agents to respond in that language.

    ``response_language`` optionally overrides the display language of
    the narrative (agent-generated) sections only — for example an
    English-speaking supervisor reviewing a Hindi worker assessment.
    When omitted, narratives are produced directly in ``language``.
    Deterministic safety alerts always follow ``language``.
    """

    language_name = _LANGUAGE_NAMES.get(language, "English")
    narrative_language_name = (
        _LANGUAGE_NAMES[response_language]
        if response_language in _LANGUAGE_NAMES
        else language_name
    )

    print("\n" + "=" * 65)
    print("             HEATSHIELD AI")
    print("       MULTI-AGENT SAFETY INTELLIGENCE")
    print("=" * 65)

    # ----------------------------------------------
    # STAGE 1: WEATHER RETRIEVAL
    # ----------------------------------------------

    print("\n[1/6] Retrieving environmental intelligence...")

    weather = get_weather(location)

    if not weather.get("success"):
        raise RuntimeError(
            f"Weather retrieval failed: {weather.get('error')}"
        )

    print("[SUCCESS] Weather data retrieved.")

    # ----------------------------------------------
    # STAGE 2: WORKER VALIDATION
    # ----------------------------------------------

    print("\n[2/6] Validating worker profile...")

    worker = WorkerProfile(**worker_data)

    validated_worker = worker.model_dump()

    print("[SUCCESS] Worker profile validated.")

    # ----------------------------------------------
    # STAGE 3A: CLIMATE INTELLIGENCE
    # ----------------------------------------------

    print("\n[3/6] Running Climate Intelligence Agent...")

    climate_prompt = f"""
Analyse the following environmental weather data.

WEATHER DATA:
{json.dumps(weather, indent=2, ensure_ascii=False)}

LOCATION:
{location}

Responsibilities:

1. Summarise current environmental conditions.
2. Explain temperature and humidity independently.
3. Explain apparent temperature accurately.
4. Describe forecast trends using actual values.
5. Explain relevant environmental considerations
   for outdoor workers.
6. State the limitations of the data.

LANGUAGE RULES:

- If the requested response language is not English, translate every
  heading and sentence into that language.
- Never leave untranslated English sentences inside a non-English
  report. Keep only proper nouns, units and measurement values
  unchanged.
- The narrative response language ({narrative_language_name}) may
  differ from the worker's own language; always follow the narrative
  response language requested below.

STRICT RULES:

- Use only the supplied weather data.
- Do not retrieve weather again.
- Do not invent measurements.
- Do not assign occupational heat-risk categories.
- Apparent temperature is not WBGT.
- Compare forecast variables independently.
- Never invent or reverse forecast trends.
- Distinguish environmental observations from
  occupational heat assessments.
- Do not diagnose medical conditions.

Respond in {narrative_language_name}.
"""

    climate_result = climate_agent(climate_prompt)

    climate_report = clean_agent_output(climate_result)

    print("[SUCCESS] Climate analysis completed.")

    # ----------------------------------------------
    # STAGE 3B: STRUCTURED EXPOSURE VALIDATION
    # ----------------------------------------------

    print("\n[4/6] Validating worker exposure information...")

    exposure_data = assess_worker_exposure_data(
        **validated_worker
    )

    if not exposure_data.get("success"):
        raise RuntimeError(
            f"Exposure validation failed: "
            f"{exposure_data.get('error')}"
        )

    print("[SUCCESS] Exposure information validated.")

    # ----------------------------------------------
    # STAGE 3C: EXPOSURE INTELLIGENCE AGENT
    # ----------------------------------------------

    print("\nRunning Worker Exposure Intelligence Agent...")

    exposure_prompt = f"""
You are interpreting an already validated worker exposure
assessment.

The Python exposure validation tool has already executed.

Do not call the tool again.

VALIDATED EXPOSURE RESULT:

{json.dumps(exposure_data, indent=2, ensure_ascii=False)}

Your responsibilities:

1. Explain the worker profile.
2. Explain the identified exposure factors.
3. Explain the missing information.
4. Describe practical safety considerations.
5. Explain assessment limitations.

STRICT DATA RULES:

- The validated JSON is the source of truth.
- Do not modify any worker profile values.
- Do not invent missing information.
- Do not confuse continuous exposure duration
  with break frequency.
- If break_frequency_minutes is null,
  report that break frequency was not provided.
- If work_area is present, report the supplied work area.
- If water_access is true, report that water access
  is available according to the supplied profile.
- Do not generate numerical risk scores.
- Do not assign occupational heat-risk categories.
- Do not diagnose medical conditions.
- Do not declare the worker safe or unsafe.

LANGUAGE RULES:

- If the requested response language is not English, translate every
  section heading into that language as well.
- Translate enumerated field names (for example
  "continuous_exposure_minutes" or "shade_availability") into the
  requested language using plain, worker-friendly wording.
- Never leave untranslated English sentences or snake_case field
  identifiers inside a non-English report.
- Keep only proper nouns, units and measurement values unchanged.
- The narrative response language ({narrative_language_name}) may
  differ from the worker's own language; always follow the narrative
  response language requested below.

Use this output structure:

WORKER PROFILE
EXPOSURE FACTORS
MISSING INFORMATION
PRACTICAL SAFETY CONSIDERATIONS
ASSESSMENT LIMITATIONS

(Translate these headings into the requested response language.)

Use simple, professional language.

Respond in {narrative_language_name}.
"""

    exposure_result = exposure_agent(exposure_prompt)

    exposure_report = clean_agent_output(exposure_result)

    print("[SUCCESS] Worker exposure analysis completed.")

    # ----------------------------------------------
    # STAGE 4: DETERMINISTIC ASSESSMENT
    # ----------------------------------------------

    print("\nRunning deterministic heat assessment...")

    assessment = assess_heat_exposure(
        weather=weather,
        worker=validated_worker,
    )

    if not assessment.get("success"):
        raise RuntimeError(
            f"Assessment failed: {assessment.get('error')}"
        )

    print("[SUCCESS] Deterministic assessment completed.")

    # ----------------------------------------------
    # CONSISTENCY CHECK
    # ----------------------------------------------

    expected_missing = exposure_data["missing_information"]

    engine_missing = assessment["missing_information"]

    if set(expected_missing) != {
        item.removeprefix("worker.")
        for item in engine_missing
    }:
        raise RuntimeError(
            "Data consistency failure: exposure validation "
            "and deterministic assessment disagree."
        )

    print("[SUCCESS] Data consistency verified.")

    # ----------------------------------------------
    # STAGE 5: PROACTIVE SAFETY ALERTS
    # ----------------------------------------------

    print("\n[5/6] Generating proactive safety alerts...")

    safety_alerts = generate_safety_alerts(
        assessment=assessment,
        worker=validated_worker,
        language=language,
    )

    if not safety_alerts.get("success"):
        raise RuntimeError(
            f"Safety alerts generation failed: "
            f"{safety_alerts.get('error')}"
        )

    print("[SUCCESS] Proactive safety alerts generated.")

    # ----------------------------------------------
    # STAGE 5B: VALIDATED KNOWLEDGE BASE RETRIEVAL
    # ----------------------------------------------

    print("\nRetrieving validated occupational safety knowledge...")

    knowledge_base = retrieve_knowledge(
        weather_summary=assessment.get("weather_summary"),
        worker_summary=assessment.get("worker_summary"),
        language=language,
    )

    print(
        f"[SUCCESS] {knowledge_base.get('entry_count', 0)} "
        "validated knowledge entries retrieved."
    )

    # ----------------------------------------------
    # STAGE 5C: COOLING RESOURCE DISCOVERY
    # ----------------------------------------------

    print("\nDiscovering nearby cooling resources...")

    place = weather.get("location") or {}

    cooling_resources = discover_cooling_resources(
        location=place.get("name") or location,
        latitude=place.get("latitude"),
        longitude=place.get("longitude"),
    )

    if cooling_resources.get("success"):
        print(
            "[SUCCESS] Cooling resource discovery completed "
            f"({cooling_resources.get('resource_count', 0)} mapped resources)."
        )
    else:
        print(
            "[NOTICE] Cooling resource discovery unavailable: "
            f"{cooling_resources.get('error')}"
        )

    # ----------------------------------------------
    # STAGE 6: SAFETY ADVISORY
    # ----------------------------------------------

    print("\n[6/6] Generating safety advisory...")

    advisory_result = generate_safety_advisory(
        assessment,
        safety_alerts=safety_alerts,
        language=language,
        response_language=response_language,
        knowledge_base=knowledge_base,
    )

    advisory_report = clean_agent_output(advisory_result)

    print("[SUCCESS] Safety advisory generated.")

    # ----------------------------------------------
    # FINAL REPORT
    # ----------------------------------------------

    return {
        "success": True,

        "project": "HeatShield AI",

        "location": location,

        "language": language,

        "response_language": (
            response_language
            if response_language in _LANGUAGE_NAMES
            else language
        ),

        "climate_analysis": climate_report,

        "worker_exposure_analysis": exposure_report,

        "validated_exposure_data": exposure_data,

        "deterministic_assessment": assessment,

        "safety_alerts": safety_alerts,

        "knowledge_base": knowledge_base,

        "cooling_resources": cooling_resources,

        "safety_advisory": advisory_report,
    }


# ==================================================
# TEST EXECUTION
# ==================================================

if __name__ == "__main__":

    worker_data = {
        "occupation": "Construction worker",

        "workload": "heavy",

        "shift_hours": 8,

        "direct_sunlight": True,

        "shade_availability": "partial",

        "water_access": True,

        "acclimatization": "not_acclimatized",

        "ppe_items": [
            "Safety helmet",
            "Safety boots",
            "Protective clothing",
        ],

        "continuous_exposure_minutes": 120,

        "break_frequency_minutes": None,

        "work_area": "Outdoor construction site, Vadodara",
    }

    try:

        result = run_heatshield(
            location="Vadodara",
            worker_data=worker_data,
        )

        print("\n" + "=" * 65)
        print("              HEATSHIELD AI FINAL REPORT")
        print("=" * 65)

        print("\n1. CLIMATE INTELLIGENCE")
        print("-" * 65)
        print(result["climate_analysis"])

        print("\n2. WORKER EXPOSURE INTELLIGENCE")
        print("-" * 65)
        print(result["worker_exposure_analysis"])

        print("\n3. VALIDATED EXPOSURE DATA")
        print("-" * 65)

        print(
            json.dumps(
                result["validated_exposure_data"],
                indent=2,
                ensure_ascii=False,
            )
        )

        print("\n4. DETERMINISTIC ASSESSMENT")
        print("-" * 65)

        print(
            json.dumps(
                result["deterministic_assessment"],
                indent=2,
                ensure_ascii=False,
            )
        )

        print("\n5. SAFETY ADVISORY")
        print("-" * 65)
        print(result["safety_advisory"])

        print("\n" + "=" * 65)
        print("HEATSHIELD AI PIPELINE EXECUTION SUCCESSFUL")
        print("=" * 65)

    except Exception as error:

        print("\n" + "=" * 65)
        print("HEATSHIELD AI PIPELINE EXECUTION FAILED")
        print("=" * 65)

        print(f"\nError: {error}")

        raise
