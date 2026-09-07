"""Computer-vision inference pipeline for Site Clearing."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml
from ultralytics import YOLO

try:
    from features.feature_extractor import extract_features
    from rules.activity_rules import calculate_activity_score
except ModuleNotFoundError:
    from .features.feature_extractor import extract_features
    from .rules.activity_rules import calculate_activity_score


# Purpose: Loads local models, detects machinery and road layers, extracts features, and scores Site Clearing.
# Use: Exposes run_inference for the unified dashboard, local API, and direct image analysis.

ROOT = Path(__file__).resolve().parent


# Logical block: reads and validates the activity configuration file.
def load_config() -> dict:
    with (ROOT / "config" / "config.yaml").open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError("Invalid Site Clearing YAML configuration")
    return config


# Logical block: loads the first local YOLO weight file for the requested model type.
def _model(kind: str) -> YOLO:
    candidates = [ROOT / "models" / kind, ROOT / "model" / kind]
    weights = sorted(
        weight
        for directory in candidates
        if directory.is_dir()
        for weight in directory.rglob("*.pt")
    )
    if not weights:
        locations = ", ".join(str(path) for path in candidates)
        raise FileNotFoundError(f"No local .pt {kind} model found. Searched: {locations}")
    return YOLO(str(weights[0]))


# Logical block: loads the machinery and road-layer YOLO models required by the pipeline.
def load_models() -> tuple[YOLO, YOLO]:
    return _model("machinery"), _model("road_layer")


# Logical block: normalizes model class-name mappings into integer-to-name dictionaries.
def _names(model: YOLO) -> dict[int, str]:
    return dict(enumerate(model.names)) if isinstance(model.names, list) else {int(key): str(value) for key, value in model.names.items()}


# Logical block: runs one configured prediction pass against an OpenCV image.
def _predict(model: YOLO, image: np.ndarray, config: dict) -> list:
    return model.predict(
        source=image,
        conf=float(config["inference"]["confidence_threshold"]),
        imgsz=int(config["inference"]["image_size"]),
        verbose=False,
    )


# Logical block: creates comparable names for machinery classes.
def _normalise(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


# Logical block: converts machinery model boxes into serializable detection dictionaries.
def detect_machinery(model: YOLO, image: np.ndarray, config: dict) -> list[dict]:
    results = _predict(model, image, config)
    if not results or results[0].boxes is None:
        return []
    boxes = results[0].boxes
    names = _names(model)
    return [
        {"name": names[int(class_id)], "confidence": float(confidence), "box": [float(value) for value in box]}
        for box, confidence, class_id in zip(
            boxes.xyxy.cpu().numpy(),
            boxes.conf.cpu().numpy(),
            boxes.cls.cpu().numpy(),
        )
    ]


# Logical block: keeps the highest confidence for every configured machinery class.
def summarize_machinery(detections: list[dict], required: list[str]) -> dict[str, float]:
    return {
        name: max(
            (detection["confidence"] for detection in detections if _normalise(detection["name"]) == _normalise(name)),
            default=0.0,
        )
        for name in required
    }


# Logical block: selects the highest-confidence road-layer prediction.
def detect_road_layer(model: YOLO, image: np.ndarray, config: dict) -> dict[str, str | float | None]:
    results = _predict(model, image, config)
    if not results or results[0].boxes is None or len(results[0].boxes) == 0:
        return {"detected": None, "confidence": 0.0}
    boxes = results[0].boxes
    index = int(boxes.conf.argmax().item())
    return {"detected": _names(model)[int(boxes.cls[index].item())], "confidence": float(boxes.conf[index].item())}


# Logical block: draws machine boxes and confidence labels on a copy of the source image.
def draw_detections(image: np.ndarray, detections: list[dict]) -> np.ndarray:
    output = image.copy()
    for detection in detections:
        x1, y1, x2, y2 = map(int, detection["box"])
        cv2.rectangle(output, (x1, y1), (x2, y2), (35, 180, 90), 2)
        cv2.putText(
            output,
            f'{detection["name"]} {detection["confidence"]:.2f}',
            (x1, max(18, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (35, 180, 90),
            2,
        )
    return output


# Logical block: executes the complete Site Clearing pipeline and returns dashboard-ready results.
def run_inference(image: str | Path | np.ndarray, save_results: bool = False) -> dict:
    config = load_config()
    original = cv2.imread(str(image)) if isinstance(image, (str, Path)) else image.copy()
    if original is None or not isinstance(original, np.ndarray) or original.size == 0:
        raise ValueError("Invalid or unreadable image")
    machinery_model, road_layer_model = load_models()
    detections = detect_machinery(machinery_model, original, config)
    road_layer = detect_road_layer(road_layer_model, original, config)
    features = extract_features(original, config["features"])
    machinery = summarize_machinery(detections, config["machinery"])
    scores = calculate_activity_score(machinery, road_layer["detected"], road_layer["confidence"], features)
    return {
        **scores,
        "machinery": machinery,
        "detections": detections,
        "road_layer": road_layer,
        "features": features,
        "processed_image": draw_detections(original, detections),
        "image": str(image) if isinstance(image, (str, Path)) else None,
    }


if __name__ == "__main__":
    print("Site Clearing inference module is ready.")
