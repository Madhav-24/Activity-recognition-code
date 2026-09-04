from pathlib import Path
import textwrap


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

ACTIVITIES_DIR = PROJECT_ROOT / "activities"


# ============================================================
# ACTIVITY CONFIGURATION
# ============================================================

ACTIVITIES = {

    "site_clearing": {
        "display_name": "Site Clearing",

        "machinery": [
            "Bulldozer",
            "Excavator",
            "Loader"
        ],

        "road_layer": "soil",

        "features": [
            "edge_density",
            "texture_variance",
            "green_ratio"
        ],

        "special_feature": "green_ratio"
    },


    "excavation": {
        "display_name": "Excavation / Earthwork",

        "machinery": [
            "Excavator",
            "Dump Truck"
        ],

        "road_layer": "soil",

        "features": [
            "edge_density",
            "texture_variance",
            "machinery_proximity"
        ],

        "special_feature": "machinery_proximity"
    },


    "land_grading": {
        "display_name": "Land Grading",

        "machinery": [
            "Grader",
            "Bulldozer",
            "Roller"
        ],

        "road_layer": "soil",

        "features": [
            "edge_density",
            "texture_variance"
        ],

        "special_feature": None
    },


    "subgrade_preparation": {
        "display_name": "Subgrade Preparation",

        "machinery": [
            "Grader",
            "Roller",
            "Bulldozer"
        ],

        "road_layer": "soil",

        "features": [
            "edge_density",
            "texture_variance"
        ],

        "special_feature": None
    },


    "gsb_laying": {
        "display_name": "GSB Laying",

        "machinery": [
            "Dump Truck",
            "Loader",
            "Roller"
        ],

        "road_layer": "GSB",

        "features": [
            "edge_density",
            "texture_variance"
        ],

        "special_feature": None
    },


    "wmm_laying": {
        "display_name": "WMM Laying",

        "machinery": [
            "Dump Truck",
            "Loader",
            "Roller"
        ],

        "road_layer": "WMM",

        "features": [
            "edge_density",
            "texture_variance"
        ],

        "special_feature": None
    },


    "asphalt_paving": {
        "display_name": "Asphalt Paving",

        "machinery": [
            "Asphalt Paver",
            "Dump Truck",
            "Roller"
        ],

        "road_layer": "asphalt",

        "features": [
            "edge_density",
            "texture_variance"
        ],

        "special_feature": None
    },


    "prime_coat": {
        "display_name": "Prime Coat",

        "machinery": [
            "Bitumen Sprayer"
        ],

        "road_layer": "WMM",

        "features": [
            "edge_density",
            "texture_variance"
        ],

        "special_feature": None
    },


    "tack_coat": {
        "display_name": "Tack Coat",

        "machinery": [
            "Bitumen Sprayer"
        ],

        "road_layer": "asphalt",

        "features": [
            "edge_density",
            "texture_variance"
        ],

        "special_feature": None
    },


    "piling": {
        "display_name": "Piling",

        "machinery": [
            "Piling Rig"
        ],

        "road_layer": "soil",

        "features": [
            "edge_density",
            "texture_variance"
        ],

        "special_feature": None
    }
}


# ============================================================
# UTILITY
# ============================================================

def write_file(path: Path, content: str):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        textwrap.dedent(content).strip() + "\n",
        encoding="utf-8"
    )


# ============================================================
# FEATURE EXTRACTOR
# ============================================================

def generate_feature_extractor(activity):

    features = activity["features"]

    imports = """
        import cv2
        import numpy as np
    """

    functions = ""


    # --------------------------------------------------------
    # EDGE DENSITY
    # --------------------------------------------------------

    if "edge_density" in features:

        functions += """

        def calculate_edge_density(image):
            \"\"\"
            Calculate edge density using Canny edge detection.

            Returns:
                float: ratio of edge pixels to total pixels.
            \"\"\"

            if image is None:
                return 0.0

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            edges = cv2.Canny(
                gray,
                100,
                200
            )

            edge_pixels = np.count_nonzero(edges)

            total_pixels = edges.size

            if total_pixels == 0:
                return 0.0

            return float(
                edge_pixels / total_pixels
            )
        """


    # --------------------------------------------------------
    # TEXTURE VARIANCE
    # --------------------------------------------------------

    if "texture_variance" in features:

        functions += """

        def calculate_texture_variance(image):
            \"\"\"
            Calculate image texture variance.

            Uses grayscale intensity variance.

            Returns:
                float: grayscale variance.
            \"\"\"

            if image is None:
                return 0.0

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            return float(
                np.var(gray)
            )
        """


    # --------------------------------------------------------
    # GREEN RATIO
    # --------------------------------------------------------

    if "green_ratio" in features:

        functions += """

        def calculate_green_ratio(image):
            \"\"\"
            Calculate the percentage of green pixels.

            HSV color segmentation is used to estimate
            vegetation/green surface coverage.

            Returns:
                float: ratio between 0 and 1.
            \"\"\"

            if image is None:
                return 0.0

            hsv = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2HSV
            )

            lower_green = np.array(
                [35, 40, 40]
            )

            upper_green = np.array(
                [90, 255, 255]
            )

            green_mask = cv2.inRange(
                hsv,
                lower_green,
                upper_green
            )

            green_pixels = np.count_nonzero(
                green_mask
            )

            total_pixels = green_mask.size

            if total_pixels == 0:
                return 0.0

            return float(
                green_pixels / total_pixels
            )
        """


    # --------------------------------------------------------
    # MACHINERY PROXIMITY
    # --------------------------------------------------------

    if "machinery_proximity" in features:

        functions += """

        def calculate_center(
            bbox
        ):
            \"\"\"
            Calculate center point of YOLO-style
            bounding box.

            bbox:
                [x1, y1, x2, y2]
            \"\"\"

            x1, y1, x2, y2 = bbox

            center_x = (
                x1 + x2
            ) / 2.0

            center_y = (
                y1 + y2
            ) / 2.0

            return (
                center_x,
                center_y
            )


        def calculate_distance(
            bbox1,
            bbox2
        ):
            \"\"\"
            Calculate Euclidean distance between
            two bounding-box centers.
            \"\"\"

            c1 = calculate_center(
                bbox1
            )

            c2 = calculate_center(
                bbox2
            )

            return float(
                np.sqrt(
                    (c1[0] - c2[0]) ** 2
                    +
                    (c1[1] - c2[1]) ** 2
                )
            )


        def calculate_machinery_proximity(
            excavator_boxes,
            dump_truck_boxes,
            image_width,
            image_height
        ):
            \"\"\"
            Calculate normalized proximity between
            Excavator and Dump Truck.

            Smaller distance means greater proximity.

            Returns:
                {
                    "distance": minimum normalized distance,
                    "proximity_score": value between 0 and 1
                }
            \"\"\"

            if (
                not excavator_boxes
                or
                not dump_truck_boxes
            ):
                return {
                    "distance": None,
                    "proximity_score": 0.0
                }

            if image_width <= 0 or image_height <= 0:
                return {
                    "distance": None,
                    "proximity_score": 0.0
                }

            min_distance = float("inf")

            for excavator in excavator_boxes:

                for truck in dump_truck_boxes:

                    distance = calculate_distance(
                        excavator,
                        truck
                    )

                    min_distance = min(
                        min_distance,
                        distance
                    )

            diagonal = np.sqrt(
                image_width ** 2
                +
                image_height ** 2
            )

            normalized_distance = (
                min_distance / diagonal
            )

            proximity_score = max(
                0.0,
                1.0 - normalized_distance
            )

            return {
                "distance": float(
                    normalized_distance
                ),
                "proximity_score": float(
                    proximity_score
                )
            }
        """


    # --------------------------------------------------------
    # FEATURE EXTRACTION FUNCTION
    # --------------------------------------------------------

    functions += """

        def extract_features(image):
            \"\"\"
            Extract activity-specific visual features.

            Returns:
                dictionary containing calculated features.
            \"\"\"

            features = {}
    """


    if "edge_density" in features:

        functions += """

            features["edge_density"] = (
                calculate_edge_density(image)
            )
        """


    if "texture_variance" in features:

        functions += """

            features["texture_variance"] = (
                calculate_texture_variance(image)
            )
        """


    if "green_ratio" in features:

        functions += """

            features["green_ratio"] = (
                calculate_green_ratio(image)
            )
        """


    functions += """

            return features
    """


    return imports + functions


# ============================================================
# RULE ENGINE
# ============================================================

def generate_rule_engine(activity):

    machinery = activity["machinery"]
    road_layer = activity["road_layer"]
    features = activity["features"]


    machinery_code = repr(machinery)
    features_code = repr(features)


    return f"""
    \"\"\"
    Rule engine for {activity["display_name"]}.

    Required machinery:
    {machinery}

    Required road layer:
    {road_layer}
    \"\"\"

    REQUIRED_MACHINERY = {machinery_code}

    REQUIRED_ROAD_LAYER = "{road_layer}"

    FEATURES_USED = {features_code}


    def machinery_score(
        detections,
        required_machinery=None
    ):
        \"\"\"
        Calculate machinery contribution.

        detections should be a dictionary such as:

        {{
            "Excavator": 0.92,
            "Dump Truck": 0.87,
            "Roller": 0.75
        }}

        Values represent confidence scores.
        \"\"\"

        if required_machinery is None:
            required_machinery = REQUIRED_MACHINERY

        score = 0.0

        for machine in required_machinery:

            confidence = float(
                detections.get(
                    machine,
                    0.0
                )
            )

            score += confidence

        return score


    def road_layer_score(
        detected_layer,
        confidence=1.0
    ):
        \"\"\"
        Calculate road-layer contribution.
        \"\"\"

        if detected_layer is None:
            return 0.0

        if (
            str(detected_layer).lower()
            ==
            REQUIRED_ROAD_LAYER.lower()
        ):
            return float(confidence)

        return 0.0


    def feature_score(
        features
    ):
        \"\"\"
        Calculate feature contribution.

        This is intentionally kept simple initially.
        Activity-specific thresholds can be tuned after
        testing on your actual site data.
        \"\"\"

        score = 0.0

        if not features:
            return score


        # --------------------------------------------
        # Edge density
        # --------------------------------------------

        if "edge_density" in features:

            edge_density = float(
                features.get(
                    "edge_density",
                    0.0
                )
            )

            # Low edge density receives a positive
            # contribution.
            edge_component = max(
                0.0,
                1.0 - min(
                    edge_density / 0.30,
                    1.0
                )
            )

            score += edge_component


        # --------------------------------------------
        # Texture variance
        # --------------------------------------------

        if "texture_variance" in features:

            texture = float(
                features.get(
                    "texture_variance",
                    0.0
                )
            )

            # Normalize approximately.
            texture_component = min(
                texture / 5000.0,
                1.0
            )

            score += texture_component


        # --------------------------------------------
        # Green ratio
        # --------------------------------------------

        if "green_ratio" in features:

            green_ratio = float(
                features.get(
                    "green_ratio",
                    0.0
                )
            )

            # Green vegetation can support
            # site-clearing detection.
            score += green_ratio


        return score


    def calculate_activity_score(
        detections,
        detected_layer,
        layer_confidence,
        features
    ):
        \"\"\"
        Calculate total activity score.

        Score components:

            Machinery
            +
            Road layer
            +
            Visual features
        \"\"\"

        m_score = machinery_score(
            detections
        )

        l_score = road_layer_score(
            detected_layer,
            layer_confidence
        )

        f_score = feature_score(
            features
        )


        total_score = (
            m_score
            +
            l_score
            +
            f_score
        )


        return {{
            "activity": "{activity["display_name"]}",
            "machinery_score": float(m_score),
            "road_layer_score": float(l_score),
            "feature_score": float(f_score),
            "total_score": float(total_score)
        }}
    """


# ============================================================
# CONFIG.YAML
# ============================================================

def generate_config(activity):

    machinery_yaml = "\n".join(
        [
            f"  - {machine}"
            for machine in activity["machinery"]
        ]
    )


    features_yaml = "\n".join(
        [
            f"  - {feature}"
            for feature in activity["features"]
        ]
    )


    return f"""
    activity:
      name: "{activity["display_name"]}"
      id: "{activity}"

    machinery:
    {machinery_yaml}

    road_layer:
      required: "{activity["road_layer"]}"

    features:
    {features_yaml}

    inference:
      confidence_threshold: 0.40
      image_size: 640

    scoring:
      machinery_weight: 3.0
      road_layer_weight: 3.0
      feature_weight: 1.0

    temporal:
      enabled: true
      window_size: 10

    output:
      save_results: true
      save_json: true
    """


# ============================================================
# INFERENCE.PY
# ============================================================

def generate_inference(activity):

    return f"""
    \"\"\"
    Inference pipeline for {activity["display_name"]}.

    Pipeline:

        Image
          ↓
        Machinery model
          ↓
        Road-layer model
          ↓
        Activity-specific features
          ↓
        Rule engine
          ↓
        Activity score
    \"\"\"

    from pathlib import Path
    import cv2
    import yaml

    from features.feature_extractor import (
        extract_features
    )

    from rules.activity_rules import (
        calculate_activity_score
    )


    BASE_DIR = Path(__file__).resolve().parent

    CONFIG_PATH = (
        BASE_DIR
        / "config"
        / "config.yaml"
    )


    def load_config():

        with open(
            CONFIG_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            return yaml.safe_load(f)


    def process_image(
        image_path,
        machinery_detections,
        road_layer,
        road_layer_confidence
    ):
        \"\"\"
        Process one image after model inference.

        machinery_detections:
            dictionary containing machinery
            confidence values.

        Example:

        {{
            "Excavator": 0.91,
            "Dump Truck": 0.84
        }}
        \"\"\"

        image = cv2.imread(
            str(image_path)
        )


        if image is None:

            raise FileNotFoundError(
                f"Could not read image: {{image_path}}"
            )


        features = extract_features(
            image
        )


        result = calculate_activity_score(
            detections=machinery_detections,
            detected_layer=road_layer,
            layer_confidence=road_layer_confidence,
            features=features
        )


        result["features"] = features

        result["road_layer"] = road_layer

        result["road_layer_confidence"] = (
            road_layer_confidence
        )

        result["image"] = str(
            image_path
        )


        return result


    if __name__ == "__main__":

        print(
            "{activity["display_name"]} inference module"
        )

        print(
            "Model loading and camera integration "
            "can be connected here."
        )
    """


# ============================================================
# TRAIN.PY
# ============================================================

def generate_train(activity):

    return f"""
    \"\"\"
    Training entry point for {activity["display_name"]}.

    NOTE:
    Your trained model weights are already stored
    under the models/ directory.

    This file is provided so the activity remains
    completely independent.
    \"\"\"

    from pathlib import Path


    BASE_DIR = Path(__file__).resolve().parent

    MACHINERY_DATASET = (
        BASE_DIR
        / "dataset"
        / "machinery"
    )

    ROAD_LAYER_DATASET = (
        BASE_DIR
        / "dataset"
        / "road_layer"
    )

    MACHINERY_MODELS = (
        BASE_DIR
        / "models"
        / "machinery"
    )

    ROAD_LAYER_MODELS = (
        BASE_DIR
        / "models"
        / "road_layer"
    )


    def main():

        print("=" * 60)

        print(
            "TRAINING: "
            "{activity["display_name"]}"
        )

        print("=" * 60)


        print(
            "\\nMachinery dataset:"
        )

        print(
            MACHINERY_DATASET
        )


        print(
            "\\nRoad-layer dataset:"
        )

        print(
            ROAD_LAYER_DATASET
        )


        print(
            "\\nMachinery models:"
        )

        print(
            MACHINERY_MODELS
        )


        print(
            "\\nRoad-layer models:"
        )

        print(
            ROAD_LAYER_MODELS
        )


        print(
            "\\nExisting weights should be used "
            "for inference unless retraining is required."
        )


    if __name__ == "__main__":
        main()
    """


# ============================================================
# TEST.PY
# ============================================================

def generate_test(activity):

    return f"""
    \"\"\"
    Testing entry point for {activity["display_name"]}.
    \"\"\"

    from pathlib import Path


    BASE_DIR = Path(__file__).resolve().parent


    def main():

        print("=" * 60)

        print(
            "TESTING: "
            "{activity["display_name"]}"
        )

        print("=" * 60)


        print(
            "\\nRequired machinery:"
        )

        for machine in {activity["machinery"]!r}:

            print(
                f"  - {{machine}}"
            )


        print(
            "\\nRequired road layer:"
        )

        print(
            "  - "
            "{activity["road_layer"]}"
        )


        print(
            "\\nActivity-specific features:"
        )

        for feature in {activity["features"]!r}:

            print(
                f"  - {{feature}}"
            )


        print(
            "\\nTesting module is ready."
        )


    if __name__ == "__main__":
        main()
    """


# ============================================================
# README
# ============================================================

def generate_readme(activity):

    machinery = "\n".join(
        [
            f"- {machine}"
            for machine in activity["machinery"]
        ]
    )

    features = "\n".join(
        [
            f"- {feature}"
            for feature in activity["features"]
        ]
    )


    return f"""
    # {activity["display_name"]}

    Independent activity-recognition module
    for the AI Road Construction system.


    ## Required Machinery

    {machinery}


    ## Required Road Layer

    {activity["road_layer"]}


    ## Features

    {features}


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
    {activity["display_name"].lower().replace(" ", "_")}/

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
    """


# ============================================================
# CREATE COMMON FILES
# ============================================================

def create_common_files():

    common_dir = (
        PROJECT_ROOT
        / "src"
        / "common"
    )

    common_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    image_utils = """
    import cv2


    def load_image(path):

        image = cv2.imread(
            str(path)
        )

        if image is None:
            raise FileNotFoundError(
                f"Unable to read image: {path}"
            )

        return image
    """


    temporal = """
    from collections import deque


    class TemporalBuffer:

        def __init__(
            self,
            max_length=10
        ):

            self.buffer = deque(
                maxlen=max_length
            )


        def add(self, value):

            self.buffer.append(
                value
            )


        def get(self):

            return list(
                self.buffer
            )


        def clear(self):

            self.buffer.clear()


        def average(self):

            values = self.get()

            if not values:
                return 0.0

            return sum(values) / len(values)
    """


    write_file(
        common_dir
        / "image_utils.py",
        image_utils
    )

    write_file(
        common_dir
        / "temporal.py",
        temporal
    )


# ============================================================
# CREATE ACTIVITY FILES
# ============================================================

def create_activity(activity_name, activity):

    activity_dir = (
        ACTIVITIES_DIR
        / activity_name
    )


    print(
        f"\nCreating: {activity['display_name']}"
    )


    # --------------------------------------------------------
    # DIRECTORIES
    # --------------------------------------------------------

    directories = [

        activity_dir / "dataset" / "machinery",

        activity_dir / "dataset" / "road_layer",

        activity_dir / "models" / "machinery",

        activity_dir / "models" / "road_layer",

        activity_dir / "rules",

        activity_dir / "features",

        activity_dir / "config"
    ]


    for directory in directories:

        directory.mkdir(
            parents=True,
            exist_ok=True
        )


    # --------------------------------------------------------
    # RULES
    # --------------------------------------------------------

    write_file(
        activity_dir
        / "rules"
        / "activity_rules.py",

        generate_rule_engine(
            activity
        )
    )


    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    write_file(
        activity_dir
        / "features"
        / "feature_extractor.py",

        generate_feature_extractor(
            activity
        )
    )


    # --------------------------------------------------------
    # CONFIG
    # --------------------------------------------------------

    write_file(
        activity_dir
        / "config"
        / "config.yaml",

        generate_config(
            activity
        )
    )


    # --------------------------------------------------------
    # INFERENCE
    # --------------------------------------------------------

    write_file(
        activity_dir
        / "inference.py",

        generate_inference(
            activity
        )
    )


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    write_file(
        activity_dir
        / "train.py",

        generate_train(
            activity
        )
    )


    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    write_file(
        activity_dir
        / "test.py",

        generate_test(
            activity
        )
    )


    # --------------------------------------------------------
    # README
    # --------------------------------------------------------

    write_file(
        activity_dir
        / "README.md",

        generate_readme(
            activity
        )
    )


    print(
        "  ✓ rules/activity_rules.py"
    )

    print(
        "  ✓ features/feature_extractor.py"
    )

    print(
        "  ✓ config/config.yaml"
    )

    print(
        "  ✓ inference.py"
    )

    print(
        "  ✓ train.py"
    )

    print(
        "  ✓ test.py"
    )

    print(
        "  ✓ README.md"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")

    print("=" * 70)

    print(
        "AI ROAD CONSTRUCTION"
    )

    print(
        "ACTIVITY FILE GENERATOR"
    )

    print("=" * 70)


    print(
        f"\nProject root:"
    )

    print(
        PROJECT_ROOT
    )


    print(
        f"\nActivities directory:"
    )

    print(
        ACTIVITIES_DIR
    )


    # --------------------------------------------------------
    # CREATE ACTIVITIES DIRECTORY
    # --------------------------------------------------------

    ACTIVITIES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # CREATE COMMON UTILITIES
    # --------------------------------------------------------

    print(
        "\nCreating common utilities..."
    )

    create_common_files()


    print(
        "  ✓ src/common/image_utils.py"
    )

    print(
        "  ✓ src/common/temporal.py"
    )


    # --------------------------------------------------------
    # CREATE EACH ACTIVITY
    # --------------------------------------------------------

    for activity_name, activity in ACTIVITIES.items():

        create_activity(
            activity_name,
            activity
        )


    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\n")

    print("=" * 70)

    print(
        "GENERATION COMPLETED SUCCESSFULLY"
    )

    print("=" * 70)


    print(
        "\nActivities generated:"
    )


    for activity_name, activity in ACTIVITIES.items():

        print(
            f"  ✓ {activity_name}"
        )


    print(
        "\nTotal activities:"
    )

    print(
        len(ACTIVITIES)
    )


    print(
        "\nImportant:"
    )

    print(
        "Existing dataset and model files were NOT modified."
    )

    print(
        "Only the required Python/config/README files "
        "were generated."
    )


    print(
        "\nDone."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()