# Purpose: Implements the activity_recognition/dashboard/app.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

"""Unified dashboard for all independent road-construction activity pipelines."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ACTIVITIES = [
    ("site_clearing", "Site Clearing"),
    ("excavation", "Excavation / Earthwork"),
    ("land_grading", "Land Grading"),
    ("subgrade_preparation", "Subgrade Preparation"),
    ("gsb_laying", "GSB Laying"),
    ("wmm_laying", "WMM Laying"),
    ("asphalt_paving", "Asphalt Paving"),
]


# Logical block: defines the def _load_activity_module and controls its related behavior.
def _load_activity_module(activity_id: str) -> ModuleType:
    """Load one activity's inference module with its local feature/rule imports."""
    activity_root = PROJECT_ROOT / "activities" / activity_id
    module_name = f"unified_{activity_id}_inference"
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


# Logical block: defines the def analyze_all and controls its related behavior.
def analyze_all(image: np.ndarray) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
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
    return results, errors


# Logical block: defines the def score_table and controls its related behavior.
def score_table(results: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append({
            "Activity": result["activity"],
            "Machinery Score": result.get("machinery_score", 0.0),
            "Road Layer Score": result.get("road_layer_score", 0.0),
            "Feature Score": result.get("feature_score", 0.0),
            "Total Score": result.get("total_score", 0.0),
        })
    return pd.DataFrame(rows).sort_values("Total Score", ascending=False).reset_index(drop=True)


# Logical block: defines the def _feature_cards and controls its related behavior.
def _feature_cards(features: dict[str, Any]) -> None:
    columns = st.columns(min(max(len(features), 1), 4))
    for column, (name, value) in zip(columns, features.items()):
        label = name.replace("_", " ").title()
        column.metric(label, f"{value:.4f}")


st.set_page_config(page_title="AI Road Construction Monitoring", page_icon="[AI]", layout="wide")
st.title("AI ROAD CONSTRUCTION ACTIVITY MONITORING")
st.caption("Multi-Activity Computer Vision Analysis")
st.divider()

uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
if uploaded is None:
    st.info("Upload a construction-site image to preview it before analysis.")
    st.stop()

try:
    preview = Image.open(uploaded).convert("RGB")
except Exception as error:
    st.error(f"Invalid image: {error}")
    st.stop()

st.subheader("Image preview")
st.image(preview, use_container_width=True)
analyze = st.button("Analyze Image", type="primary", use_container_width=True)
if not analyze:
    st.stop()

image_bgr = cv2.cvtColor(np.asarray(preview), cv2.COLOR_RGB2BGR)
with st.spinner("Running all 7 activity pipelines..."):
    activity_results, activity_errors = analyze_all(image_bgr)

if not activity_results:
    st.error("No activity pipeline completed successfully.")
    for error in activity_errors:
        st.write(f'**{error["activity"]}:** {error["error"]}')
    st.stop()

ranked = score_table(activity_results)
best_activity = ranked.iloc[0]["Activity"]
best_score = float(ranked.iloc[0]["Total Score"])

st.success(f"DETECTED ACTIVITY: {best_activity}")
st.metric("Confidence / Activity Score", f"{best_score:.3f}")
st.caption("The detected activity is selected from the highest complete rule-engine score.")

st.subheader("Activity score comparison")
chart_data = ranked.set_index("Activity")[["Total Score"]]
st.bar_chart(chart_data, horizontal=True, color="#149c88")
st.dataframe(ranked.style.format({
    "Machinery Score": "{:.3f}",
    "Road Layer Score": "{:.3f}",
    "Feature Score": "{:.3f}",
    "Total Score": "{:.3f}",
}), hide_index=True, use_container_width=True)

if activity_errors:
    with st.expander("Pipelines that could not be completed"):
        for error in activity_errors:
            st.warning(f'{error["activity"]}: {error["error"]}')

winner = next(result for result in activity_results if result["activity"] == best_activity)
st.subheader("Machinery detections")
st.image(cv2.cvtColor(winner["processed_image"], cv2.COLOR_BGR2RGB), caption=f"Annotated output from {best_activity}", use_container_width=True)
st.dataframe(pd.DataFrame([
    {"Machinery": name, "Confidence": f"{confidence:.3f}", "Count": sum(
        "".join(character for character in detection["name"].lower() if character.isalnum())
        == "".join(character for character in name.lower() if character.isalnum())
        for detection in winner.get("detections", [])
    )}
    for name, confidence in winner.get("machinery", {}).items()
]), hide_index=True, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Road layer")
    st.metric("Detected Road Layer", winner["road_layer"].get("detected") or "None")
    st.metric("Road Layer Confidence", f'{winner["road_layer"].get("confidence", 0.0):.3f}')
with right:
    st.subheader("Visual features")
    _feature_cards(winner.get("features", {}))

st.subheader("Winning activity score components")
score_columns = st.columns(4)
for column, label, key in zip(
    score_columns,
    ("Machinery", "Road Layer", "Features", "Total"),
    ("machinery_score", "road_layer_score", "feature_score", "total_score"),
):
    column.metric(label, f'{winner.get(key, 0.0):.3f}')
