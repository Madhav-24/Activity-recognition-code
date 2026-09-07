# Purpose: Implements the activity_recognition/activities/site_clearing/features/feature_extractor.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

import cv2
import numpy as np


# ============================================================
# EDGE DENSITY
# ============================================================

# Logical block: defines the def calculate_edge_density and controls its related behavior.
def calculate_edge_density(image):
    """
    Calculate edge density using Canny edge detection.

    Returns:
        float: Ratio of edge pixels to total pixels.
    """

    if image is None:
        return 0.0

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    total_pixels = edges.size

    if total_pixels == 0:
        return 0.0

    edge_pixels = np.count_nonzero(edges)

    return float(
        edge_pixels / total_pixels
    )


# ============================================================
# TEXTURE VARIANCE
# ============================================================

# Logical block: defines the def calculate_texture_variance and controls its related behavior.
def calculate_texture_variance(image):
    """
    Calculate grayscale intensity variance.

    Higher values generally indicate greater
    local intensity variation / texture.

    Returns:
        float: Grayscale intensity variance.
    """

    if image is None:
        return 0.0

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        np.var(gray)
    )


# ============================================================
# GREEN RATIO
# ============================================================

# Logical block: defines the def calculate_green_ratio and controls its related behavior.
def calculate_green_ratio(image):
    """
    Calculate the ratio of green pixels in the image.

    HSV segmentation is used to estimate
    vegetation/green surface coverage.

    Returns:
        float: Green pixel ratio between 0 and 1.
    """

    if image is None:
        return 0.0

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # HSV range for green vegetation
    lower_green = np.array(
        [35, 40, 40],
        dtype=np.uint8
    )

    upper_green = np.array(
        [90, 255, 255],
        dtype=np.uint8
    )

    green_mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    total_pixels = green_mask.size

    if total_pixels == 0:
        return 0.0

    green_pixels = np.count_nonzero(
        green_mask
    )

    return float(
        green_pixels / total_pixels
    )


# ============================================================
# FEATURE EXTRACTION
# ============================================================

# Logical block: defines the def extract_features and controls its related behavior.
def extract_features(
    image,
    enabled_features=None
):
    """
    Extract only the requested activity-specific
    visual features.

    Args:
        image:
            OpenCV BGR image.

        enabled_features:
            List of feature names to calculate.

            Example:
                [
                    "edge_density",
                    "texture_variance",
                    "green_ratio"
                ]

            If None, all supported features are calculated.

    Returns:
        dict:
            Dictionary containing only the requested features.
    """

    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("A non-empty OpenCV image is required")

    if enabled_features is None:

        enabled_features = [
            "edge_density",
            "texture_variance",
            "green_ratio"
        ]

    features = {}


    # --------------------------------------------------------
    # EDGE DENSITY
    # --------------------------------------------------------

    if "edge_density" in enabled_features:

        features["edge_density"] = (
            calculate_edge_density(image)
        )


    # --------------------------------------------------------
    # TEXTURE VARIANCE
    # --------------------------------------------------------

    if "texture_variance" in enabled_features:

        features["texture_variance"] = (
            calculate_texture_variance(image)
        )


    # --------------------------------------------------------
    # GREEN RATIO
    # --------------------------------------------------------

    if "green_ratio" in enabled_features:

        features["green_ratio"] = (
            calculate_green_ratio(image)
        )


    return features