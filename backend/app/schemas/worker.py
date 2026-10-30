from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class WorkerProfile(BaseModel):
    """Validated working-condition profile for HeatShield AI."""

    model_config = ConfigDict(extra="forbid")

    occupation: str = Field(min_length=2, max_length=100)

    workload: Literal[
        "light",
        "moderate",
        "heavy",
        "very_heavy",
        "unknown",
    ]

    shift_hours: float = Field(gt=0, le=24)

    direct_sunlight: bool

    shade_availability: Literal[
        "full",
        "partial",
        "none",
        "unknown",
    ]

    water_access: bool

    acclimatization: Literal[
        "acclimatized",
        "not_acclimatized",
        "unknown",
    ]

    ppe_items: list[str] = Field(default_factory=list)

    continuous_exposure_minutes: int | None = Field(
        default=None,
        ge=0,
        le=1440,
    )

    break_frequency_minutes: int | None = Field(
        default=None,
        ge=1,
        le=1440,
    )

    work_area: str | None = None


def get_missing_information(profile: WorkerProfile) -> list[str]:
    """Identify useful exposure details that were not supplied."""

    missing = []

    if profile.continuous_exposure_minutes is None:
        missing.append("continuous_exposure_minutes")

    if profile.break_frequency_minutes is None:
        missing.append("break_frequency_minutes")

    if profile.work_area is None:
        missing.append("work_area")

    if profile.shade_availability == "unknown":
        missing.append("shade_availability")

    if profile.acclimatization == "unknown":
        missing.append("acclimatization")

    if profile.workload == "unknown":
        missing.append("workload")

    return missing
