"""Purpose: Standalone Streamlit dashboard for Piling recognition.
Use: Upload an image, run the local Piling computer-vision pipeline, and review its results.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

ACTIVITY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ACTIVITY_ROOT))
from inference import run_inference  # noqa: E402

st.set_page_config(page_title="Piling Activity Recognition", page_icon="L&T", layout="wide")
st.title("L&T | PILING ACTIVITY RECOGNITION")
st.caption("Standalone computer-vision analysis for Piling work")
st.divider()

uploaded = st.file_uploader("Upload a road-construction image", type=["jpg", "jpeg", "png"])
if uploaded is None:
    st.info("Upload a Piling image to begin analysis.")
    st.stop()

try:
    preview = Image.open(uploaded).convert("RGB")
except Exception as error:
    st.error(f"Invalid image: {error}")
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("Original image")
    st.image(preview, use_container_width=True)
with right:
    st.subheader("Analysis")
    analyze = st.button("Analyze Image", type="primary", use_container_width=True)
    st.caption("Required road layer: Soil | Machinery: Piling Rig")

if not analyze:
    st.stop()

image_bgr = cv2.cvtColor(np.asarray(preview), cv2.COLOR_RGB2BGR)
with st.spinner("Running Piling models..."):
    try:
        result = run_inference(image_bgr)
    except Exception as error:
        st.error(f"Analysis failed: {error}")
        st.stop()

score = float(result.get("normalized_score", result.get("total_score", 0.0)))
st.success(f"DETECTED ACTIVITY: {result.get('activity', 'Piling')}")
st.metric("Confidence / Activity Score", f"{score:.3f}")

st.subheader("Analyzed image")
st.image(cv2.cvtColor(result["processed_image"], cv2.COLOR_BGR2RGB), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Machinery detections")
    st.dataframe(pd.DataFrame([{"Machinery": name, "Confidence": f"{confidence:.3f}"} for name, confidence in result.get("machinery", {}).items()]), hide_index=True, use_container_width=True)
with col2:
    st.subheader("Road layer detection")
    st.metric("Detected layer", result.get("road_layer", {}).get("detected") or "None")
    st.metric("Confidence", f"{result.get('road_layer', {}).get('confidence', 0.0):.3f}")

st.subheader("Visual indicators")
feature_columns = st.columns(max(1, min(4, len(result.get("features", {})))))
for column, (name, value) in zip(feature_columns, result.get("features", {}).items()):
    column.metric(name.replace("_", " ").title(), f"{value:.4f}")

st.subheader("Score components")
score_columns = st.columns(4)
for column, label, key in zip(score_columns, ("Machinery", "Road Layer", "Features", "Total"), ("machinery_score", "road_layer_score", "feature_score", "total_score")):
    column.metric(label, f"{result.get(key, 0.0):.3f}")
