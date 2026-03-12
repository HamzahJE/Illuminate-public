import cv2
import os
import time
import platform

# Pi-optimized: More warmup on Pi for better auto-adjustment, less on desktop
WARMUP_FRAMES = 30 if platform.system() == 'Linux' else 10

def capture_image():
    # Setup images folder
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    folder = os.path.join(project_root, 'images')
    image_path = os.path.join(folder, "image.jpg")

    # Make sure folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Clear previous images
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Cannot open camera")

    time.sleep(0.1)  # Allow camera to warm up more

    # Skip several frames to allow auto-adjustment
    # Pi optimized: Use WARMUP_FRAMES (default 30 on Linux/Pi, 10 elsewhere)
    for _ in range(WARMUP_FRAMES):
        ret, frame = cam.read()
        if not ret:
            cam.release()
            raise RuntimeError("Failed to grab frame during warm-up")

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
