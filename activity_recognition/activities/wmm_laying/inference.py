# Purpose: Implements the activity_recognition/activities/wmm_laying/inference.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

from pathlib import Path
import cv2,yaml,numpy as np
from ultralytics import YOLO
try:
 from features.feature_extractor import extract_features,machinery_proximity
 from rules.activity_rules import calculate_activity_score
except ModuleNotFoundError:
 from .features.feature_extractor import extract_features,machinery_proximity
 from .rules.activity_rules import calculate_activity_score
ROOT=Path(__file__).resolve().parent
# Logical block: defines the def load_config and controls its related behavior.
def load_config():
 with (ROOT/'config/config.yaml').open(encoding='utf-8') as f: config=yaml.safe_load(f)
 if not isinstance(config,dict): raise ValueError('Invalid YAML configuration')
 return config
# Logical block: defines the def _model and controls its related behavior.
def _model(kind):
 candidates=[ROOT/'models'/kind,ROOT/'model'/kind]; weights=sorted(f for d in candidates if d.is_dir() for f in d.rglob('*.pt'))
 if not weights: raise FileNotFoundError(f'No local .pt {kind} model found. Searched: {", ".join(map(str,candidates))}')
 return YOLO(str(weights[0]))
# Logical block: defines the def load_models and controls its related behavior.
def load_models(): return _model('machinery'),_model('road_layer')
# Logical block: defines the def _names and controls its related behavior.
def _names(model): return dict(enumerate(model.names)) if isinstance(model.names,list) else {int(k):str(v) for k,v in model.names.items()}
# Logical block: defines the def _predict and controls its related behavior.
def _predict(model,image,c): return model.predict(source=image,conf=float(c['inference']['confidence_threshold']),imgsz=int(c['inference']['image_size']),verbose=False)
# Logical block: defines the def _norm and controls its related behavior.
def _norm(v): return ''.join(c for c in v.lower() if c.isalnum())
# Logical block: defines the def detect_machinery and controls its related behavior.
def detect_machinery(model,image,c):
 r=_predict(model,image,c)
 if not r or r[0].boxes is None:return []
 b=r[0].boxes; names=_names(model); return [{'name':names[int(k)],'confidence':float(q),'box':[float(x) for x in box]} for box,q,k in zip(b.xyxy.cpu().numpy(),b.conf.cpu().numpy(),b.cls.cpu().numpy())]
# Logical block: defines the def summarize_machinery and controls its related behavior.
def summarize_machinery(detections,required): return {n:max((d['confidence'] for d in detections if _norm(d['name'])==_norm(n)),default=0.0) for n in required}
# Logical block: defines the def detect_road_layer and controls its related behavior.
def detect_road_layer(model,image,c):
 r=_predict(model,image,c)
 if not r or r[0].boxes is None or len(r[0].boxes)==0:return {'detected':None,'confidence':0.0}
 b=r[0].boxes; i=int(b.conf.argmax().item()); return {'detected':_names(model)[int(b.cls[i].item())],'confidence':float(b.conf[i].item())}
# Logical block: defines the def draw_detections and controls its related behavior.
def draw_detections(image,detections):
 out=image.copy()
 for d in detections:
  x1,y1,x2,y2=map(int,d['box']); cv2.rectangle(out,(x1,y1),(x2,y2),(35,180,90),2); cv2.putText(out,f"{d['name']} {d['confidence']:.2f}",(x1,max(18,y1-5)),cv2.FONT_HERSHEY_SIMPLEX,.55,(35,180,90),2)
 return out
# Logical block: defines the def run_inference and controls its related behavior.
def run_inference(image,save_results=False):
 c=load_config(); original=cv2.imread(str(image)) if isinstance(image,(str,Path)) else image.copy()
 if original is None or not isinstance(original,np.ndarray) or original.size==0: raise ValueError('Invalid or unreadable image')
 mm,rm=load_models(); detections=detect_machinery(mm,original,c); layer=detect_road_layer(rm,original,c); features=extract_features(original,c['features'])
 if 'excavator_dump_truck_proximity' in c['features']: features['excavator_dump_truck_proximity']=machinery_proximity(detections,original.shape[1],original.shape[0])
 machinery=summarize_machinery(detections,c['machinery']); scores=calculate_activity_score(machinery,layer['detected'],layer['confidence'],features,c)
 return {**scores,'machinery':machinery,'detections':detections,'road_layer':layer,'features':features,'processed_image':draw_detections(original,detections),'image':str(image) if isinstance(image,(str,Path)) else None}
