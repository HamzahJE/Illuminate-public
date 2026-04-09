import os
import sys
from typing import Optional

import cv2
import numpy as np
import wordninja
from rapidocr_onnxruntime import RapidOCR

# Ensure sibling modules can be imported when this file is executed directly.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from modules.test_mode import is_test_mode

OCR_IMAGES_FOLDER = "ocr_images"
OCR_DEBUG_FOLDER = "ocr_debug"

# Initialize once — no large framework to load, just ONNX models
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = RapidOCR()
    return _reader


def _find_default_jpg() -> str:
    """Return the first JPG path found in the OCR images folder."""
    images_dir = os.path.join(ROOT_DIR, OCR_IMAGES_FOLDER)
    image_path = os.path.join(images_dir, "image.jpg")
    if not os.path.exists(image_path):
        for file_name in os.listdir(images_dir):
            if file_name.lower().endswith(".jpg"):
                image_path = os.path.join(images_dir, file_name)
                break
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No JPG image found in {images_dir}")
    return image_path


def get_text_from_image(image_path: Optional[str] = None) -> str:
    """Extract text from an image using OCR."""
    if image_path is None:
        image_path = _find_default_jpg()

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    print(f"Loading image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        raise RuntimeError(f"Could not open image file: {image_path}")

    # Upscale small images so distant sign text is large enough for detection
    h, w = image.shape[:2]
    if h < 1500:
        scale = 3 if h < 800 else 2
        image = cv2.resize(image, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

    reader = _get_reader()
    result, _ = reader(image)

    if not result:
        return ""

    # result is list of [bbox, text, confidence]
    # Split joined words (e.g. "DONOT" -> "DO NOT") and filter by confidence
    words = []
    for (_, text, conf) in result:
        if float(conf) > 0.2 and text.strip():
            if ' ' not in text and len(text) > 4:
                words.append(" ".join(wordninja.split(text)))
            else:
                words.append(text)

    if is_test_mode():
        debug_dir = os.path.join(ROOT_DIR, OCR_DEBUG_FOLDER)
        os.makedirs(debug_dir, exist_ok=True)
        debug_img = image.copy()
        for (bbox, text, conf) in result:
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(debug_img, [pts], True, (0, 255, 0), 2)
            cv2.putText(debug_img, f"{text} ({float(conf):.0%})", tuple(pts[0]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imwrite(os.path.join(debug_dir, "rapidocr_debug.jpg"), debug_img)
        print(f"Debug image saved to {debug_dir}")

    return " ".join(words)


if __name__ == "__main__":
    detected_text = get_text_from_image()
    print("Detected Text:")
    print(detected_text)
