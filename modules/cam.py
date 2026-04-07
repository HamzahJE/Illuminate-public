import cv2
import numpy as np
import os
import platform
import time

IS_PI = platform.system() == 'Linux'
WARMUP_FRAMES = 30 if IS_PI else 10


def _resolve_capture_folder(folder_name: str) -> str:
    """Resolve a capture folder inside the project root and ensure it exists."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    folder = os.path.join(project_root, folder_name)
    os.makedirs(folder, exist_ok=True)
    return folder

def capture_image(folder_name='images'):
    # Setup destination folder
    folder = _resolve_capture_folder(folder_name)
    image_path = os.path.join(folder, "image.jpg")

    # Clear previous images
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Cannot open camera")

    time.sleep(0.1)
    
    for _ in range(WARMUP_FRAMES):
        cam.read()

    # Capture final frame
    ret, image = cam.read()
    if not ret:
        cam.release()
        raise RuntimeError("Failed to grab frame")

    # Correct overexposure via gamma correction if image is too bright
    gray_check = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray_check)
    if mean_brightness > 170:
        # Apply gamma > 1 to darken overexposed image
        gamma = 1.0 + (mean_brightness - 170) / 85.0  # scales ~1.0–2.0
        inv_gamma = 1.0 / gamma
        lut = np.array([((i / 255.0) ** inv_gamma) * 255
                        for i in range(256)]).astype("uint8")
        image = cv2.LUT(image, lut)

    image_path = os.path.join(folder, "image.jpg")
    cv2.imwrite(image_path, image)
    print("Image saved to", image_path)
    cam.release()

    return image_path

# Example usage
if __name__ == "__main__":
    capture_image()
