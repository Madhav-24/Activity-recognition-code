"""
Rule engine for Site Clearing.

Required machinery:
    Bulldozer
    Excavator
    Loader

Required road layer:
    Soil

Features:
    Edge density
    Texture variance
    Green ratio
"""

# ============================================================
# CONFIGURATION
# ============================================================

ACTIVITY_NAME = "Site Clearing"

REQUIRED_MACHINERY = [
    "Bulldozer",
    "Excavator",
    "Loader"
]

REQUIRED_ROAD_LAYER = "soil"

FEATURES_USED = [
    "edge_density",
    "texture_variance",
    "green_ratio"
]

# Weights
MACHINERY_WEIGHT = 3.0
ROAD_LAYER_WEIGHT = 3.0
FEATURE_WEIGHT = 1.0


# ============================================================
# MACHINERY SCORE
# ============================================================

def machinery_score(detections):
    """
    Calculate normalized machinery score.

    def machinery_score(detections: dict[str, float], required: list[str]) -> float:
    detection confidence.
    def machinery_score(detections: dict[str, float], required: list[str]) -> float:
    Example:

        Bulldozer = 0.90
        Excavator = 0.80
        Loader = 0.70

    Average confidence:

        (0.90 + 0.80 + 0.70) / 3
        = 0.80
    """

    if not detections:
        return 0.0

    total = 0.0
        if not required:
            return 0.0
        return sum(_bounded(detections.get(name, 0.0)) for name in required) / len(required)
        )
        total += confidence
    return total / len(REQUIRED_MACHINERY)


        if detected_layer is None or detected_layer.strip().lower() != required.strip().lower():
            return 0.0
        return _bounded(confidence)
# ============================================================

def road_layer_score(
    detected_layer,
    confidence=1.0
    def road_layer_score(detected_layer: str | None, confidence: float, required: str) -> float:
    """

    if detected_layer is None:
        return 0.0

    if (
        str(detected_layer).strip().lower()
        ==
        REQUIRED_ROAD_LAYER.lower()
    ):

        confidence = max(
            0.0,
            min(float(confidence), 1.0)
        )

        return confidence

    return 0.0


# ============================================================
# FEATURE SCORE
# ============================================================

def feature_score(features):
    """
    Calculate normalized visual-feature score.
    def feature_score(features: dict[str, float], normalization: dict[str, float]) -> float:
    Features:

        edge_density
        texture_variance
        green_ratio

    Final value is between 0 and 1.
    """

    if not features:
        return 0.0

    components = []


    # --------------------------------------------------------
    # EDGE DENSITY
    # --------------------------------------------------------

    if "edge_density" in FEATURES_USED:

        edge_density = float(
            features.get(
                "edge_density",
                0.0
            )
        )

        # Lower edge density supports
        # relatively open/cleared surfaces.

        edge_component = max(
            0.0,
            1.0 - min(
                edge_density / 0.30,
                1.0
            )
        )

        components.append(
            edge_component
        )


    # --------------------------------------------------------
    # TEXTURE VARIANCE
    # --------------------------------------------------------

    if "texture_variance" in FEATURES_USED:

        texture = float(
            features.get(
                "texture_variance",
                0.0
            )
        )

        texture_component = min(
            texture / 5000.0,
            1.0
        )

        components.append(
            texture_component
        )


    # --------------------------------------------------------
    # GREEN RATIO
    # --------------------------------------------------------

    if "green_ratio" in FEATURES_USED:

        green_ratio = float(
            features.get(
    def calculate_activity_score(
        detections: dict[str, float],
        detected_layer: str | None,
        layer_confidence: float,
        features: dict[str, float],
        config: dict[str, Any],
    ) -> dict[str, Any]:
            0.0,
            min(
                green_ratio,
                1.0
            )
        )

        components.append(
            green_component
        )


    if not components:
        return 0.0

    def calculate_activity_score(
        detections: dict[str, float],
        detected_layer: str | None,
        layer_confidence: float,
        features: dict[str, float],
        config: dict[str, Any],
    ) -> dict[str, Any]:

def calculate_activity_score(
    detections,
    detected_layer,
        weights = [float(scoring[key]) for key in ("machinery_weight", "road_layer_weight", "feature_weight")]
        total = machinery * weights[0] + layer * weights[1] + feature * weights[2]
    """
    Calculate the Site Clearing activity score.

    Components:



    l_score = road_layer_score(
        detected_layer,
        normalized = total / sum(weights) if sum(weights) else 0.0
    f_score = feature_score(
        features
    )


    # --------------------------------------------------------
    # WEIGHTED SCORE
    # --------------------------------------------------------

    weighted_machinery = (
        m_score * MACHINERY_WEIGHT
    )

    weighted_layer = (
        l_score * ROAD_LAYER_WEIGHT
    )

    weighted_features = (
        f_score * FEATURE_WEIGHT
    )


    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total_weight = (
        MACHINERY_WEIGHT
        +
        ROAD_LAYER_WEIGHT
        +
        FEATURE_WEIGHT
    )

    total_score = (
        weighted_machinery
        +
        weighted_layer
        +
        weighted_features
    )

    # Normalize to 0-1

    normalized_score = (
        total_score / total_weight
    )


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {

        "activity": ACTIVITY_NAME,

        "machinery_score":
            float(m_score),

        "road_layer_score":
            float(l_score),

        "feature_score":
            float(f_score),

        "weighted_machinery_score":
            float(weighted_machinery),

        "weighted_road_layer_score":
            float(weighted_layer),

        "weighted_feature_score":
            float(weighted_features),

        "total_score":
            float(total_score),

        "normalized_score":
            float(normalized_score)
    }