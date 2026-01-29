import threading
import time
import sys
from queue import Queue

# Import AI/Vision modules
from modules.cam import capture_image
from modules.openai_vision import get_image_description
from modules.tts import speak_text
from modules.stt_mic import listen_from_mic
from modules.chat import query_openai


# ============================================================================
# HARDWARE SETUP - GPIO Configuration
# ============================================================================

# Detect if running on Raspberry Pi with GPIO hardware
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    print("[Hardware] Raspberry Pi GPIO detected")
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("[Hardware] Running in SOFTWARE-ONLY mode (no GPIO)")
    
    # Mock GPIO for testing on laptop/desktop
    class MockGPIO:
        BCM, IN, HIGH, LOW, PUD_UP = 'BCM', 'IN', 1, 0, 'PUD_UP'
        @staticmethod
        def setmode(mode): pass
        @staticmethod
        def setwarnings(flag): pass
        @staticmethod
        def setup(pin, mode, pull_up_down=None): pass
        @staticmethod
        def input(pin): return 1  # Always HIGH (not pressed)
        @staticmethod
        def cleanup(): pass
    GPIO = MockGPIO()


# Hardware Configuration: 1x4 Keypad
KEYPAD_CONFIG = {
    23: '1',  # GPIO23 -> Button 1 (Camera + AI Description)
    24: '2',  # GPIO24 -> Button 2 (Voice Assistant)
    25: 'q',  # GPIO25 -> Button Q (Quit)
    8:  '4',  # GPIO8  -> Button 4 (Unassigned)
}


class HardwareInterface:
    """Manages GPIO keypad hardware interactions."""
    
    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.running = False
        
    def setup(self):
        """Initialize GPIO pins for keypad input."""
        if not GPIO_AVAILABLE:
            return
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configure each pin as input with pull-up resistor
        for pin in KEYPAD_CONFIG.keys():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print(f"[Hardware] Keypad initialized: {list(KEYPAD_CONFIG.keys())}")
    
    def monitor_loop(self):
        """Continuously monitor hardware buttons for presses."""
        if not GPIO_AVAILABLE:
            # No hardware available, just wait
            while self.running:
                time.sleep(1)
            return
        
        # Track button states for edge detection
        button_states = {pin: GPIO.HIGH for pin in KEYPAD_CONFIG.keys()}
        
        while self.running:
            for pin, key in KEYPAD_CONFIG.items():
                current = GPIO.input(pin)
                
                # Detect button press (falling edge: HIGH -> LOW)
                if button_states[pin] == GPIO.HIGH and current == GPIO.LOW:
                    print(f"[Hardware] GPIO{pin} pressed -> '{key}'")
                    self.input_queue.put(key)
                    time.sleep(0.3)  # Debounce delay
                
                button_states[pin] = current
            
            time.sleep(0.05)  # Polling interval
    
    def cleanup(self):
        """Release GPIO resources."""
        GPIO.cleanup()


# ============================================================================
# SOFTWARE INPUT - Keyboard Interface
# ============================================================================

class KeyboardInterface:
    """Manages keyboard input for testing/backup control."""
    
    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.running = False
    
    def monitor_loop(self):
        """Continuously read keyboard input."""
        while self.running:
            try:
                choice = input("Enter choice: ").strip().lower()
                if choice:
                    self.input_queue.put(choice)
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break
            except Exception as e:
                if self.running:
                    print(f"[Keyboard Error] {e}")


# ============================================================================
# APPLICATION LOGIC - Command Handlers
# ============================================================================

def execute_camera_capture():
    """Command 1: Capture image and get AI description."""
    try:
        print("\n[Action] Capturing image...")
        capture_image()
        description = get_image_description()
        print(f"[AI] {description}")
        speak_text(description)
    except Exception as e:
        print(f"[Error] Camera/AI failed: {e}")
        speak_text("Sorry, there was an error processing the image.")


def execute_voice_assistant():
    """Command 2: Listen to microphone and respond."""
    try:
        print("\n[Action] Listening...")
        text = listen_from_mic()
        if text:
            print(f"[You said] {text}")
            response = query_openai(text)
            speak_text(response)
        else:
            print("[Info] No speech detected")
    except Exception as e:
        print(f"[Error] Voice assistant failed: {e}")
        speak_text("Sorry, I couldn't process your request.")


def execute_command(command):
    """Execute the appropriate action for a command."""
    commands = {
        '1': execute_camera_capture,
        '2': execute_voice_assistant,
        '4': lambda: print("\n[Info] Button 4 - No function assigned yet"),
    }
    
    if command in commands:
        commands[command]()
    elif command == 'q':
        return True  # Signal to quit
    elif command:
        print(f"[Invalid] Unknown command: '{command}'")
    
    return False  # Continue running


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def print_startup_banner(has_gpio):
    """Display welcome screen and instructions."""
    print("=" * 60)
    print("  ILLUMINATE - AI Vision Assistant")
    print("=" * 60)
    print("\nCommands:")
    print("  [1] Camera + AI Description")
    print("  [2] Voice Assistant")
    print("  [q] Quit")
    print("  [4] Unassigned")
    print("\nInput:")
    if has_gpio:
        print("  • Hardware Keypad (GPIO buttons)")
        print("  • Keyboard (type + Enter)")
    else:
        print("  • Keyboard Only (type + Enter)")
    print("\n" + "-" * 60)
    print("Ready for input...")
    print("-" * 60 + "\n")


def main():
    """Main application entry point."""
    
    # Shared input queue for both hardware and software
    input_queue = Queue()
    
    # Initialize hardware and software interfaces
    hardware = HardwareInterface(input_queue)
    keyboard = KeyboardInterface(input_queue)
    
    # Setup hardware
    hardware.setup()
    
    # Start input monitoring threads
    hardware.running = True
    keyboard.running = True
    
    hw_thread = threading.Thread(target=hardware.monitor_loop, daemon=True)
    kb_thread = threading.Thread(target=keyboard.monitor_loop, daemon=True)
    
    hw_thread.start()
    kb_thread.start()
    
    # Show welcome screen
    print_startup_banner(GPIO_AVAILABLE)
    
    # Main event loop
    try:
        while True:
            if not input_queue.empty():
                command = input_queue.get()
                should_quit = execute_command(command)
                
                if should_quit:
                    print("\n[Shutdown] Exiting...")
                    break
            
            time.sleep(0.1)  # Reduce CPU usage
    
    except KeyboardInterrupt:
        print("\n[Shutdown] Interrupted by user")
    
    finally:
        # Clean shutdown
        hardware.running = False
        keyboard.running = False
        time.sleep(0.5)  # Let threads finish
        hardware.cleanup()
        print("[Shutdown] Cleanup complete")
        print("\033[H\033[J")  # Clear terminal
        sys.exit(0)

if __name__ == "__main__":
    main()