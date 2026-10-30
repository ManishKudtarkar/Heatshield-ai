from datetime import datetime, timezone
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from app.agents.orchestrator import run_heatshield
from app.schemas.worker import WorkerProfile


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
