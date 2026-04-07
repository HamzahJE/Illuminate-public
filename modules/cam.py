import cv2
import os
import platform
import subprocess
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
            

    # On Pi, reduce exposure via v4l2 before opening camera
    if IS_PI:
        try:
            # Print available controls so we can see what this camera supports
            result = subprocess.run(
                ["v4l2-ctl", "-d", "/dev/video0", "--list-ctrls"],
                capture_output=True, text=True, timeout=5
            )
            print("Camera controls:\n", result.stdout)

            # Disable auto-exposure (1=manual, 3=auto on most v4l2 cameras)
            subprocess.run(
                ["v4l2-ctl", "-d", "/dev/video0",
                 "-c", "exposure_auto=1"],
                capture_output=True, timeout=5
            )
            # Set a low exposure value
            subprocess.run(
                ["v4l2-ctl", "-d", "/dev/video0",
                 "-c", "exposure_absolute=150"],
                capture_output=True, timeout=5
            )
        except FileNotFoundError:
            print("v4l2-ctl not found, skipping exposure control")
        except subprocess.TimeoutExpired:
            pass

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

    image_path = os.path.join(folder, "image.jpg")
    cv2.imwrite(image_path, image)
    print("Image saved to", image_path)
    cam.release()

    return image_path

# Example usage
if __name__ == "__main__":
    capture_image()
