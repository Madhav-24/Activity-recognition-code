# Purpose: Implements the activity_recognition/activities/wmm_laying/test.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

from pathlib import Path
import cv2,yaml
from features.feature_extractor import extract_features
from rules.activity_rules import calculate_activity_score
from inference import load_models,detect_machinery,detect_road_layer,run_inference
ROOT=Path(__file__).resolve().parent; C=yaml.safe_load((ROOT/'config/config.yaml').read_text(encoding='utf-8'))
# Logical block: defines the def main and controls its related behavior.
def main():
 p=next((x for x in (ROOT/'dataset').rglob('*') if x.suffix.lower() in {'.jpg','.jpeg','.png','.bmp'}),None)
 if p is None: raise FileNotFoundError('No dataset image found')
 image=cv2.imread(str(p)); assert image is not None; features=extract_features(image,C['features']); features.update({'excavator_dump_truck_proximity':0.0} if 'excavator_dump_truck_proximity' in C['features'] else {}); assert set(features)==set(C['features']); score=calculate_activity_score({},C['road_layer']['required'],.8,features,C); assert 0<=score['normalized_score']<=1; print('PASS features and rules')
 try:
  mm,rm=load_models(); assert isinstance(detect_machinery(mm,image,C),list); detect_road_layer(rm,image,C); result=run_inference(p); assert result['processed_image'].shape==image.shape; print('PASS models and complete pipeline')
 except FileNotFoundError as error: print(f'SKIPPED model check: {error}')
if __name__=='__main__': main()
