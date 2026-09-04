# Site Clearing

    Independent activity-recognition module
    for the AI Road Construction system.


    ## Required Machinery

    - Bulldozer
- Excavator
- Loader


    ## Required Road Layer

    soil


    ## Features

    - edge_density
- texture_variance
- green_ratio


    ## Pipeline

    Image
    ↓
    Machinery detection
    ↓
    Road-layer detection
    ↓
    Activity-specific feature extraction
    ↓
    Rule engine
    ↓
    Activity score


    ## Folder Structure

    ```text
    site_clearing/

    ├── dataset/
    ├── models/
    ├── rules/
    ├── features/
    ├── config/
    ├── inference.py
    ├── train.py
    ├── test.py
    └── README.md
    ```


    ## Important

    This activity is independent from the other
    activity-recognition modules.

    Activity-specific thresholds and weights can
    be tuned using actual construction-site data.
