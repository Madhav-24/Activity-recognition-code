# Purpose: Implements the activity_recognition/activities/land_grading/features/feature_extractor.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

import cv2, numpy as np
# Logical block: defines the def calculate_edge_density and controls its related behavior.
def calculate_edge_density(image): return float(np.count_nonzero(cv2.Canny(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY),100,200))/image.shape[0]/image.shape[1])
# Logical block: defines the def calculate_texture_variance and controls its related behavior.
def calculate_texture_variance(image): return float(np.var(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)))
# Logical block: defines the def calculate_green_ratio and controls its related behavior.
def calculate_green_ratio(image):
 hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV); return float(np.count_nonzero(cv2.inRange(hsv,np.array([35,40,40]),np.array([90,255,255])))/image.shape[0]/image.shape[1])
# Logical block: defines the def calculate_surface_uniformity and controls its related behavior.
def calculate_surface_uniformity(image): return float(max(0.0,1.0-np.std(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY))/128.0))
# Logical block: defines the def _norm and controls its related behavior.
def _norm(v): return ''.join(c for c in v.lower() if c.isalnum())
# Logical block: defines the def machinery_proximity and controls its related behavior.
def machinery_proximity(detections,width,height):
 diagonal=float(np.hypot(width,height)); left=[d['box'] for d in detections if _norm(d['name'])=='excavator']; right=[d['box'] for d in detections if _norm(d['name'])=='dumptruck']
 if not left or not right or diagonal<=0:return 0.0
 distances=[]
 for a in left:
  for b in right:
   ac=((a[0]+a[2])/2,(a[1]+a[3])/2); bc=((b[0]+b[2])/2,(b[1]+b[3])/2); distances.append(float(np.hypot(ac[0]-bc[0],ac[1]-bc[1])))
 return max(0.0,1.0-min(distances)/diagonal)
# Logical block: defines the def extract_features and controls its related behavior.
def extract_features(image,enabled_features=None):
 if not isinstance(image,np.ndarray) or image.size==0: raise ValueError('A non-empty OpenCV image is required')
 result={}
 for name in enabled_features or ['edge_density','texture_variance']:
  if name=='edge_density':result[name]=calculate_edge_density(image)
  elif name=='texture_variance':result[name]=calculate_texture_variance(image)
  elif name=='green_ratio':result[name]=calculate_green_ratio(image)
  elif name=='surface_uniformity':result[name]=calculate_surface_uniformity(image)
 return result
