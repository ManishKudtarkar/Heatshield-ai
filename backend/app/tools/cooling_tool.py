"""
HeatShield AI — Cooling Resource Discovery Tool

Discovers publicly mapped cooling resources near a worksite using
the OpenStreetMap Overpass API (https://overpass-api.de).

Cooling resources include:
- drinking water (fountains, taps, potable water),
- public toilets with shade/refuge value,
- transit shelters and waiting rooms,
- shaded public amenities (parks, gardens, benches),
- community refuges (libraries, malls, places of worship,
  healthcare facilities).

Design rules (mirrors the rest of HeatShield AI):

- Never fabricate resources: only map-verified features are returned.
- Every result carries its OSM source so supervisors can verify it.
- Graceful degradation: API failures return structured errors, never
  invented data.
"""

import math
from typing import Any

import httpx
from strands import tool

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

SUPPORTED_CATEGORIES = (
    "water",
    "shelter",
    "refuge",
    "shade",
)

# Map category -> human-readable label.
CATEGORY_LABELS = {
    "water": "Drinking water",
    "shelter": "Shaded shelter / waiting area",
    "refuge": "Air-conditioned or indoor refuge",
    "shade": "Shaded public space",
}

# OpenStreetMap feature selectors per cooling-resource category.
_CATEGORY_SELECTORS: dict[str, list[str]] = {
    "water": [
        'node["drinking_water"~"yes|restricted"]',
        'node["amenity"="drinking_water"]',
        'node["amenity"="water_point"]',
        'way["amenity"="drinking_water"]',
    ],
    "shelter": [
        'node["amenity"="shelter"]',
        'way["amenity"="shelter"]',
        'node["highway"="bus_stop"]',
        'node["public_transport"="platform"]',
    ],
    "refuge": [
        'node["amenity"="library"]',
        'way["amenity"="library"]',
        'node["amenity"="place_of_worship"]',
        'way["amenity"="place_of_worship"]',
        'node["shop"="mall"]',
        'way["shop"="mall"]',
        'node["amenity"~"clinic|hospital|pharmacy"]',
        'way["amenity"~"clinic|hospital|pharmacy"]',
    ],
    "shade": [
        'node["leisure"="park"]',
        'way["leisure"="park"]',
        'node["leisure"="garden"]',
        'way["leisure"="garden"]',
        'node["natural"="tree"]',
        'node["amenity"="bench"]',
    ],
}


def _haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Great-circle distance in kilometres between two points."""
    radius_km = 6371.0

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )

    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _build_query(
    latitude: float,
    longitude: float,
    radius_m: int,
    categories: list[str],
) -> str:
    """Build an Overpass QL query for the requested categories."""
    bbox = (
        f"(around:{radius_m},{latitude},{longitude})"
    )

    parts = []

    for category in categories:
        for selector in _CATEGORY_SELECTORS[category]:
            parts.append(
                f'{selector}{bbox};'
            )

    body = "\n  ".join(parts)

    return f"[out:json][timeout:25];\n(\n  {body}\n);\nout center tags 1..{400};"


def _extract_name(tags: dict[str, Any]) -> str | None:
    """Pick the best available display name from OSM tags."""
    for key in ("name", "name:en", "operator", "brand"):
        value = tags.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def _categorize_element(element: dict[str, Any]) -> str | None:
    """Map an OSM element's tags to a HeatShield cooling category."""
    tags = element.get("tags", {})

    if (
        tags.get("drinking_water") in ("yes", "restricted")
        or tags.get("amenity") in ("drinking_water", "water_point")
    ):
        return "water"

    if (
        tags.get("amenity") == "shelter"
        or tags.get("highway") == "bus_stop"
        or tags.get("public_transport") == "platform"
    ):
        return "shelter"

    if (
        tags.get("amenity") in ("library", "place_of_worship", "clinic", "hospital", "pharmacy")
        or tags.get("shop") == "mall"
    ):
        return "refuge"

    if (
        tags.get("leisure") in ("park", "garden")
        or tags.get("natural") == "tree"
        or tags.get("amenity") == "bench"
    ):
        return "shade"

    return None


def find_cooling_resources_data(
    latitude: float,
    longitude: float,
    radius_m: int = 1500,
    categories: list[str] | None = None,
) -> dict:
    """
    Core Python discovery function (callable without an LLM tool call).

    Args:
        latitude: Worksite latitude (WGS84).
        longitude: Worksite longitude (WGS84).
        radius_m: Search radius in metres (100–5000).
        categories: Subset of SUPPORTED_CATEGORIES (default: all).

    Returns:
        Structured discovery result. ``success`` is False with an
        ``error`` field when the map service cannot be reached;
        resources are never fabricated.
    """
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return {
            "success": False,
            "error": "Coordinates must be valid WGS84 values.",
        }

    if not (100 <= radius_m <= 5000):
        return {
            "success": False,
            "error": "Search radius must be between 100 and 5000 metres.",
        }

    selected = categories or list(SUPPORTED_CATEGORIES)

    unknown = [c for c in selected if c not in SUPPORTED_CATEGORIES]
    if unknown:
        return {
            "success": False,
            "error": (
                f"Unsupported cooling categories: {', '.join(unknown)}. "
                f"Supported: {', '.join(SUPPORTED_CATEGORIES)}."
            ),
        }

    query = _build_query(latitude, longitude, radius_m, selected)

    try:
        response = httpx.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=30.0,
            headers={"User-Agent": "HeatShield-AI/1.0 (occupational heat safety screening)"},
        )
        response.raise_for_status()
        payload = response.json()

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Map service (OpenStreetMap Overpass) timed out.",
        }
    except httpx.HTTPStatusError as error:
        return {
            "success": False,
            "error": (
                f"Map service returned HTTP {error.response.status_code}."
            ),
        }
    except httpx.RequestError as error:
        return {
            "success": False,
            "error": f"Network error contacting map service: {error}",
        }
    except (ValueError, KeyError):
        return {
            "success": False,
            "error": "Unexpected response format from map service.",
        }

    resources: list[dict[str, Any]] = []

    for element in payload.get("elements", []):
        category = _categorize_element(element)

        if category is None or category not in selected:
            continue

        lat = element.get("lat")
        lon = element.get("lon")

        if lat is None or lon is None:
            center = element.get("center") or {}
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is None or lon is None:
            continue

        tags = element.get("tags", {})
        distance_km = _haversine_km(latitude, longitude, lat, lon)

        resources.append(
            {
                "osm_id": f"{element.get('type')}/{element.get('id')}",
                "name": _extract_name(tags) or CATEGORY_LABELS[category],
                "category": category,
                "category_label": CATEGORY_LABELS[category],
                "osm_tags": {
                    key: tags[key]
                    for key in (
                        "amenity",
                        "drinking_water",
                        "leisure",
                        "shop",
                        "highway",
                        "public_transport",
                        "natural",
                        "opening_hours",
                        "covered",
                        "air_conditioning",
                        "internet_access",
                        "wheelchair",
                    )
                    if key in tags
                },
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "distance_km": round(distance_km, 2),
                "source": "OpenStreetMap",
                "source_url": (
                    "https://www.openstreetmap.org/"
                    f"{element.get('type')}/{element.get('id')}"
                ),
            }
        )

    resources.sort(key=lambda item: item["distance_km"])

    deduped: list[dict[str, Any]] = []
    seen_names: set[tuple[str, str]] = set()

    for resource in resources:
        key = (resource["category"], resource["name"].lower())
        if key in seen_names and resource["distance_km"] > 0.3:
            continue
        seen_names.add(key)
        deduped.append(resource)

    by_category: dict[str, int] = {c: 0 for c in selected}
    for resource in deduped:
        by_category[resource["category"]] += 1

    return {
        "success": True,
        "location": {"latitude": latitude, "longitude": longitude},
        "radius_m": radius_m,
        "categories": selected,
        "resource_count": len(deduped),
        "counts_by_category": by_category,
        "resources": deduped[:60],
        "source": "OpenStreetMap (Overpass API)",
        "limitations": [
            "Mapped resources may be closed, relocated, or restricted; verify before relying on them.",
            "OpenStreetMap coverage varies by region; absence of results does not mean no resources exist.",
            "This tool lists candidate resources only; it does not confirm access, capacity, or operating hours.",
        ],
    }


try:  # Register as a Strands tool when the framework is available.

    @tool
    def get_cooling_resources(
        location: str,
        radius_m: int = 1500,
    ) -> dict:
        """
        Discover nearby publicly mapped cooling resources (drinking
        water, shelters, indoor refuges, shaded spaces) for a city or
        worksite location using OpenStreetMap data.

        Args:
            location: City or area name, e.g. Vadodara.
            radius_m: Search radius in metres (100-5000).

        Returns:
            Dictionary of map-verified cooling resources sorted by
            distance, or a structured error. Resources are never
            fabricated.
        """
        geo_response = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=15.0,
        )
        geo_response.raise_for_status()
        results = geo_response.json().get("results")

        if not results:
            return {
                "success": False,
                "error": f"Location not found: {location}",
            }

        place = results[0]

        return find_cooling_resources_data(
            latitude=place["latitude"],
            longitude=place["longitude"],
            radius_m=radius_m,
        )

except ImportError:  # pragma: no cover - strands optional
    get_cooling_resources = None  # type: ignore[assignment]
