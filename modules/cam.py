import cv2
import os
import platform
import time

IS_PI = platform.system() == 'Linux'
SENSOR_SETTLE_SECS = 0.5 if IS_PI else 0.1
BUFFER_FLUSH_FRAMES = 3


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

    # Lock exposure and white balance to prevent oversaturation
    if IS_PI:
        cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)   # 1 = manual mode
        cam.set(cv2.CAP_PROP_EXPOSURE, -4)        # negative = shorter exposure, less saturation
        cam.set(cv2.CAP_PROP_AUTO_WB, 0)          # disable auto white balance
        cam.set(cv2.CAP_PROP_WB_TEMPERATURE, 4500)  # neutral daylight

    # Let sensor settle (exposure, white balance) then flush stale buffer frames
    time.sleep(SENSOR_SETTLE_SECS)
    for _ in range(BUFFER_FLUSH_FRAMES):
        cam.grab()

    # Capture final frame
    ret, image = cam.read()
    if not ret:
        cam.release()
        raise RuntimeError("Failed to grab frame")

    image_path = os.path.join(folder, "image.jpg")
    cv2.imwrite(image_path, image)
    print("Image saved to", image_path)
    cam.release()

    return image_path

# Example usage
if __name__ == "__main__":
    capture_image()
