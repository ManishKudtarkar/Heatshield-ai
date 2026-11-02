from datetime import datetime, timezone
import logging
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

from app.agents.orchestrator import run_heatshield
from app.schemas.worker import WorkerProfile
from app.engine.safety_alerts import (
    SUPPORTED_LANGUAGES,
    language_name,
)
from app.engine.supervisor_store import (
    list_records,
    record_assessment,
)
from app.tools.cooling_resources import discover_cooling_resources


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("heatshield-api")


# --------------------------------------------------
# API CONFIGURATION
# --------------------------------------------------

app = FastAPI(
    title="HeatShield AI API",
    description=(
        "Multi-agent climate intelligence and worker "
        "heat-exposure screening platform."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --------------------------------------------------
# SUPPORTED INTERFACE LANGUAGES
# --------------------------------------------------

class LanguageOption(BaseModel):
    code: str
    name: str
    native_name: str


LANGUAGE_NATIVE_NAMES = {
    "en": "English",
    "hi": "\u0939\u093f\u0928\u094d\u0926\u0940",       # Hindi
    "gu": "\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0",  # Gujarati
}

SUPPORTED_LANGUAGE_OPTIONS = [
    LanguageOption(
        code=code,
        name=language_name(code),
        native_name=LANGUAGE_NATIVE_NAMES.get(code, language_name(code)),
    )
    for code in SUPPORTED_LANGUAGES
]


# --------------------------------------------------
# REQUEST SCHEMA
# --------------------------------------------------

class HeatAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: str = Field(
        min_length=2,
        max_length=120,
        description="City or location to retrieve weather for.",
        examples=["Vadodara"],
    )

    worker: WorkerProfile

    language: Literal["en", "hi", "gu"] = Field(
        default="en",
        description=(
            "Worker interface language. Localizes deterministic safety "
            "alerts and instructs the advisory agents to respond in this "
            "language. Supported: en (English), hi (Hindi), gu (Gujarati). "
            "Discoverable via GET /api/v1/languages."
        ),
        examples=["hi"],
    )

    response_language: str | None = Field(
        default=None,
        description=(
            "Optional display language for narrative sections returned to "
            "the worker interface (for example \"en\" to read a Hindi "
            "assessment in English). When omitted, narrative sections are "
            "shown directly in the selected worker language. Deterministic "
            "safety alerts always follow the worker ``language``."
        ),
        examples=["en"],
    )


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "project": "HeatShield AI",
        "tagline": "Intelligence Against Extreme Heat. Protection for Every Worker.",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "success": True,
        "service": "HeatShield AI API",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# --------------------------------------------------
# SUPPORTED LANGUAGES ENDPOINT
# --------------------------------------------------

@app.get("/api/v1/languages")
def supported_languages():
    """Interface languages available for worker assessments."""
    return {
        "success": True,
        "default": "en",
        "languages": [option.model_dump() for option in SUPPORTED_LANGUAGE_OPTIONS],
    }


# --------------------------------------------------
# COOLING RESOURCE DISCOVERY ENDPOINT
# --------------------------------------------------

@app.get("/api/v1/cooling-resources")
def cooling_resources(
    location: str = Query(
        default="Vadodara",
        min_length=2,
        max_length=120,
        description="City or worksite to search near.",
    )
):
    """
    Discover mapped public cooling resources (drinking-water points,
    shaded rest points and public shelters) near a location.

    Resources come from OpenStreetMap data and are not physically
    verified; responses include explicit limitations.
    """

    result = discover_cooling_resources(location=location)

    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error"),
            "resources": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }


# --------------------------------------------------
# SUPERVISOR MONITORING DASHBOARD ENDPOINTS
# --------------------------------------------------

PRIORITY_ORDER = {
    "critical_precaution": 3,
    "heightened_precaution": 2,
    "advisory": 1,
    "none": 0,
}


@app.get("/api/v1/supervisor/dashboard")
def supervisor_dashboard():
    """
    Aggregated supervisory view of recent assessments.

    Shows team-wide precaution levels, attention items (assessments
    with critical precautions or missing information) and coverage
    gaps such as water access and shade availability. Screening
    summaries only — no medical records.
    """

    records = list_records()

    priority_counts: dict[str, int] = {}
    for record in records:
        key = record.get("highest_priority", "none")
        priority_counts[key] = priority_counts.get(key, 0) + 1

    attention_items = sorted(
        (
            record
            for record in records
            if record.get("has_critical_precaution")
            or record.get("missing_information")
        ),
        key=lambda record: PRIORITY_ORDER.get(
            record.get("highest_priority", "none"), 0
        ),
        reverse=True,
    )

    locations: dict[str, int] = {}
    for record in records:
        name = record.get("location") or "Unknown"
        locations[name] = locations.get(name, 0) + 1

    coverage_gaps = {
        "no_water_access": sum(
            1 for r in records if r.get("water_access") is False
        ),
        "no_shade": sum(
            1 for r in records if r.get("shade_availability") == "none"
        ),
        "not_acclimatized": sum(
            1 for r in records
            if r.get("acclimatization") == "not_acclimatized"
        ),
    }

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_assessments": len(records),
            "priority_counts": priority_counts,
            "assessments_requiring_attention": len(attention_items),
            "locations_covered": len(locations),
            "coverage_gaps": coverage_gaps,
        },
        "locations": [
            {"location": name, "assessment_count": count}
            for name, count in sorted(
                locations.items(), key=lambda item: -item[1]
            )
        ],
        "attention_items": attention_items[:20],
        "recent_assessments": records[:20],
        "limitations": [
            "Dashboard aggregates screening summaries of submitted "
            "assessments; it does not perform live site monitoring.",
            "Records reflect reported worker profiles at assessment "
            "time, not current conditions.",
            "This is a demonstration store; production deployments "
            "should persist records with appropriate access control.",
        ],
    }


# --------------------------------------------------
# MAIN ASSESSMENT ENDPOINT
# --------------------------------------------------

@app.post("/api/v1/assess")
def create_assessment(payload: HeatAssessmentRequest):

    logger.info(
        "Assessment requested for location: %s",
        payload.location,
    )

    try:
        worker_data = payload.worker.model_dump()

        # Execute the existing multi-agent pipeline.
        result = run_heatshield(
            location=payload.location,
            worker_data=worker_data,
            language=payload.language,
            response_language=payload.response_language,
        )

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="The assessment pipeline returned an invalid response.",
            )

        if not result.get("success"):
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Assessment could not be completed.",
                    "result": result,
                },
            )

        logger.info(
            "Assessment completed successfully for: %s",
            payload.location,
        )

        # Record a supervisory summary for the monitoring dashboard.
        try:
            record_assessment(result)
        except Exception:  # dashboard recording must never fail an assessment
            logger.exception("Supervisor dashboard recording failed.")

        return {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("HeatShield assessment failed.")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the assessment.",
        )
