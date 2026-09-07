# Purpose: Implements the activity_recognition/src/common/image_utils.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

import cv2


# Logical block: defines the def load_image and controls its related behavior.
def load_image(path):

    image = cv2.imread(
        str(path)
    )

    if image is None:
        raise FileNotFoundError(
            f"Unable to read image: {path}"
        )

    return image
