# Purpose: Implements the activity_recognition/activities/asphalt_paving/rules/activity_rules.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

def _bound(v): return max(0.0,min(float(v),1.0))
# Logical block: defines the def machinery_score and controls its related behavior.
def machinery_score(detections,required): return sum(_bound(detections.get(n,0)) for n in required)/len(required) if required else 0.0
# Logical block: defines the def road_layer_score and controls its related behavior.
def road_layer_score(detected,confidence,required): return _bound(confidence) if detected and detected.strip().lower()==required.strip().lower() else 0.0
# Logical block: defines the def feature_score and controls its related behavior.
def feature_score(features,norm):
 values=[]
 for n,v in features.items():
  if n=='edge_density': values.append(1-min(float(v)/norm.get('edge_density_max',.3),1))
  elif n=='texture_variance': values.append(min(max(float(v)/norm.get('texture_variance_max',5000),0),1))
  else: values.append(_bound(v))
 return sum(values)/len(values) if values else 0.0
# Logical block: defines the def _normalized and controls its related behavior.
def _normalized(label):
 return ''.join(c for c in label.lower() if c.isalnum())

# Logical block: defines the def special_score and controls its related behavior.
def special_score(detections,detected_layer,layer_confidence,features,required_layer):
 confidences={}
 for detection in detections:
    label=_normalized(detection['name'])
    confidences[label]=max(confidences.get(label,0.0),float(detection['confidence']))
 indicators=[road_layer_score(detected_layer,layer_confidence,required_layer),_bound(confidences.get('roller',0.0)),_bound(confidences.get('asphaltpaver',0.0)),_bound(features.get('surface_uniformity',0.0)),max(0.0,1.0-min(float(features.get('edge_density',1.0))/0.30,1.0))]
 return sum(indicators)/len(indicators)

# Logical block: defines the def calculate_activity_score and controls its related behavior.
def calculate_activity_score(detections,detected_layer,layer_confidence,features,config):
 s=config['scoring']; parts=(machinery_score(detections,config['machinery']),road_layer_score(detected_layer,layer_confidence,config['road_layer']['required']),feature_score(features,s['feature_normalization']))
 special=special_score(detections,detected_layer,layer_confidence,features,config['road_layer']['required'])
 weights=[float(s[k]) for k in ('machinery_weight','road_layer_weight','feature_weight','special_weight')]; total=sum(a*b for a,b in zip(parts,weights[:3]))+special*weights[3]; normalized=total/sum(weights) if sum(weights) else 0.0
 return {'activity':config['activity']['name'],'machinery_score':parts[0],'road_layer_score':parts[1],'feature_score':parts[2],'special_feature_score':special,'total_score':total,'normalized_score':normalized,'activity_detected':normalized>=float(s['detection_threshold'])}
