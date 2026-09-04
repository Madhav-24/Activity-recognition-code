"""
Testing entry point for Site Clearing.
"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


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
