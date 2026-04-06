import os
import sys
from typing import Optional

import platform

import cv2
import pytesseract

# Set Tesseract path based on platform
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Linux (Raspberry Pi) and macOS use system PATH — no explicit path needed

# Ensure sibling modules can be imported when this file is executed directly.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from modules.tts import speak_text


OCR_IMAGES_FOLDER = "ocr_images"


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
    """Extract text from a JPG image using Tesseract OCR."""
    if image_path is None:
        image_path = _find_default_jpg()

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    print(f"Loading image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        raise RuntimeError(f"Could not open image file: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)


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
