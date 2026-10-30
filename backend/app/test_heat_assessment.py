import json

from app.engine.heat_assessment import assess_heat_exposure
from app.tools.weather_tool import get_weather
from app.schemas.worker import WorkerProfile


def main():

    print("\nHEATSHIELD AI — DETERMINISTIC ASSESSMENT TEST")
    print("=" * 60)

    # Retrieve actual weather data
    weather = get_weather("Vadodara")

    if not weather.get("success"):
        print("Weather retrieval failed:", weather.get("error"))
        return

    # Example worker profile
    worker = WorkerProfile(
        occupation="Construction worker",
        workload="heavy",
        shift_hours=8,
        direct_sunlight=True,
        shade_availability="partial",
        water_access=True,
        acclimatization="not_acclimatized",
        ppe_items=[
            "Safety helmet",
            "Safety boots",
            "Protective clothing",
        ],
        continuous_exposure_minutes=120,
        break_frequency_minutes=None,
        work_area="Outdoor construction site, Vadodara",
    )

    # Run deterministic assessment
    result = assess_heat_exposure(
        weather=weather,
        worker=worker.model_dump(),
    )

    print("\nASSESSMENT RESULT")
    print("-" * 60)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("ASSESSMENT ENGINE EXECUTION SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()
