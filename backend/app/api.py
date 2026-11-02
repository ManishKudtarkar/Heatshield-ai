from datetime import datetime, timezone
import logging
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

from app.agents.orchestrator import run_heatshield
from app.schemas.worker import WorkerProfile
from app.engine.safety_alerts import (
    SUPPORTED_LANGUAGES,
    language_name,
)


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
