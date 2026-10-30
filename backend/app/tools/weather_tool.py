"""
HeatShield AI — Weather Intelligence Tool

Retrieves current weather and hourly forecasts from Open-Meteo.

Incomplete hourly forecast records are excluded.
Weather data is not a substitute for occupational WBGT.
"""

import httpx

from strands import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

TIMEOUT_SECONDS = 20

CURRENT_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "wind_speed_10m",
    "cloud_cover",
]

HOURLY_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
]


def _error(message: str) -> dict:
    """Return a consistent weather error response."""

    return {
        "success": False,
        "source": "Open-Meteo",
        "error": message,
    }


def _is_complete_record(record: dict) -> bool:
    """Check that all required hourly measurements are available."""

    return all(
        record.get(field) is not None
        for field in HOURLY_FIELDS
    )


@tool
def get_weather(location: str) -> dict:
    """
    Retrieve current weather and the next six complete
    hourly forecast records for a location.

    Args:
        location: City or place name.

    Returns:
        Structured weather information from Open-Meteo.
    """

    if not location or not location.strip():
        return _error("Location cannot be empty.")

    location = location.strip()

    try:

        # ------------------------------------------
        # STEP 1: GEOCODING
        # ------------------------------------------

        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:

            geo_response = client.get(
                GEOCODING_URL,
                params={
                    "name": location,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
            )

            geo_response.raise_for_status()

            geo_data = geo_response.json()

            results = geo_data.get("results", [])

            if not results:
                return _error(
                    f"No location found for '{location}'."
                )

            place = results[0]

            latitude = place["latitude"]
            longitude = place["longitude"]

            resolved_location = {
                "name": place.get("name"),
                "country": place.get("country"),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": place.get("timezone"),
            }

            # --------------------------------------
            # STEP 2: WEATHER RETRIEVAL
            # --------------------------------------

            forecast_response = client.get(
                FORECAST_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": ",".join(CURRENT_FIELDS),
                    "hourly": ",".join(HOURLY_FIELDS),
                    "forecast_days": 1,
                    "timezone": "auto",
                },
            )

            forecast_response.raise_for_status()

            weather_data = forecast_response.json()

        # ------------------------------------------
        # STEP 3: VALIDATE CURRENT CONDITIONS
        # ------------------------------------------

        current = weather_data.get("current")

        if not isinstance(current, dict):
            return _error(
                "Current weather information is unavailable."
            )

        missing_current = [
            field
            for field in CURRENT_FIELDS
            if current.get(field) is None
        ]

        if missing_current:
            return _error(
                "Incomplete current weather measurements: "
                + ", ".join(missing_current)
            )

        current_time = current.get("time")

        if not current_time:
            return _error(
                "Current weather timestamp is unavailable."
            )

        # ------------------------------------------
        # STEP 4: PROCESS HOURLY FORECAST
        # ------------------------------------------

        hourly = weather_data.get("hourly", {})

        times = hourly.get("time", [])

        hourly_records = []

        omitted_incomplete_records = 0

        omitted_past_records = 0

        for index, timestamp in enumerate(times):

            # Open-Meteo returns local timestamps in
            # ascending chronological order.
            if timestamp < current_time:
                omitted_past_records += 1
                continue

            record = {
                "time": timestamp,
            }

            for field in HOURLY_FIELDS:

                values = hourly.get(field, [])

                value = (
                    values[index]
                    if index < len(values)
                    else None
                )

                record[field] = value

            # Never send incomplete forecast records
            # to the Climate Intelligence Agent.
            if not _is_complete_record(record):

                omitted_incomplete_records += 1

                continue

            hourly_records.append(record)

            if len(hourly_records) == 6:
                break

        # ------------------------------------------
        # STEP 5: UNIT INFORMATION
        # ------------------------------------------

        current_units = weather_data.get(
            "current_units",
            {},
        )

        hourly_units = weather_data.get(
            "hourly_units",
            {},
        )

        # ------------------------------------------
        # STEP 6: FINAL RESPONSE
        # ------------------------------------------

        return {
            "success": True,

            "source": "Open-Meteo",

            "location": resolved_location,

            "current": current,

            "hourly_forecast": hourly_records,

            "forecast_data_quality": {
                "requested_records": 6,
                "returned_records": len(hourly_records),
                "omitted_incomplete_records": (
                    omitted_incomplete_records
                ),
                "omitted_past_records": (
                    omitted_past_records
                ),
                "all_returned_records_complete": all(
                    _is_complete_record(record)
                    for record in hourly_records
                ),
            },

            "units": {
                "current": current_units,
                "hourly": hourly_units,
            },

            "data_note": (
                "Weather data is provided by Open-Meteo. "
                "It represents environmental weather information, "
                "not direct occupational worksite measurements. "
                "Apparent temperature is not measured WBGT."
            ),
        }

    except httpx.TimeoutException:

        return _error(
            "Weather service request timed out. Please retry."
        )

    except httpx.HTTPStatusError as error:

        return _error(
            f"Weather service returned HTTP "
            f"{error.response.status_code}."
        )

    except httpx.RequestError as error:

        return _error(
            f"Weather service connection failed: {error}"
        )

    except (KeyError, IndexError, TypeError, ValueError) as error:

        return _error(
            f"Weather response could not be processed: {error}"
        )


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("HEATSHIELD AI — WEATHER TOOL TEST")
    print("=" * 60)

    result = get_weather("Vadodara")

    import json

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    if result.get("success"):
        print("\nWEATHER TOOL EXECUTION SUCCESSFUL")
    else:
        print("\nWEATHER TOOL EXECUTION FAILED")
