"""Redraw each area as one convex outline around its border and its transformers.

No extra packages. The map reads the GeoJSON this writes; the reference file stays
the published municipal geometry.
"""

from __future__ import annotations

import math

# Kept beyond each site so the map dot sits inside the stroke, not on it.
PAD_M = 600


def _cross(origin, a, b):
    return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0])


def _hull(points):
    ordered = sorted(set(points))
    if len(ordered) <= 2:
        return list(ordered)
    lower = []
    for point in ordered:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(ordered):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def _exterior(ring):
    points = [(float(p[0]), float(p[1])) for p in ring]
    if len(points) >= 2 and points[0] == points[-1]:
        points.pop()
    return points


def _pad(lon, lat, radius_m, n=12):
    dlat = radius_m / 111_320
    dlon = dlat / max(0.2, math.cos(math.radians(lat)))
    return [
        (round(lon + dlon * math.cos(2 * math.pi * i / n), 6), round(lat + dlat * math.sin(2 * math.pi * i / n), 6))
        for i in range(n)
    ]


def _outline(geometry, sites, radius_m):
    coords = geometry.get("coordinates") or []
    if geometry.get("type") == "Polygon":
        parts = [coords]
    elif geometry.get("type") == "MultiPolygon":
        parts = coords
    else:
        return None
    raw = []
    for poly in parts:
        if poly:
            raw.extend(_exterior(poly[0]))
    for lon, lat in sites:
        raw.extend(_pad(lon, lat, radius_m))
    hull = _hull(raw)
    if len(hull) < 3:
        return None
    ring = [[point[0], point[1]] for point in hull]
    ring.append([ring[0][0], ring[0][1]])
    return [ring]


def expand_boundaries(gj, points_by_area, radius_m=PAD_M):
    """Replace each area polygon with the convex outline that contains its sites."""
    for feature in gj.get("features", []):
        area_id = str((feature.get("properties") or {}).get("area_id", ""))
        sites = [(float(lon), float(lat)) for lon, lat in points_by_area.get(area_id, [])]
        geom = feature.get("geometry") or {}
        ring = _outline(geom, sites, radius_m)
        if ring is None:
            continue
        geom["type"] = "Polygon"
        geom["coordinates"] = ring
    gj.setdefault("metadata", {})["geometry_note"] = (
        "Convex outline of the municipal boundary plus every transformer assigned to the area."
    )
    return gj
