def _bound(v): return max(0.0,min(float(v),1.0))
def machinery_score(detections,required): return sum(_bound(detections.get(n,0)) for n in required)/len(required) if required else 0.0
def road_layer_score(detected,confidence,required): return _bound(confidence) if detected and detected.strip().lower()==required.strip().lower() else 0.0
def feature_score(features,norm):
 values=[]
 for n,v in features.items():
  if n=='edge_density': values.append(1-min(float(v)/norm.get('edge_density_max',.3),1))
  elif n=='texture_variance': values.append(min(max(float(v)/norm.get('texture_variance_max',5000),0),1))
  else: values.append(_bound(v))
 return sum(values)/len(values) if values else 0.0
def calculate_activity_score(detections,detected_layer,layer_confidence,features,config):
 s=config['scoring']; parts=(machinery_score(detections,config['machinery']),road_layer_score(detected_layer,layer_confidence,config['road_layer']['required']),feature_score(features,s['feature_normalization'])); weights=[float(s[k]) for k in ('machinery_weight','road_layer_weight','feature_weight')]; total=sum(a*b for a,b in zip(parts,weights)); normalized=total/sum(weights) if sum(weights) else 0.0
 return {'activity':config['activity']['name'],'machinery_score':parts[0],'road_layer_score':parts[1],'feature_score':parts[2],'total_score':total,'normalized_score':normalized,'activity_detected':normalized>=float(s['detection_threshold'])}
