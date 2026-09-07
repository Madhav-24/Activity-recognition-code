# Purpose: Implements the activity_recognition/activities/land_grading/dashboard/app.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

import sys
from pathlib import Path
import cv2,numpy as np,streamlit as st
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from inference import load_config,run_inference
c=load_config(); st.set_page_config(page_title=c['activity']['name'],layout='wide')
uploaded=st.file_uploader('Upload image',type=['jpg','jpeg','png','bmp'])
if uploaded is None: st.info('Choose an image to begin inference.'); st.stop()
try:
 original=Image.open(uploaded).convert('RGB'); result=run_inference(cv2.cvtColor(np.array(original),cv2.COLOR_RGB2BGR))
except Exception as error: st.error(f'Inference failed: {error}'); st.stop()
a,b=st.columns(2)
with a: st.image(original,caption='Original image',use_container_width=True); st.image(cv2.cvtColor(result['processed_image'],cv2.COLOR_BGR2RGB),caption='Processed image',use_container_width=True)
with b:
 activity_name = result['activity'].upper()
 st.metric('Activity score',f"{result['normalized_score']:.1%}"); (st.success if result['activity_detected'] else st.warning)(f"{activity_name} DETECTED" if result['activity_detected'] else f"{activity_name} NOT DETECTED")
 st.subheader('Machinery'); st.dataframe([{'Machinery':n,'Confidence':f'{v:.2f}','Count':sum(''.join(c for c in d['name'].lower() if c.isalnum())==''.join(c for c in n.lower() if c.isalnum()) for d in result['detections'])} for n,v in result['machinery'].items()],hide_index=True,use_container_width=True)
 st.subheader('Road layer'); st.write(f"Detected: **{result['road_layer']['detected'] or 'None'}**"); st.write(f"Confidence: **{result['road_layer']['confidence']:.2f}**")
st.subheader('Features'); st.dataframe([{'Feature':n.replace('_',' ').title(),'Value':f'{v:.4f}'} for n,v in result['features'].items()],hide_index=True,use_container_width=True)
st.subheader('Score components'); st.dataframe([{'Component':n,'Score':f'{result[k]:.3f}'} for n,k in [('Machinery','machinery_score'),('Road layer','road_layer_score'),('Features','feature_score'),('Total','total_score')]],hide_index=True,use_container_width=True)
