# Tack Coat

Independent Ultralytics YOLO application.

- Machinery: Bitumen Sprayer
- Road layer: Asphalt
- Features: edge_density, texture_variance

The pipeline searches local `models/<type>` before `model/<type>` and never downloads weights. Missing weights raise a clear `FileNotFoundError`. Required-machine confidence is averaged with matching road-layer confidence and normalized features; missing machines score zero. Asphalt surface uniformity is `1 - normalized grayscale standard deviation`.

Run: `streamlit run activities/tack_coat/dashboard/app.py`
Test: `py -3.10 activities/tack_coat/test.py`
Retrain: call `train(model_path, data_yaml, name)`; Ultralytics writes `runs/` with `exist_ok=False` and does not overwrite `best.pt`.
