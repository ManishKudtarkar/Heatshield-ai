"""
HeatShield AI — Worker Exposure Validation Tool

Validates worker information and identifies occupational
heat-exposure factors.
"""

from strands import tool
from pydantic import ValidationError

from app.schemas.worker import (
    WorkerProfile,
    get_missing_information,
)


def assess_worker_exposure_data(**worker_data) -> dict:
    """
    Core Python validation function.

    Can be called directly by the orchestrator without
    requiring an LLM tool call.
    """

    try:
        profile = WorkerProfile(**worker_data)

        missing = get_missing_information(profile)

        exposure_factors = []

        if profile.workload in ["heavy", "very_heavy"]:
            exposure_factors.append({
                "factor": "physical_workload",
                "observation": "Reported workload is heavy or very heavy.",
                "reason": "Physical exertion increases metabolic heat production.",
            })

        if profile.direct_sunlight:
            exposure_factors.append({
                "factor": "direct_sunlight",
                "observation": "Worker is exposed to direct sunlight.",
                "reason": "Solar radiation can increase environmental heat load.",
            })

        if profile.shade_availability in ["none", "partial"]:
            exposure_factors.append({
                "factor": "shade",
                "observation": "Shade availability is limited.",
                "reason": "Limited shade reduces opportunities for cooling.",
            })

        if not profile.water_access:
            exposure_factors.append({
                "factor": "water_access",
                "observation": "Drinking water access is unavailable.",
                "reason": "Reliable drinking water access is an important preventive control.",
            })

        if profile.acclimatization == "not_acclimatized":
            exposure_factors.append({
                "factor": "acclimatization",
                "observation": "Worker is reported as not acclimatized.",
                "reason": "Workers new to heat exposure need a gradual acclimatization plan.",
            })

        if profile.ppe_items:
            exposure_factors.append({
                "factor": "protective_equipment",
                "observation": "Protective equipment is reported.",
                "reason": "Some clothing and PPE can reduce heat dissipation.",
            })

        profile_data = profile.model_dump()

        return {
            "success": True,
            "profile": profile_data,

            "field_summary": {
                "continuous_exposure_minutes":
                    profile.continuous_exposure_minutes,

                "break_frequency_minutes":
                    profile.break_frequency_minutes,

                "work_area": profile.work_area,

                "water_access": profile.water_access,
            },

            "exposure_factors": exposure_factors,

            "missing_information": missing,

            "assessment_status": (
                "incomplete" if missing else "profile_complete"
            ),

            "limitations": [
                "This is a worker exposure profile, not a medical diagnosis.",
                "This tool does not calculate an occupational heat-risk score.",
                "Weather conditions and validated occupational heat measurements must be evaluated separately.",
            ],
        }

    except ValidationError as error:

        return {
            "success": False,
            "error": "Worker profile validation failed.",
            "details": error.errors(include_url=False),
        }


@tool
def assess_worker_exposure(
    occupation: str,
    workload: str,
    shift_hours: float,
    direct_sunlight: bool,
    shade_availability: str,
    water_access: bool,
    acclimatization: str,
    ppe_items: list[str],
    continuous_exposure_minutes: int | None = None,
    break_frequency_minutes: int | None = None,
    work_area: str | None = None,
) -> dict:
    """
    Strands tool for validating worker exposure information.
    """

    return assess_worker_exposure_data(
        occupation=occupation,
        workload=workload,
        shift_hours=shift_hours,
        direct_sunlight=direct_sunlight,
        shade_availability=shade_availability,
        water_access=water_access,
        acclimatization=acclimatization,
        ppe_items=ppe_items,
        continuous_exposure_minutes=continuous_exposure_minutes,
        break_frequency_minutes=break_frequency_minutes,
        work_area=work_area,
    )
