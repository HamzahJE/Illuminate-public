import os
import sys
from typing import Optional

import cv2
import easyocr

# Ensure sibling modules can be imported when this file is executed directly.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from modules.test_mode import is_test_mode
from modules.tts import speak_text

OCR_IMAGES_FOLDER = "ocr_images"
OCR_DEBUG_FOLDER = "ocr_debug"

# Initialize reader once — model loading is slow, only pay the cost at startup
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
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
    """Extract text from an image using EasyOCR."""
    if image_path is None:
        image_path = _find_default_jpg()

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    print(f"Loading image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        raise RuntimeError(f"Could not open image file: {image_path}")

    reader = _get_reader()
    results = reader.readtext(image)

    # Filter by confidence > 0.4
    words = [text for (_, text, conf) in results if conf > 0.4 and text.strip()]

    if is_test_mode():
        debug_dir = os.path.join(ROOT_DIR, OCR_DEBUG_FOLDER)
        os.makedirs(debug_dir, exist_ok=True)
        # Draw detected text boxes on image for debugging
        debug_img = image.copy()
        for (bbox, text, conf) in results:
            pts = [tuple(int(c) for c in p) for p in bbox]
            cv2.polylines(debug_img, [__import__("numpy").array(pts)], True, (0, 255, 0), 2)
            cv2.putText(debug_img, f"{text} ({conf:.0%})", pts[0],
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imwrite(os.path.join(debug_dir, "easyocr_debug.jpg"), debug_img)
        print(f"Debug image saved to {debug_dir}")

    return " ".join(words)


def speak_text_from_image(image_path: Optional[str] = None) -> str:
    """Extract text from an image and speak it using the TTS module."""
    text = get_text_from_image(image_path)

    if not text.strip():
        print("No text found to speak.")
        return text

    speak_text(text)
    return text


if __name__ == "__main__":
    detected_text = speak_text_from_image()
    print("Detected Text:")
    print(detected_text)
