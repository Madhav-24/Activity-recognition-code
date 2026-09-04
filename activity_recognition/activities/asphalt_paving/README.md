# Asphalt Paving

Independent Ultralytics YOLO application.

- Machinery: Asphalt Paver, Dump Truck, Roller
- Road layer: Asphalt
- Features: edge_density, texture_variance, surface_uniformity, green_ratio

The pipeline searches local `models/<type>` before `model/<type>` and never downloads weights. Missing weights raise a clear `FileNotFoundError`. Required-machine confidence is averaged with matching road-layer confidence and normalized features; missing machines score zero. Asphalt surface uniformity is `1 - normalized grayscale standard deviation`.

Run: `streamlit run activities/asphalt_paving/dashboard/app.py`
Test: `py -3.10 activities/asphalt_paving/test.py`
Retrain: call `train(model_path, data_yaml, name)`; Ultralytics writes `runs/` with `exist_ok=False` and does not overwrite `best.pt`.
