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
