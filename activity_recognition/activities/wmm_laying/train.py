from pathlib import Path
from ultralytics import YOLO
ROOT=Path(__file__).resolve().parent
def train(model_path:str,data_yaml:str,name:str)->None:
 for value in (model_path,data_yaml):
  if not Path(value).is_file(): raise FileNotFoundError(f'Training input does not exist: {value}')
 if not name or Path(name).name!=name: raise ValueError('name must be a non-empty run name without path separators')
 YOLO(model_path).train(data=data_yaml,project=str(ROOT/'runs'),name=name,exist_ok=False)
