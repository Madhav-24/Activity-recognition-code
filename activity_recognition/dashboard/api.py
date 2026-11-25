# Purpose: Implements the activity_recognition/dashboard/api.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

"""Local HTTP API for the activity-recognition HTML dashboard."""

from __future__ import annotations

import base64
import importlib.util
import sys
from pathlib import Path
from threading import Lock
from typing import Any

import cv2
import numpy as np
from flask import Flask, jsonify, request, send_from_directory

DASHBOARD_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = DASHBOARD_ROOT.parent
ACTIVITIES = [
    ("site_clearing", "Site Clearing"),
    ("excavation", "Excavation / Earthwork"),
    ("land_grading", "Land Grading"),
    ("subgrade_preparation", "Subgrade Preparation"),
    ("gsb_laying", "GSB Laying"),
    ("wmm_laying", "WMM Laying"),
    ("asphalt_paving", "Asphalt Paving"),
]
INFERENCE_LOCK = Lock()
app = Flask(__name__, static_folder=str(DASHBOARD_ROOT), static_url_path="")


# Logical block: defines the def _load_activity_module and controls its related behavior.
def _load_activity_module(activity_id: str):
    activity_root = PROJECT_ROOT / "activities" / activity_id
    module_name = f"api_{activity_id}_inference"
    for name in ("inference", "features", "features.feature_extractor", "rules", "rules.activity_rules"):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(activity_root))
    try:
        spec = importlib.util.spec_from_file_location(module_name, activity_root / "inference.py")
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load inference module for {activity_id}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(activity_root))


# Logical block: defines the def _normalise and controls its related behavior.
def _normalise(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


# Logical block: defines the def _json_value and controls its related behavior.
def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    return value


# Logical block: defines the def _machinery_rows and controls its related behavior.
def _machinery_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    detections = result.get("detections", [])
    rows = []
    for name, confidence in result.get("machinery", {}).items():
        matching = [item for item in detections if _normalise(item["name"]) == _normalise(name)]
        rows.append({"name": name, "count": len(matching), "confidence": float(confidence)})
    return rows


# Logical block: defines the def _image_data and controls its related behavior.
def _image_data(image: np.ndarray) -> str:
    success, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not success:
        raise ValueError("Could not encode analyzed image")
    return "data:image/jpeg;base64," + base64.b64encode(encoded).decode("ascii")


# Logical block: defines the def _dashboard_features and controls its related behavior.
def _dashboard_features(image: np.ndarray, detections: list[dict[str, Any]]) -> dict[str, float]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([90, 255, 255]))
    edge_density = float(np.count_nonzero(cv2.Canny(gray, 100, 200)) / image.shape[0] / image.shape[1])
    diagonal = float(np.hypot(image.shape[1], image.shape[0]))
    excavators = [item["box"] for item in detections if _normalise(item["name"]) == "excavator"]
    trucks = [item["box"] for item in detections if _normalise(item["name"]) == "dumptruck"]
    proximity = 0.0
    if excavators and trucks and diagonal > 0:
        distances = []
        for left in excavators:
            for right in trucks:
                left_center = ((left[0] + left[2]) / 2, (left[1] + left[3]) / 2)
                right_center = ((right[0] + right[2]) / 2, (right[1] + right[3]) / 2)
                distances.append(float(np.hypot(left_center[0] - right_center[0], left_center[1] - right_center[1])))
        proximity = max(0.0, 1.0 - min(distances) / diagonal)
    return {
        "green_ratio": float(np.count_nonzero(green_mask) / image.shape[0] / image.shape[1] * 100),
        "texture_variance": float(np.var(gray)),
        "edge_density": edge_density,
        "machinery_proximity": proximity,
    }


# Logical block: defines the def analyse and controls its related behavior.
def analyse(image: np.ndarray) -> dict[str, Any]:
    results = []
    errors = []
    for activity_id, activity_name in ACTIVITIES:
        try:
            module = _load_activity_module(activity_id)
            result = module.run_inference(image)
            result["activity_id"] = activity_id
            result["activity"] = activity_name
            results.append(result)
        except Exception as error:
            errors.append({"activity": activity_name, "error": str(error)})
    if not results:
        raise RuntimeError("No activity pipeline completed successfully")

    ranked = sorted(results, key=lambda item: item.get("normalized_score", item.get("total_score", 0.0)), reverse=True)
    winner = ranked[0]
    result_by_id = {item["activity_id"]: item for item in results}
    return {
        "activities": [{
            "activity": activity_name,
            "activity_id": activity_id,
            "machinery_score": float(result_by_id[activity_id].get("machinery_score", 0.0)) if activity_id in result_by_id else 0.0,
            "road_layer_score": float(result_by_id[activity_id].get("road_layer_score", 0.0)) if activity_id in result_by_id else 0.0,
            "feature_score": float(result_by_id[activity_id].get("feature_score", 0.0)) if activity_id in result_by_id else 0.0,
            "total_score": float(result_by_id[activity_id].get("total_score", 0.0)) if activity_id in result_by_id else 0.0,
            "score": float(result_by_id[activity_id].get("normalized_score", result_by_id[activity_id].get("total_score", 0.0))) if activity_id in result_by_id else 0.0,
            "activity_detected": bool(result_by_id[activity_id].get("activity_detected", False)) if activity_id in result_by_id else False,
            "status": "Analyzed" if activity_id in result_by_id else "Unavailable",
        } for activity_id, activity_name in ACTIVITIES],
        "winner": {
            "activity": winner["activity"],
            "score": float(winner.get("normalized_score", winner.get("total_score", 0.0))),
            "road_layer": _json_value(winner.get("road_layer", {})),
            "machinery": _machinery_rows(winner),
            "detections": _json_value(winner.get("detections", [])),
            "features": _dashboard_features(image, winner.get("detections", [])),
            "analyzed_image": _image_data(winner["processed_image"]),
        },
        "errors": errors,
    }


@app.get("/")
# Logical block: defines the def dashboard and controls its related behavior.
def dashboard():
    return send_from_directory(DASHBOARD_ROOT, "index.html")


@app.post("/api/analyze")
# Logical block: defines the def analyze_endpoint and controls its related behavior.
def analyze_endpoint():
    uploaded = request.files.get("image")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "Upload a JPG, JPEG, or PNG image."}), 400
    image = cv2.imdecode(np.frombuffer(uploaded.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return jsonify({"error": "The uploaded file is not a readable image."}), 400
    try:
        with INFERENCE_LOCK:
            return jsonify(analyse(image))
    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
