
"""
HeatShield AI — Weather Intelligence Tool

Retrieves current weather and forecast data
from the Open-Meteo API.

No API key required.
"""

import httpx

from strands import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@tool
def get_weather(location: str) -> dict:
    """
    Retrieve current weather and forecast information
    for a given city.

    Args:
        location: City name, e.g. Vadodara, Ahmedabad.

    Returns:
        Dictionary containing location, current weather,
        and forecast information.
    """

    try:
        # ------------------------------------------
        # STEP 1: FIND LOCATION COORDINATES
        # ------------------------------------------

        geo_response = httpx.get(
            GEOCODING_URL,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=15.0,
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        results = geo_data.get("results")

        if not results:
            return {
                "success": False,
                "error": f"Location not found: {location}",
            }

        place = results[0]

        latitude = place["latitude"]
        longitude = place["longitude"]

        # ------------------------------------------
        # STEP 2: FETCH WEATHER DATA
        # ------------------------------------------

        weather_response = httpx.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "wind_speed_10m,"
                    "cloud_cover"
                ),
                "hourly": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature"
                ),
                "forecast_days": 1,
                "timezone": "auto",
            },
            timeout=20.0,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data.get("current", {})

        hourly = weather_data.get("hourly", {})

        # ------------------------------------------
        # STEP 3: STRUCTURE RESPONSE
        # ------------------------------------------

        return {
            "success": True,
            "source": "Open-Meteo",
            "location": {
                "name": place.get("name"),
                "country": place.get("country"),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": weather_data.get("timezone"),
            },
            "current_weather": {
                "temperature_c": current.get("temperature_2m"),
                "humidity_percent": current.get(
                    "relative_humidity_2m"
                ),
                "apparent_temperature_c": current.get(
                    "apparent_temperature"
                ),
                "wind_speed_kmh": current.get(
                    "wind_speed_10m"
                ),
                "precipitation_mm": current.get(
                    "precipitation"
                ),
                "cloud_cover_percent": current.get(
                    "cloud_cover"
                ),
                "observed_at": current.get("time"),
            },
            "hourly_forecast": [
                {
                    "time": hourly["time"][i],
                    "temperature_c": hourly["temperature_2m"][i],
                    "humidity_percent": hourly[
                        "relative_humidity_2m"
                    ][i],
                    "apparent_temperature_c": hourly[
                        "apparent_temperature"
                    ][i],
                }
                for i in range(
                    min(6, len(hourly.get("time", [])))
                )
            ],
            "units": weather_data.get("current_units", {}),
            "data_note": (
                "Weather API values are model-based weather "
                "data, not occupational WBGT measurements. "
                "Apparent temperature is not a substitute "
                "for a measured WBGT."
            ),
        }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Weather service timed out.",
        }

    except httpx.HTTPStatusError as error:
        return {
            "success": False,
            "error": (
                f"Weather service returned HTTP "
                f"{error.response.status_code}"
            ),
        }

    except httpx.RequestError as error:
        return {
            "success": False,
            "error": f"Network error: {str(error)}",
        }

    except (KeyError, IndexError, TypeError, ValueError) as error:
        return {
            "success": False,
            "error": f"Unexpected weather data format: {str(error)}",
        }