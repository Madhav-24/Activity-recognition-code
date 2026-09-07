# Purpose: Implements the activity_recognition/activities/site_clearing/dashboard/app.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

"""Streamlit dashboard for the independent Site Clearing application."""

import sys
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

ACTIVITY_ROOT = Path(__file__).resolve().parents[1]
if str(ACTIVITY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACTIVITY_ROOT))

from inference import run_inference, load_config


config = load_config()
st.set_page_config(page_title="Site Clearing Monitoring", page_icon="[SC]", layout="wide")
st.title("AI ROAD CONSTRUCTION")
st.caption("Upload one CCTV frame for local machinery, road-layer, and visual-feature inference.")

uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "bmp"])
if uploaded is None:
    st.info("Choose an image to begin inference.")
    st.stop()

try:
    image = Image.open(uploaded).convert("RGB")
    image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    with st.spinner("Running Site Clearing inference..."):
        result = run_inference(image_bgr, save_results=config["output"].get("save_results", False))
except Exception as error:
    st.error(f"Inference failed: {error}")
    st.stop()

left, right = st.columns([1.35, 1])
with left:
    st.image(image, caption="Original image", use_container_width=True)
    st.image(cv2.cvtColor(result["processed_image"], cv2.COLOR_BGR2RGB), caption="Processed image", use_container_width=True)
with right:
    st.metric("Activity score", f'{result["normalized_score"]:.1%}')
    status = "SITE CLEARING DETECTED" if result["activity_detected"] else "SITE CLEARING NOT DETECTED"
    (st.success if result["activity_detected"] else st.warning)(status)
    st.subheader("Machinery detection")
    # Logical block: defines the def normalize_label and controls its related behavior.
    def normalize_label(label):
        return "".join(character for character in label.lower() if character.isalnum())

    machinery_rows = []
    for name, confidence in result["machinery"].items():
        count = sum(
            normalize_label(detection["name"]) == normalize_label(name)
            for detection in result["detections"]
        )
        machinery_rows.append({
            "Machinery": name,
            "Confidence": f"{confidence:.2f}",
            "Count": count,
        })
    st.dataframe(machinery_rows, hide_index=True, use_container_width=True)
    layer = result["road_layer"]
    st.subheader("Road layer")
    st.write(f'Detected: **{layer["detected"] or "None"}**')
    st.write(f'Confidence: **{layer["confidence"]:.2f}**')

st.subheader("Feature measurements")
st.dataframe([{"Feature": name.replace("_", " ").title(), "Value": f"{value:.4f}"} for name, value in result["features"].items()], hide_index=True, use_container_width=True)
st.subheader("Activity score components")
score_columns = st.columns(4)
for column, (label, key) in zip(score_columns, [("Machinery", "machinery_score"), ("Road layer", "road_layer_score"), ("Features", "feature_score"), ("Total", "total_score")]):
    column.metric(label, f'{result[key]:.3f}')
