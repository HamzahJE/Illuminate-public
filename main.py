import threading
import time
import sys
import argparse
import os
from queue import Queue, Empty
from dotenv import load_dotenv
os.environ["ORT_LOGGING_LEVEL"] = "3" # supress warning to clean up console output

# Load environment variables once at startup
project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_root, '.env'))

# AI/Vision modules
import base64
from modules.cam import capture_image
from modules.openai_vision import get_image_description
from modules.tts import speak_text, warm_up
from modules.stt_mic import listen_from_mic
from modules.chat import query_openai, set_image_context, has_image_context, query_image_followup

# Input modules
from modules.hardware import GPIOKeypad, has_gpio_hardware
from modules.keyboard_input import KeyboardInput
from modules.ui import print_banner
from modules.test_mode import print_test_mode_banner, set_test_mode


# ============================================================================
# COMMAND HANDLERS - What each button does
# ============================================================================

def capture_and_describe():
    """Command 1: Take photo and describe what's in it. Resets image conversation."""
    try:
        t_start = time.time()
        print(f"\n[Action] Capturing image...  [{time.strftime('%H:%M:%S')}]")
        image_path = capture_image()
        t_captured = time.time()
        print(f"[Timestamp] Image captured    +{t_captured - t_start:.2f}s")

        print(f"[Action] Getting AI description...  [{time.strftime('%H:%M:%S')}]")
        description = get_image_description()
        t_described = time.time()
        print(f"[AI] {description}")
        print(f"[Timestamp] AI response received  +{t_described - t_captured:.2f}s  (total +{t_described - t_start:.2f}s)")

        # Inject image into conversation history for follow-up questions (button 3)
        image_base64 = base64.b64encode(open(image_path, 'rb').read()).decode('ascii')
        set_image_context(image_base64, description)
        print("[Info] Image context set — press [3] to ask follow-up questions")

        print(f"[Action] Speaking response...  [{time.strftime('%H:%M:%S')}]")
        speech_timing = speak_text(description) or {}
        t_speech_started = speech_timing.get("started_at") or time.time()
        t_done = speech_timing.get("finished_at") or time.time()
        ttfb = t_speech_started - t_described
        print(f"[Timestamp] Speech started   +{t_speech_started - t_described:.2f}s  (total +{t_speech_started - t_start:.2f}s)")
        print(f"[Timestamp] Speech finished  +{t_done - t_described:.2f}s  (total +{t_done - t_start:.2f}s)")
        print(f"[Latency] TTS TTFB          {ttfb:.2f}s")
    except Exception as e:
        print(f"[Error] Camera/AI failed: {e}")
        speak_text("Sorry, there was an error processing the image.")


def voice_interaction():
    """Command 2: Listen and respond to voice question."""
    try:
        t_start = time.time()
        print(f"\n[Action] Listening...  [{time.strftime('%H:%M:%S')}]")
        text = listen_from_mic()
        t_heard = time.time()
        if text:
            print(f"[You said] {text}")
            print(f"[Timestamp] Speech recognised  +{t_heard - t_start:.2f}s")

            print(f"[Action] Querying AI...  [{time.strftime('%H:%M:%S')}]")
            t_query = time.time()
            response = query_openai(text)
            t_responded = time.time()
            print(f"[Timestamp] AI response received  +{t_responded - t_query:.2f}s  (total +{t_responded - t_start:.2f}s)")

            print(f"[Action] Speaking response...  [{time.strftime('%H:%M:%S')}]")
            speech_timing = speak_text(response) or {}
            t_speech_started = speech_timing.get("started_at") or time.time()
            t_done = speech_timing.get("finished_at") or time.time()
            ttfb = t_speech_started - t_responded
            print(f"[Timestamp] Speech started   +{t_speech_started - t_responded:.2f}s  (total +{t_speech_started - t_start:.2f}s)")
            print(f"[Timestamp] Speech finished  +{t_done - t_responded:.2f}s  (total +{t_done - t_start:.2f}s)")
            print(f"[Latency] TTS TTFB          {ttfb:.2f}s")
        else:
            print("[Info] No speech detected")
            speak_text("I didn't catch that.")
    except Exception as e:
        print(f"[Error] Voice assistant failed: {e}")
        speak_text("Sorry, I couldn't process your request.")


def image_followup():
    """Command 3: Ask a follow-up question about the captured image."""
    if not has_image_context():
        print("\n[Info] No image captured yet — press [1] first")
        speak_text("Please capture an image first.")
        return

    try:
        t_start = time.time()
        print(f"\n[Action] Listening for image question...  [{time.strftime('%H:%M:%S')}]")
        text = listen_from_mic()
        t_heard = time.time()
        if text:
            print(f"[You said] {text}")
            print(f"[Timestamp] Speech recognised  +{t_heard - t_start:.2f}s")

            print(f"[Action] Querying AI about image...  [{time.strftime('%H:%M:%S')}]")
            t_query = time.time()
            response = query_image_followup(text)
            t_responded = time.time()
            print(f"[Timestamp] AI response received  +{t_responded - t_query:.2f}s  (total +{t_responded - t_start:.2f}s)")

            print(f"[Action] Speaking response...  [{time.strftime('%H:%M:%S')}]")
            speech_timing = speak_text(response) or {}
            t_speech_started = speech_timing.get("started_at") or time.time()
            t_done = speech_timing.get("finished_at") or time.time()
            ttfb = t_speech_started - t_responded
            print(f"[Timestamp] Speech started   +{t_speech_started - t_responded:.2f}s  (total +{t_speech_started - t_start:.2f}s)")
            print(f"[Timestamp] Speech finished  +{t_done - t_responded:.2f}s  (total +{t_done - t_start:.2f}s)")
            print(f"[Latency] TTS TTFB          {ttfb:.2f}s")
        else:
            print("[Info] No speech detected")
            speak_text("I didn't catch that.")
    except Exception as e:
        print(f"[Error] Image follow-up failed: {e}")
        speak_text("Sorry, I couldn't process your question about the image.")


def ocr_read():
    """Command 4: Capture a fresh image and extract text via OCR."""
    try:
        t_start = time.time()
        print(f"\n[Action] Capturing image for OCR...  [{time.strftime('%H:%M:%S')}]")
        image_path = capture_image(folder_name='ocr_images')
        t_captured = time.time()
        print(f"[Timestamp] Image captured    +{t_captured - t_start:.2f}s")

        print(f"[Action] Running OCR...  [{time.strftime('%H:%M:%S')}]")
        from modules.OCR import get_text_from_image
        text = get_text_from_image(image_path)
        t_ocr = time.time()
        print(f"[Timestamp] OCR completed     +{t_ocr - t_captured:.2f}s  (total +{t_ocr - t_start:.2f}s)")

        if text.strip():
            print(f"[OCR] {text.strip()}")
            speak_text(text.strip())
        else:
            print("[OCR] No text found in image")
            speak_text("No text was found in the image.")
    except Exception as e:
        print(f"[Error] OCR failed: {e}")
        speak_text("Sorry, I couldn't read text from the image.")


def rapidocr_read():
    """Command 5: Capture a fresh image and extract text via RapidOCR."""
    try:
        t_start = time.time()
        print(f"\n[Action] Capturing image for RapidOCR...  [{time.strftime('%H:%M:%S')}]")
        image_path = capture_image(folder_name='ocr_images')
        t_captured = time.time()
        print(f"[Timestamp] Image captured    +{t_captured - t_start:.2f}s")

        print(f"[Action] Running RapidOCR...  [{time.strftime('%H:%M:%S')}]")
        from modules import rapid_ocr
        text = rapid_ocr.get_text_from_image(image_path)
        t_ocr = time.time()
        print(f"[Timestamp] RapidOCR completed  +{t_ocr - t_captured:.2f}s  (total +{t_ocr - t_start:.2f}s)")

        if text.strip():
            print(f"[RapidOCR] {text.strip()}")
            speak_text(text.strip())
        else:
            print("[RapidOCR] No text found in image")
            speak_text("No text was found in the image.")
    except Exception as e:
        print(f"[Error] RapidOCR failed: {e}")
        speak_text("Sorry, I couldn't read text from the image.")


def process_command(command):
    """Process a command and return True if should quit."""
    if command == '1':
        capture_and_describe()
    elif command == '2':
        voice_interaction()
    elif command == '3':
        image_followup()
    elif command == '4':
        ocr_read()
    elif command == '5':
        rapidocr_read()
    elif command == 'q':
        return True  # Quit
    elif command:
        print(f"[Invalid] Unknown command: '{command}'")

    return False  # Continue


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def setup_input_handlers(input_queue):
    """Initialize and start GPIO and keyboard input handlers."""
    gpio_keypad = GPIOKeypad(input_queue)
    keyboard = KeyboardInput(input_queue)
    
    gpio_keypad.setup()
    gpio_keypad.running = True
    keyboard.running = True
    
    # Start monitoring threads
    gpio_thread = threading.Thread(target=gpio_keypad.monitor_loop, daemon=True)
    kb_thread = threading.Thread(target=keyboard.monitor_loop, daemon=True)
    gpio_thread.start()
    kb_thread.start()
    time.sleep(0.1)  # Let keyboard prompt appear
    
    return gpio_keypad, keyboard


def run_command_loop(input_queue, gpio_keypad, keyboard):
    """Main event loop - process commands from queue."""
    try:
        while True:
            try:
                # Block until a command arrives (or timeout) — no CPU wasted
                command = input_queue.get(timeout=0.1)
            except Empty:
                continue  # No input yet, loop back

            # Clear any additional inputs that arrived while we process this command
            while not input_queue.empty():
                input_queue.get()  # Discard queued inputs

            should_quit = process_command(command)

            if should_quit:
                print("\n[Shutdown] Exiting...")
                gpio_keypad.running = False
                keyboard.running = False
                gpio_keypad.cleanup()
                print("[Shutdown] Complete")
                print("\033[H\033[J")  # Clear terminal
                sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n[Shutdown] Interrupted")
        gpio_keypad.running = False
        keyboard.running = False
        gpio_keypad.cleanup()
        print("\033[H\033[J")
        sys.exit(0)


def main():
    """Main application entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Illuminate - AI Vision Assistant')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no API calls)')
    args = parser.parse_args()
    
    # Set test mode if flag provided
    if args.test:
        set_test_mode(True)
    
    input_queue = Queue()
    print_test_mode_banner()
    print_banner(has_gpio_hardware())

    # Pre-load the TTS engine while the user reads the banner
    # so the first speak_text() call is instant, not delayed
    warm_up()

    gpio_keypad, keyboard = setup_input_handlers(input_queue)
    run_command_loop(input_queue, gpio_keypad, keyboard)

if __name__ == "__main__":
    main()