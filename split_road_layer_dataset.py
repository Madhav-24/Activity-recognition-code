import shutil
import yaml
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

# ORIGINAL ROAD-LAYER DATASET
SOURCE_DATASET = Path(
    r"C:\Users\Student\Desktop\SPLIT_DATASET\road_layer\roadLayer"
)

# ORIGINAL TRAINED ROAD-LAYER MODEL
BEST_PT = Path(
    r"C:\Users\Student\Desktop\SPLIT_DATASET\road_layer\best.pt"
)

# NEW OUTPUT FOLDER
OUTPUT_DIR = Path(
    r"C:\Users\Student\Desktop\SPLIT_DATASET\road_layer\road_layer_separated"
)


# ============================================================
# CHECK INPUT PATHS
# ============================================================

print("=" * 70)
print("CHECKING INPUT PATHS")
print("=" * 70)

print("\nSource Dataset:")
print(SOURCE_DATASET)

print("\nBest.pt:")
print(BEST_PT)

print("\nOutput Folder:")
print(OUTPUT_DIR)


if not SOURCE_DATASET.exists():
    raise FileNotFoundError(
        f"\nERROR: Road-layer dataset not found:\n{SOURCE_DATASET}"
    )


if not BEST_PT.exists():
    raise FileNotFoundError(
        f"\nERROR: best.pt not found:\n{BEST_PT}"
    )


# ============================================================
# READ ORIGINAL DATA.YAML
# ============================================================

yaml_path = SOURCE_DATASET / "data.yaml"

if not yaml_path.exists():
    raise FileNotFoundError(
        f"\nERROR: data.yaml not found:\n{yaml_path}"
    )


print("\n" + "=" * 70)
print("READING ORIGINAL DATA.YAML")
print("=" * 70)


with open(
    yaml_path,
    "r",
    encoding="utf-8"
) as f:

    data = yaml.safe_load(f)


names = data["names"]


# ============================================================
# CONVERT CLASS NAMES INTO DICTIONARY
# ============================================================

if isinstance(names, dict):

    class_names = {
        int(k): str(v)
        for k, v in names.items()
    }

else:

    class_names = {
        i: str(name)
        for i, name in enumerate(names)
    }


print("\nOriginal road-layer classes detected:")

for class_id, class_name in class_names.items():

    print(
        f"  Class {class_id}: {class_name}"
    )


print(
    f"\nTotal road-layer classes: "
    f"{len(class_names)}"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def safe_folder_name(name):

    return (
        name
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )


# ============================================================
# DATASET SPLITS
# ============================================================

splits = [
    "train",
    "valid",
    "test"
]


# ============================================================
# PROCESS EACH ROAD-LAYER CLASS
# ============================================================

for class_id, class_name in class_names.items():

    folder_name = safe_folder_name(
        class_name
    )

    road_layer_dir = (
        OUTPUT_DIR / folder_name
    )


    print("\n")
    print("=" * 70)
    print(f"PROCESSING: {class_name}")
    print(f"ORIGINAL CLASS ID: {class_id}")
    print("=" * 70)


    # ========================================================
    # CREATE WEIGHTS DIRECTORY
    # ========================================================

    weights_dir = (
        road_layer_dir / "weights"
    )

    weights_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    # ========================================================
    # CREATE TRAIN / VALID / TEST DIRECTORIES
    # ========================================================

    for split in splits:

        images_dir = (
            road_layer_dir
            / split
            / "images"
        )

        labels_dir = (
            road_layer_dir
            / split
            / "labels"
        )


        images_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        labels_dir.mkdir(
            parents=True,
            exist_ok=True
        )


    # ========================================================
    # COPY BEST.PT
    # ========================================================

    destination_pt = (
        weights_dir / "best.pt"
    )

    shutil.copy2(
        BEST_PT,
        destination_pt
    )

    print(
        "\nCopied best.pt to:"
    )

    print(
        destination_pt
    )


    # ========================================================
    # PROCESS TRAIN / VALID / TEST
    # ========================================================

    for split in splits:

        print(
            f"\nProcessing {split}..."
        )


        # ----------------------------------------------------
        # SOURCE DIRECTORIES
        # ----------------------------------------------------

        source_images = (
            SOURCE_DATASET
            / split
            / "images"
        )

        source_labels = (
            SOURCE_DATASET
            / split
            / "labels"
        )


        # ----------------------------------------------------
        # CHECK SOURCE DIRECTORIES
        # ----------------------------------------------------

        if not source_images.exists():

            print(
                f"WARNING: Images folder does not exist:"
            )

            print(
                source_images
            )

            continue


        if not source_labels.exists():

            print(
                f"WARNING: Labels folder does not exist:"
            )

            print(
                source_labels
            )

            continue


        # ----------------------------------------------------
        # OUTPUT DIRECTORIES
        # ----------------------------------------------------

        output_images = (
            road_layer_dir
            / split
            / "images"
        )

        output_labels = (
            road_layer_dir
            / split
            / "labels"
        )


        image_count = 0


        # ----------------------------------------------------
        # READ EVERY LABEL FILE
        # ----------------------------------------------------

        for label_file in source_labels.glob(
            "*.txt"
        ):

            with open(
                label_file,
                "r",
                encoding="utf-8"
            ) as f:

                lines = f.readlines()


            selected_annotations = []


            # =================================================
            # SELECT ONLY CURRENT ROAD-LAYER CLASS
            # =================================================

            for line in lines:

                line = line.strip()


                if not line:
                    continue


                parts = line.split()


                # YOLO format:
                #
                # class_id
                # x_center
                # y_center
                # width
                # height

                if len(parts) < 5:

                    continue


                try:

                    original_class_id = int(
                        parts[0]
                    )

                except ValueError:

                    continue


                # ------------------------------------------------
                # KEEP ONLY CURRENT CLASS
                # ------------------------------------------------

                if original_class_id == class_id:

                    # Each separated dataset has only one class.
                    #
                    # Therefore:
                    #
                    # Original:
                    # 0 x y w h
                    #
                    # New:
                    # 0 x y w h
                    #
                    # Original class 1:
                    # 1 x y w h
                    #
                    # New:
                    # 0 x y w h

                    parts[0] = "0"


                    selected_annotations.append(
                        " ".join(parts)
                    )


            # =================================================
            # SKIP IMAGE IF CLASS IS NOT PRESENT
            # =================================================

            if not selected_annotations:

                continue


            # =================================================
            # FIND CORRESPONDING IMAGE
            # =================================================

            image_file = None


            image_extensions = [
                ".jpg",
                ".jpeg",
                ".png",
                ".JPG",
                ".JPEG",
                ".PNG",
                ".webp",
                ".WEBP"
            ]


            for extension in image_extensions:

                possible_image = (
                    source_images
                    / (
                        label_file.stem
                        + extension
                    )
                )


                if possible_image.exists():

                    image_file = (
                        possible_image
                    )

                    break


            # =================================================
            # IMAGE NOT FOUND
            # =================================================

            if image_file is None:

                print(
                    f"WARNING: Image not found for:"
                    f" {label_file.name}"
                )

                continue


            # =================================================
            # COPY IMAGE
            # =================================================

            destination_image = (
                output_images
                / image_file.name
            )


            shutil.copy2(
                image_file,
                destination_image
            )


            # =================================================
            # CREATE NEW LABEL
            # =================================================

            destination_label = (
                output_labels
                / label_file.name
            )


            with open(
                destination_label,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    "\n".join(
                        selected_annotations
                    )
                    + "\n"
                )


            image_count += 1


        # ----------------------------------------------------
        # SPLIT SUMMARY
        # ----------------------------------------------------

        print(
            f"{split}: "
            f"{image_count} images copied"
        )


    # ========================================================
    # CREATE INDIVIDUAL DATA.YAML
    # ========================================================

    individual_yaml = {

        "train": "train/images",

        "val": "valid/images",

        "test": "test/images",

        "nc": 1,

        "names": [
            class_name
        ]
    }


    yaml_output = (
        road_layer_dir / "data.yaml"
    )


    with open(
        yaml_output,
        "w",
        encoding="utf-8"
    ) as f:

        yaml.dump(
            individual_yaml,
            f,
            sort_keys=False
        )


    print(
        "\nCreated YAML:"
    )

    print(
        yaml_output
    )


# ============================================================
# CREATE ROAD_LAYER_CLASSES.YAML
# ============================================================

classes_yaml = {
    "classes": class_names
}


classes_output = (
    OUTPUT_DIR
    / "road_layer_classes.yaml"
)


with open(
    classes_output,
    "w",
    encoding="utf-8"
) as f:

    yaml.dump(
        classes_yaml,
        f,
        sort_keys=False
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n\n")

print("=" * 70)
print("SUCCESS! ROAD-LAYER DATASET SPLITTING COMPLETED")
print("=" * 70)


print(
    "\nOutput folder:"
)

print(
    OUTPUT_DIR
)


print("\nCreated structure:")

print(
    """
road_layer_separated/
│
├── GSB/
│   ├── weights/
│   │   └── best.pt
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── valid/
│   │   ├── images/
│   │   └── labels/
│   ├── test/
│   │   ├── images/
│   │   └── labels/
│   └── data.yaml
│
├── asphalt/
│   ├── weights/
│   │   └── best.pt
│   ├── train/
│   ├── valid/
│   ├── test/
│   └── data.yaml
│
├── concrete/
│   └── ...
│
├── soil/
│   └── ...
│
└── road_layer_classes.yaml
"""
)


print(
    "\nIMPORTANT:"
)

print(
    "The best.pt files are COPIES of your original "
    "4-class road-layer model."
)

print(
    "They are NOT separately retrained models."
)

print(
    "For inference, use the original class ID "
    "with classes=[class_id]."
)

print(
    "\nFinished."
)