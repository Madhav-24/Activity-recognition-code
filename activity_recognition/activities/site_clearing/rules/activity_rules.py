"""Scoring rules for the Site Clearing activity."""

from __future__ import annotations

from typing import Any


# Purpose: Defines machinery, road-layer, and visual-feature scores for Site Clearing.
# Use: Combines those component scores into the activity result consumed by inference and dashboards.

ACTIVITY_NAME = "Site Clearing"
REQUIRED_MACHINERY = ["Bulldozer", "Excavator", "Loader"]
REQUIRED_ROAD_LAYER = "Soil"
FEATURES_USED = ["edge_density", "texture_variance", "green_ratio"]
MACHINERY_WEIGHT = 3.0
ROAD_LAYER_WEIGHT = 3.0
FEATURE_WEIGHT = 1.0


# Logical block: clamps a confidence or normalized feature value to the valid 0-to-1 range.
def _bounded(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


# Logical block: averages the best detected confidence for each required machine class.
def machinery_score(detections: dict[str, float]) -> float:
    if not detections:
        return 0.0
    values = [_bounded(detections.get(name, 0.0)) for name in REQUIRED_MACHINERY]
    return sum(values) / len(values)


# Logical block: awards the road-layer confidence only when the required layer matches.
def road_layer_score(detected_layer: str | None, confidence: float) -> float:
    if detected_layer is None or detected_layer.strip().lower() != REQUIRED_ROAD_LAYER.lower():
        return 0.0
    return _bounded(confidence)


# Logical block: converts configured visual features into a normalized feature score.
def feature_score(features: dict[str, float]) -> float:
    if not features:
        return 0.0
    components = []
    if "edge_density" in FEATURES_USED:
        components.append(1.0 - min(float(features.get("edge_density", 0.0)) / 0.30, 1.0))
    if "texture_variance" in FEATURES_USED:
        components.append(min(max(float(features.get("texture_variance", 0.0)) / 5000.0, 0.0), 1.0))
    if "green_ratio" in FEATURES_USED:
        components.append(_bounded(features.get("green_ratio", 0.0)))
    return sum(components) / len(components) if components else 0.0


# Logical block: combines component scores using the Site Clearing weights.
def calculate_activity_score(
    detections: dict[str, float],
    detected_layer: str | None,
    layer_confidence: float,
    features: dict[str, float],
) -> dict[str, Any]:
    machinery = machinery_score(detections)
    layer = road_layer_score(detected_layer, layer_confidence)
    visual_features = feature_score(features)
    total_weight = MACHINERY_WEIGHT + ROAD_LAYER_WEIGHT + FEATURE_WEIGHT
    total = (
        machinery * MACHINERY_WEIGHT
        + layer * ROAD_LAYER_WEIGHT
        + visual_features * FEATURE_WEIGHT
    )
    normalized = total / total_weight if total_weight else 0.0
    return {
        "activity": ACTIVITY_NAME,
        "machinery_score": machinery,
        "road_layer_score": layer,
        "feature_score": visual_features,
        "total_score": total,
        "normalized_score": normalized,
        "activity_detected": normalized >= 0.35,
    }
