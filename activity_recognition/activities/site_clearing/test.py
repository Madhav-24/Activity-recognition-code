# Purpose: Implements the activity_recognition/activities/site_clearing/test.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

"""
Testing entry point for Site Clearing.
"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


# Logical block: defines the def main and controls its related behavior.
def main():

    print("=" * 60)

    print(
        "TESTING: "
        "Site Clearing"
    )

    print("=" * 60)


    print(
        "\nRequired machinery:"
    )

    for machine in ['Bulldozer', 'Excavator', 'Loader']:

        print(
            f"  - {machine}"
        )


    print(
        "\nRequired road layer:"
    )

    print(
        "  - "
        "soil"
    )


    print(
        "\nActivity-specific features:"
    )

    for feature in ['edge_density', 'texture_variance', 'green_ratio']:

        print(
            f"  - {feature}"
        )


    print(
        "\nTesting module is ready."
    )


if __name__ == "__main__":
    main()
