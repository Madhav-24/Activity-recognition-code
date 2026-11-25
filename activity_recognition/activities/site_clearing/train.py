# Purpose: Implements the activity_recognition/activities/site_clearing/train.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

"""
Training entry point for Site Clearing.

NOTE:
Your trained model weights are already stored
under the models/ directory.

This file is provided so the activity remains
completely independent.
"""

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


# Logical block: defines the def main and controls its related behavior.
def main():

    print("=" * 60)

    print(
        "TRAINING: "
        "Site Clearing"
    )

    print("=" * 60)


    print(
        "\nMachinery dataset:"
    )

    print(
        MACHINERY_DATASET
    )


    print(
        "\nRoad-layer dataset:"
    )

    print(
        ROAD_LAYER_DATASET
    )


    print(
        "\nMachinery models:"
    )

    print(
        MACHINERY_MODELS
    )


    print(
        "\nRoad-layer models:"
    )

    print(
        ROAD_LAYER_MODELS
    )


    print(
        "\nExisting weights should be used "
        "for inference unless retraining is required."
    )


if __name__ == "__main__":
    main()
