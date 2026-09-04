"""
Inference pipeline for Site Clearing.

Pipeline:

    Image
      ↓
    Machinery model
      ↓
    Road-layer model
      ↓
    Activity-specific features
      ↓
    Rule engine
      ↓
    Activity score
"""

from pathlib import Path
import cv2
import yaml

from features.feature_extractor import (
    extract_features
)

from rules.activity_rules import (
    calculate_activity_score
)


BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = (
    BASE_DIR
    / "config"
    / "config.yaml"
)


def load_config():

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return yaml.safe_load(f)


def process_image(
    image_path,
    machinery_detections,
    road_layer,
    road_layer_confidence
):
    """
    Process one image after model inference.

    machinery_detections:
        dictionary containing machinery
        confidence values.

    Example:

    {
        "Excavator": 0.91,
        "Dump Truck": 0.84
    }
    """

    image = cv2.imread(
        str(image_path)
    )


    if image is None:

        raise FileNotFoundError(
            f"Could not read image: {image_path}"
        )


    features = extract_features(
        image
    )


    result = calculate_activity_score(
        detections=machinery_detections,
        detected_layer=road_layer,
        layer_confidence=road_layer_confidence,
        features=features
    )


    result["features"] = features

    result["road_layer"] = road_layer

    result["road_layer_confidence"] = (
        road_layer_confidence
    )

    result["image"] = str(
        image_path
    )


    return result


if __name__ == "__main__":

    print(
        "Site Clearing inference module"
    )

    print(
        "Model loading and camera integration "
        "can be connected here."
    )
