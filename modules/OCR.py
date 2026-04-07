import os
import sys
from typing import Optional

import platform

import cv2
import numpy as np
import pytesseract

# Set Tesseract path based on platform
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Linux (Raspberry Pi) and macOS use system PATH — no explicit path needed

# Ensure sibling modules can be imported when this file is executed directly.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from modules.test_mode import is_test_mode
from modules.tts import speak_text


OCR_IMAGES_FOLDER = "ocr_images"
OCR_DEBUG_FOLDER = "ocr_debug"


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

    # Enhance contrast to handle uneven / low lighting
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # 4x upscale for 640x480 — distant sign text needs ~40px+ per char
    h, w = gray.shape
    if h < 1500:
        scale = 4 if h < 800 else 2
        gray = cv2.resize(gray, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

    # Sharpen to restore edges blurred by upscaling
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, sharpen_kernel)

    # Light denoise without killing fine text
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive threshold handles shadows and varied brightness
    gray = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )

    # Save processed images in test mode for debugging
    if is_test_mode():
        debug_dir = os.path.join(ROOT_DIR, OCR_DEBUG_FOLDER)
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, "processed.jpg"), gray)
        cv2.imwrite(os.path.join(debug_dir, "inverted.jpg"), cv2.bitwise_not(gray))
        print(f"Debug images saved to {debug_dir}")

    # Try both normal and inverted (light text on dark signs)
    custom_config = r"--oem 3 --psm 3"
    results = []
    for img in [gray, cv2.bitwise_not(gray)]:
        data = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
        words = [
            data["text"][i]
            for i in range(len(data["text"]))
            if int(data["conf"][i]) > 40 and data["text"][i].strip()
        ]
        results.append(" ".join(words))

    # Return whichever pass found more text
    return results[0] if len(results[0]) >= len(results[1]) else results[1]


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
