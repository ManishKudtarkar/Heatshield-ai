"""
HeatShield AI — Cooling Resource Discovery

Deterministic discovery of public cooling resources near an assessed
location — shaded rest points, drinking-water stations and public
shelters — using the OpenStreetMap Overpass API.

Design principles (mirrors the rest of HeatShield AI):

- Resources come only from real map data; nothing is invented.
- Every resource keeps its raw OSM provenance (element id, name) so a
  worker or supervisor can verify it on a map.
- Availability cannot be confirmed remotely; every response carries
  explicit limitations (verify before relying on a resource).
- If the map service is unreachable, the module fails gracefully with
  success=False and an explanatory error rather than fabricating data.
"""

import logging
from typing import Any

import httpx


logger = logging.getLogger("heatshield-cooling-resources")

OVERPASS_ENDPOINT = "https://api.overpass-api.de/api/interpreter"
GEOCODING_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"

RESOURCE_QUERY_RADIUS_METERS = 5000
MAX_RESULTS_PER_CATEGORY = 10

REQUEST_TIMEOUT_SECONDS = 20.0

# Overpass selector fragments per cooling-resource category.
CATEGORY_SELECTORS: dict[str, str] = {
    "drinking_water": (
        'node["drinking_water"~"yes|tap|bottle_refill|public"]'
        '["access"!~"private"]'
    ),
    "shade": (
        'node["amenity"~"bench|shelter"]'
        ',way["amenity"~"shelter|covered_bench"]'
        ',node["highway"="bus_stop"]["shelter"="yes"]'
    ),
    "cooled_shelter": (
        'node["amenity"="community_centre"]'
        ',way["amenity"="community_centre"]'
        ',node["emergency"="assembly_point"]'
        ',way["emergency"="assembly_point"]'
    ),
}

CATEGORY_LABELS = {
    "drinking_water": "Drinking water point",
    "shade": "Shaded rest point",
    "cooled_shelter": "Public shelter / cooled refuge",
}

CATEGORY_DESCRIPTIONS = {
    "drinking_water": (
        "A mapped location providing drinking water. Verify that the "
        "supply is currently functional before relying on it."
    ),
    "shade": (
        "A bench, shelter structure or covered stop suitable for a "
        "shaded recovery break."
    ),
    "cooled_shelter": (
        "A public building or assembly area that may offer shade or "
        "cooler indoor space during extreme heat."
    ),
}


# --------------------------------------------------
# GEOCODING
# --------------------------------------------------

def geocode_location(location: str) -> dict:
    """Resolve a place name to coordinates via Open-Meteo geocoding."""

    try:
        response = httpx.get(
            GEOCODING_ENDPOINT,
            params={"name": location, "count": 1, "language": "en"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        results = response.json().get("results") or []
    except Exception as exc:  # network / parse failure
        return {"success": False, "error": str(exc)}

    if not results:
        return {"success": False, "error": "Location could not be resolved."}

    top = results[0]

    return {
        "success": True,
        "latitude": top.get("latitude"),
        "longitude": top.get("longitude"),
        "resolved_name": top.get("name", location),
        "country": top.get("country", "Unknown"),
    }


# --------------------------------------------------
# OVERPASS QUERY
# --------------------------------------------------

def _build_query(latitude: float, longitude: float) -> str:
    parts = []
    for selector in CATEGORY_SELECTORS.values():
        parts.append(
            f"{selector}"
            f"(around:{RESOURCE_QUERY_RADIUS_METERS},"
            f"{latitude},{longitude});"
        )

    union = "\n".join(parts)

    return (
        f"[out:json][timeout:{int(REQUEST_TIMEOUT_SECONDS)}];(\n"
        f"{union}\n"
        f");out body {MAX_RESULTS_PER_CATEGORY * len(CATEGORY_SELECTORS)};"
    )


def _classify(element: dict) -> str | None:
    tags = element.get("tags") or {}

    if tags.get("drinking_water") in ("yes", "tap", "bottle_refill", "public"):
        return "drinking_water"

    if (
        tags.get("amenity") in ("bench", "shelter", "covered_bench")
        or (tags.get("highway") == "bus_stop" and tags.get("shelter") == "yes")
    ):
        return "shade"

    if (
        tags.get("amenity") == "community_centre"
        or tags.get("emergency") == "assembly_point"
    ):
        return "cooled_shelter"

    return None


def discover_cooling_resources(
    location: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict:
    """
    Discover mapped cooling resources near a location.

    Coordinates may be supplied directly (for example from the weather
    retrieval stage); otherwise the location name is geocoded first.
    """

    resolved_name = location
    country = "Unknown"

    if latitude is None or longitude is None:
        geo = geocode_location(location)
        if not geo.get("success"):
            return {
                "success": False,
                "error": (
                    "Cooling resource discovery failed: "
                    f"{geo.get('error')}"
                ),
                "resources": [],
            }
        latitude = geo["latitude"]
        longitude = geo["longitude"]
        resolved_name = geo.get("resolved_name", location)
        country = geo.get("country", "Unknown")

    if not isinstance(latitude, (int, float)) or not isinstance(
        longitude, (int, float)
    ):
        return {
            "success": False,
            "error": "Cooling resource discovery requires valid coordinates.",
            "resources": [],
        }

    query = _build_query(latitude, longitude)

    try:
        response = httpx.post(
            OVERPASS_ENDPOINT,
            data={"data": query},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        logger.warning("Overpass request failed: %s", exc)
        return {
            "success": False,
            "error": (
                "The map data service could not be reached. No cooling "
                "resources are reported rather than guessing availability."
            ),
            "resources": [],
        }

    grouped: dict[str, list[dict]] = {
        category: [] for category in CATEGORY_LABELS
    }

    for element in payload.get("elements", []):
        category = _classify(element)
        if category is None:
            continue
        if len(grouped[category]) >= MAX_RESULTS_PER_CATEGORY:
            continue

        tags = element.get("tags") or {}
        grouped[category].append(
            {
                "osm_id": f"{element.get('type')}/{element.get('id')}",
                "name": tags.get("name") or tags.get("ref") or None,
                "category": category,
                "category_label": CATEGORY_LABELS[category],
                "description": CATEGORY_DESCRIPTIONS[category],
                "latitude": element.get("lat"),
                "longitude": element.get("lon"),
                "provenance": "OpenStreetMap via Overpass API",
            }
        )

    resources: list[dict[str, Any]] = []
    for items in grouped.values():
        resources.extend(items)

    return {
        "success": True,
        "location": resolved_name,
        "country": country,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "search_radius_meters": RESOURCE_QUERY_RADIUS_METERS,
        "resource_count": len(resources),
        "counts_by_category": {
            category: len(items) for category, items in grouped.items()
        },
        "resources": resources,
        "limitations": [
            "Mapped resources were not physically verified; opening "
            "status, functionality and access rules can change.",
            "Private or restricted facilities are excluded where the "
            "map data marks them as such, but map data may be outdated.",
            "Absence of mapped resources does not mean none exist nearby.",
            "Resource discovery supports planning; it does not replace "
            "employer-provided water, shade and rest arrangements.",
        ],
    }
