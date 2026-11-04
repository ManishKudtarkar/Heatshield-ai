from datetime import datetime, timezone
import logging
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

# Centralized application configuration
from app.config import settings

# Multi-agent orchestration
from app.agents.orchestrator import run_heatshield

# Supervisor monitoring and storage
from app.engine.monitor import build_supervisor_overview
from app.engine.store import (
    clear_records,
    list_records,
    save_assessment,
)

# Validated occupational safety knowledge base
from app.knowledge import (
    KB_VERSION,
    get_topic,
    list_topics,
    search_knowledge,
    validate_knowledge_base,
)

# Worker validation
from app.schemas.worker import WorkerProfile

# Cooling resource discovery
from app.tools.cooling_tool import (
    SUPPORTED_CATEGORIES,
    find_cooling_resources_data,
)


# ==================================================
# LOGGING CONFIGURATION
# ==================================================

logging.basicConfig(
    level=settings.log_level.upper(),
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("heatshield-api")


# ==================================================
# APPLICATION CONFIGURATION
# ==================================================

app = FastAPI(
    title=settings.app_name,
    description=(
        "Multi-agent climate intelligence and worker "
        "heat-exposure screening platform."
    ),
    version=settings.app_version,
    docs_url="/docs" if settings.api_docs_enabled else None,
    redoc_url="/redoc" if settings.api_docs_enabled else None,
    openapi_url=(
        "/openapi.json"
        if settings.api_docs_enabled
        else None
    ),
)


# ==================================================
# CORS CONFIGURATION
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)


# ==================================================
# REQUEST SCHEMAS
# ==================================================

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
        description=(
            "Optional display name used on the "
            "supervisor dashboard."
        ),
        examples=["Ramesh Patel"],
    )

    language: Literal["en", "hi", "gu"] = Field(
        default="en",
        description=(
            "Worker interface language. Localizes deterministic "
            "safety alerts and instructs advisory agents to respond "
            "in the selected language. Supported: en, hi, gu."
        ),
        examples=["hi"],
    )


class CoolingResourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )

    radius_m: int = Field(
        default=1500,
        ge=100,
        le=5000,
        description="Search radius in metres.",
    )

    categories: list[
        Literal["water", "shelter", "refuge", "shade"]
    ] | None = Field(
        default=None,
        description=(
            "Cooling-resource categories to include. "
            f"Supported: {', '.join(SUPPORTED_CATEGORIES)}. "
            "Default: all."
        ),
    )


class SupervisorOverviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: list[dict] = Field(
        default_factory=list,
        description=(
            "Optional externally collected assessment results "
            "to aggregate together with stored assessments."
        ),
    )


# ==================================================
# ROOT ENDPOINT
# ==================================================

@app.get("/")
def root():
    return {
        "project": "HeatShield AI",
        "tagline": (
            "Intelligence Against Extreme Heat. "
            "Protection for Every Worker."
        ),
        "version": settings.app_version,
        "status": "running",
        "documentation": (
            "/docs"
            if settings.api_docs_enabled
            else None
        ),
        "health": "/health",
        "readiness": "/ready",
    }


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health_check():
    """
    Basic application health check.

    Confirms that the API process is responding.
    Does not test external dependencies.
    """

    return {
        "success": True,
        "service": settings.app_name,
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ==================================================
# READINESS CHECK
# ==================================================

@app.get("/ready")
def readiness_check():
    """
    Application configuration readiness check.

    Does not invoke Amazon Bedrock or external services.
    """

    return {
        "success": True,
        "service": settings.app_name,
        "status": "ready",
        "aws_region": settings.aws_region,
        "bedrock_model_configured": bool(
            settings.bedrock_model_id
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ==================================================
# MAIN HEAT ASSESSMENT ENDPOINT
# ==================================================

@app.post("/api/v1/assess")
def create_assessment(
    payload: HeatAssessmentRequest,
):
    """
    Execute the complete HeatShield AI multi-agent
    worker heat-exposure screening pipeline.
    """

    logger.info(
        "Assessment requested for location: %s",
        payload.location,
    )

    try:
        worker_data = payload.worker.model_dump()

        # Execute existing multi-agent pipeline.
        result = run_heatshield(
            location=payload.location,
            worker_data=worker_data,
            language=payload.language,
        )

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail=(
                    "The assessment pipeline returned "
                    "an invalid response."
                ),
            )

        if not result.get("success"):
            raise HTTPException(
                status_code=422,
                detail={
                    "message": (
                        "Assessment could not be completed."
                    ),
                    "result": result,
                },
            )

        logger.info(
            "Assessment completed successfully for: %s",
            payload.location,
        )

        # Save supervisor-facing summary.
        # Storage failure must not fail the worker assessment.
        stored_summary: dict | None = None

        try:
            stored_summary = save_assessment(
                result,
                language=payload.language,
                worker_name=payload.worker_name,
            )

        except Exception:
            logger.exception(
                "Assessment summary could not be stored."
            )

        response_result = dict(result)

        if stored_summary:
            response_result["assessment_id"] = (
                stored_summary["assessment_id"]
            )

        return {
            "success": True,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "result": response_result,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "HeatShield assessment failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred while "
                "processing the assessment."
            ),
        )


# ==================================================
# KNOWLEDGE BASE ENDPOINTS
# ==================================================

@app.get("/api/v1/knowledge/topics")
def knowledge_topic_index():
    """
    Return compact index of validated occupational
    safety knowledge topics.
    """

    return {
        "success": True,
        "kb_version": KB_VERSION,
        "topics": list_topics(),
    }


@app.get("/api/v1/knowledge/topics/{topic_id}")
def knowledge_topic_detail(
    topic_id: str,
    language: str = "en",
):
    """
    Return one localized knowledge topic.
    Falls back to English per field when necessary.
    """

    topic = get_topic(
        topic_id,
        language,
    )

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown knowledge topic: {topic_id}",
        )

    return {
        "success": True,
        "kb_version": KB_VERSION,
        "topic": topic,
    }


@app.get("/api/v1/knowledge/search")
def knowledge_search(
    q: str,
    language: str = "en",
):
    """
    Deterministic keyword search over validated
    occupational safety topics.
    """

    query = q.strip()

    if len(query) < 2:
        raise HTTPException(
            status_code=422,
            detail=(
                "Search query must contain at least "
                "2 characters."
            ),
        )

    return search_knowledge(
        query,
        language,
    )


@app.get("/api/v1/knowledge/validate")
def knowledge_validate():
    """
    Validate knowledge base integrity.
    """

    return validate_knowledge_base()


# ==================================================
# COOLING RESOURCE DISCOVERY
# ==================================================

@app.post("/api/v1/cooling-resources")
def cooling_resources(
    payload: CoolingResourceRequest,
):
    """
    Discover publicly mapped cooling resources near
    a worksite.

    Supported:
    - Drinking water
    - Shelters
    - Indoor refuges
    - Shaded spaces

    Results originate from OpenStreetMap.
    """

    logger.info(
        "Cooling resource discovery at (%s, %s), radius=%sm",
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
            detail=result.get(
                "error",
                "Cooling resource discovery failed.",
            ),
        )

    return {
        "success": True,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "result": result,
    }


# ==================================================
# SUPERVISOR MONITORING DASHBOARD
# ==================================================

@app.get("/api/v1/supervisor/overview")
def supervisor_overview():
    """
    Return cohort-level monitoring overview
    using stored assessment summaries.
    """

    records = list_records()

    return {
        "success": True,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "overview": build_supervisor_overview(
            records
        ),
    }


@app.post("/api/v1/supervisor/overview")
def supervisor_overview_with_records(
    payload: SupervisorOverviewRequest,
):
    """
    Aggregate externally submitted assessment records
    together with locally stored records.
    """

    records = (
        list_records()
        + payload.records
    )

    return {
        "success": True,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "overview": build_supervisor_overview(
            records
        ),
    }


# ==================================================
# SUPERVISOR RECORD MANAGEMENT
# ==================================================

@app.delete("/api/v1/supervisor/records")
def supervisor_clear_records():
    """
    Clear stored assessment summaries.

    IMPORTANT:
    Protect this endpoint with authentication and
    authorization before exposing the API publicly.
    """

    removed = clear_records()

    logger.warning(
        "Supervisor assessment records cleared: %s",
        removed,
    )

    return {
        "success": True,
        "removed": removed,
    }