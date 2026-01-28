import threading
import time
from modules.cam import capture_image
from modules.openai_vision import get_image_description
from modules.tts import speak_text
from modules.stt_mic import listen_from_mic
from modules.chat import query_openai

# Try to import RPi.GPIO, use mock if not available (for testing on laptop)
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    print("[GPIO] Raspberry Pi GPIO detected")
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("[GPIO] Running in TEST MODE (no GPIO hardware)")
    # Mock GPIO for testing
    class MockGPIO:
        BCM = 'BCM'
        IN = 'IN'
        HIGH = 1
        LOW = 0
        PUD_UP = 'PUD_UP'
        
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

# --- GPIO Setup for 1x4 Keypad ---
# Keypad configuration: GPIO23, GPIO24, GPIO25, GPIO8
KEYPAD_PINS = [23, 24, 25, 8]
KEYPAD_KEYS = ['1', '2', 'q', '4']  # Mapping for the 4 keys

# Global flag for quit signal
quit_flag = False
keypad_input_queue = []

def setup_gpio():
    """Initialize GPIO pins for keypad."""
    if not GPIO_AVAILABLE:
        print("[GPIO] Skipping GPIO setup (test mode)")
        return
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for pin in KEYPAD_PINS:
        # Set as input with Pull-Up resistor (button connects to Ground)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    print("[GPIO] Keypad initialized on pins:", KEYPAD_PINS)

def read_keypad():
    """Continuously monitor keypad for button presses."""
    global quit_flag, keypad_input_queue
    
    if not GPIO_AVAILABLE:
        # In test mode, keypad monitoring is disabled
        while not quit_flag:
            time.sleep(1)
        return
    
    # Track last state to detect edges
    last_states = {pin: GPIO.HIGH for pin in KEYPAD_PINS}
    
    while not quit_flag:
        for i, pin in enumerate(KEYPAD_PINS):
            current_state = GPIO.input(pin)
            
            # Detect falling edge (button press)
            if last_states[pin] == GPIO.HIGH and current_state == GPIO.LOW:
                key = KEYPAD_KEYS[i]
                print(f"\n[Keypad] Button pressed: GPIO{pin} -> Key '{key}'")
                
                # Add to queue for main loop to process
                keypad_input_queue.append(key)
                
                # Small delay for debouncing
                time.sleep(0.3)
            
            last_states[pin] = current_state
        
        time.sleep(0.05)  # Small delay to reduce CPU usage

# --- Existing Flows ---

def button_1_flow():
    """Flow 1: Capture and describe image."""
    try:
        print("\n[Action] Capturing image and describing...")
        capture_image()
        description = get_image_description()
        print("Image description:", description)
        speak_text(description)
    except Exception as e:
        print(f"[Error in Flow 1] {e}")
        speak_text("Sorry, there was an error processing the image.")

def button_2_flow():
    """Flow 2: Voice interaction."""
    try:
        print("\n[Action] Listening to microphone...")
        text = listen_from_mic()
        if text:
            print("Recognized text:", text)
            response = query_openai(text)
            speak_text(response)
        else:
            print("[Info] No speech detected")
    except Exception as e:
        print(f"[Error in Flow 2] {e}")
        speak_text("Sorry, there was an error processing your request.")

# --- Main Logic ---

def process_choice(choice):
    """Process a choice from keyboard or keypad."""
    if choice == '1':
        button_1_flow()
    elif choice == '2':
        button_2_flow()
    elif choice == 'q':
        return True  # Signal to quit
    elif choice == '4':
        print("\n[Info] Key 4 pressed - currently unassigned.")
    else:
        if choice:  # Ignore empty inputs
            print("Invalid choice. Use 1, 2, q, or 4.")
    return False

def keyboard_input_thread():
    """Thread to handle keyboard input without blocking."""
    global quit_flag, keypad_input_queue
    
    while not quit_flag:
        try:
            choice = input("Enter choice: ").strip().lower()
            if choice:
                keypad_input_queue.append(choice)
        except (EOFError, KeyboardInterrupt):
            quit_flag = True
            break
        except Exception as e:
            if not quit_flag:
                print(f"[Input Error] {e}")

def main():
    global quit_flag, keypad_input_queue
    
    setup_gpio()
    
    # Start keypad monitoring thread
    keypad_thread = threading.Thread(target=read_keypad, daemon=True)
    keypad_thread.start()
    
    # Start keyboard input thread
    keyboard_thread = threading.Thread(target=keyboard_input_thread, daemon=True)
    keyboard_thread.start()
    
    print("="*60)
    print("  ILLUMINATE - AI Vision Assistant")
    print("="*60)
    print("\nAvailable Commands:")
    print("  [1] - Capture Image & Get AI Description")
    print("        (Takes a photo and describes what it sees)")
    print("  [2] - Voice Assistant")
    print("        (Speak your question and get an AI response)")
    print("  [q] - Quit Program")
    print("  [4] - Unassigned (available for future features)")
    print("\nInput Methods:")
    if GPIO_AVAILABLE:
        print("  • Physical Keypad: GPIO pins (buttons 1, 2, q, 4)")
        print("  • Keyboard: Type command and press Enter")
    else:
        print("  • Keyboard Only: Type command and press Enter")
        print("  • (GPIO disabled - not on Raspberry Pi)")
    print("\n" + "-"*60)
    print("System Ready - Waiting for input...")
    print("-"*60 + "\n")
    
    try:
        while not quit_flag:
            # Check if there's any input from keypad or keyboard
            if keypad_input_queue:
                choice = keypad_input_queue.pop(0)
                should_quit = process_choice(choice)
                if should_quit:
                    print("\nExiting program...")
                    quit_flag = True
                    break
            
            time.sleep(0.1)  # Small delay to reduce CPU usage
    
    except KeyboardInterrupt:
        print("\n[Interrupt] Shutting down...")
    
    finally:
        quit_flag = True
        time.sleep(0.5)  # Give threads time to exit
        GPIO.cleanup()
        print("GPIO Cleaned up.")

if __name__ == "__main__":
    main()