from pathlib import Path
import shutil


IMAGE_OUTPUT_DIR = Path(
    "tests_output/images"
)


def prepare_image(image_field, filename):
    """
    Copy Django uploaded image to the common
    test output folder and return the path.
    """

    if not image_field:
        return None

    IMAGE_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    extension = Path(
        image_field.name
    ).suffix

    output_path = (
        IMAGE_OUTPUT_DIR /
        f"{filename}{extension}"
    )

    if not output_path.exists():
        with image_field.open("rb") as source:
            with output_path.open("wb") as destination:
                shutil.copyfileobj(
                    source,
                    destination,
                )

    return str(output_path)