import threading
import time
import sys
import argparse
import os
from queue import Queue
from dotenv import load_dotenv

# Load environment variables once at startup
project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_root, '.env'))

# AI/Vision modules
from modules.cam import capture_image
from modules.openai_vision import get_image_description
from modules.tts import speak_text
from modules.stt_mic import listen_from_mic
from modules.chat import query_openai

# Input modules
from modules.hardware import GPIOKeypad, has_gpio_hardware
from modules.keyboard_input import KeyboardInput
from modules.ui import print_banner
from modules.test_mode import print_test_mode_banner, set_test_mode


# ============================================================================
# COMMAND HANDLERS - What each button does
# ============================================================================

def capture_and_describe():
    """Command 1: Take photo and describe what's in it."""
    try:
        print("\n[Action] Capturing image...")
        capture_image()
        description = get_image_description()
        print(f"[AI] {description}")
        speak_text(description)
    except Exception as e:
        print(f"[Error] Camera/AI failed: {e}")
        speak_text("Sorry, there was an error processing the image.")


def voice_interaction():
    """Command 2: Listen and respond to voice question."""
    try:
        print("\n[Action] Listening...")
        text = listen_from_mic()
        if text:
            print(f"[You said] {text}")
            response = query_openai(text)
            speak_text(response)
        else:
            print("[Info] No speech detected")
            speak_text("I didn't catch that.")
    except Exception as e:
        print(f"[Error] Voice assistant failed: {e}")
        speak_text("Sorry, I couldn't process your request.")


def process_command(command):
    """Process a command and return True if should quit."""
    if command == '1':
        capture_and_describe()
    elif command == '2':
        voice_interaction()
    elif command == 'q':
        return True  # Quit
    elif command == '4':
        print("\n[Info] Button 4 - No function assigned yet")
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
            if not input_queue.empty():
                command = input_queue.get()
                
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
            
            time.sleep(0.1)
    
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
    gpio_keypad, keyboard = setup_input_handlers(input_queue)
    run_command_loop(input_queue, gpio_keypad, keyboard)

if __name__ == "__main__":
    main()