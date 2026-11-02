from datetime import datetime, timezone
import logging
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agents.orchestrator import run_heatshield
from app.engine.monitor import build_supervisor_overview
from app.engine.store import clear_records, list_records, save_assessment
from app.knowledge import (
    KB_VERSION,
    get_topic,
    list_topics,
    search_knowledge,
    validate_knowledge_base,
)
from app.schemas.worker import WorkerProfile
from app.tools.cooling_tool import SUPPORTED_CATEGORIES, find_cooling_resources_data


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
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


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

    worker_name: str | None = Field(
        default=None,
        max_length=100,
        description="Optional display name used on the supervisor dashboard.",
        examples=["Ramesh Patel"],
    )

    language: Literal["en", "hi", "gu"] = Field(
        default="en",
        description=(
            "Worker interface language. Localizes deterministic safety "
            "alerts and instructs the advisory agents to respond in this "
            "language. Supported: en, hi, gu."
        ),
        examples=["hi"],
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

        # Store a supervisor-facing summary (best effort; never fails
        # the worker's assessment request).
        try:
            save_assessment(
                result,
                language=payload.language,
                worker_name=payload.worker_name,
            )
        except Exception:  # pragma: no cover - defensive
            logger.exception("Assessment summary could not be stored.")

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


# --------------------------------------------------
# KNOWLEDGE BASE ENDPOINTS
# --------------------------------------------------

@app.get("/api/v1/knowledge/topics")
def knowledge_topic_index():
    """Compact index of all validated occupational safety topics."""
    return {
        "success": True,
        "kb_version": KB_VERSION,
        "topics": list_topics(),
    }


@app.get("/api/v1/knowledge/topics/{topic_id}")
def knowledge_topic_detail(topic_id: str, language: str = "en"):
    """One validated topic, localized (falls back to English per field)."""
    topic = get_topic(topic_id, language)

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown knowledge topic: {topic_id}",
        )

    return {"success": True, "kb_version": KB_VERSION, "topic": topic}


@app.get("/api/v1/knowledge/search")
def knowledge_search(q: str, language: str = "en"):
    """Deterministic keyword search over validated topics."""
    query = q.strip()

    if len(query) < 2:
        raise HTTPException(
            status_code=422,
            detail="Search query must contain at least 2 characters.",
        )

    return search_knowledge(query, language)


@app.get("/api/v1/knowledge/validate")
def knowledge_validate():
    """Integrity check: every topic validated, cited and review-dated."""
    return validate_knowledge_base()


# --------------------------------------------------
# COOLING RESOURCE DISCOVERY
# --------------------------------------------------

class CoolingResourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_m: int = Field(
        default=1500,
        ge=100,
        le=5000,
        description="Search radius in metres.",
    )
    categories: list[Literal["water", "shelter", "refuge", "shade"]] | None = Field(
        default=None,
        description=(
            "Cooling-resource categories to include. "
            f"Supported: {', '.join(SUPPORTED_CATEGORIES)}. Default: all."
        ),
    )


@app.post("/api/v1/cooling-resources")
def cooling_resources(payload: CoolingResourceRequest):
    """
    Discover publicly mapped cooling resources near a worksite
    (drinking water, shelters, indoor refuges, shaded spaces).

    Results come from OpenStreetMap only; resources are never
    fabricated and each carries its source link for verification.
    """
    logger.info(
        "Cooling resource discovery at (%s, %s) r=%sm",
        payload.latitude,
        payload.longitude,
        payload.radius_m,
    )

    result = find_cooling_resources_data(
        latitude=payload.latitude,
        longitude=payload.longitude,
        radius_m=payload.radius_m,
        categories=payload.categories,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=502,
            detail=result.get("error", "Cooling resource discovery failed."),
        )

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }


# --------------------------------------------------
# SUPERVISOR MONITORING DASHBOARD
# --------------------------------------------------

class SupervisorOverviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: list[dict] = Field(
        default_factory=list,
        description=(
            "Optional externally collected assessment results to "
            "aggregate together with stored assessments."
        ),
    )


@app.get("/api/v1/supervisor/overview")
def supervisor_overview():
    """Cohort risk overview built from stored assessment summaries."""
    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overview": build_supervisor_overview(list_records()),
    }


@app.post("/api/v1/supervisor/overview")
def supervisor_overview_with_records(payload: SupervisorOverviewRequest):
    """Aggregate submitted assessment results plus stored records."""
    records = list_records() + payload.records

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overview": build_supervisor_overview(records),
    }


@app.delete("/api/v1/supervisor/records")
def supervisor_clear_records():
    """Clear stored assessment summaries (e.g. after a shift ends)."""
    removed = clear_records()

    return {"success": True, "removed": removed}
