import base64
import logging

from .utils import event_storage

logger = logging.getLogger(__name__)

FRAME_EXTENSION = "jpeg"


def upload_image(base64_img, storage="", credentials=""):
    logger.info("Uploading image")

    base64_bytes = base64_img.encode("ascii")
    image_bytes = base64.b64decode(base64_bytes)

    file_path = event_storage.upload_file(image_bytes, ext=FRAME_EXTENSION)

    return file_path
