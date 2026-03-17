"""
GPIO Keypad Module
Manages 1x4 button keypad connected to Raspberry Pi GPIO pins
Uses gpiozero for clean, high-level GPIO handling.
"""

import time

try:
    from gpiozero import Button  # type: ignore[import-not-found]
    GPIOZERO_AVAILABLE = True
except Exception:
    GPIOZERO_AVAILABLE = False

    class Button:
        """Mock gpiozero Button for non-Pi environments."""

        def __init__(self, pin, pull_up=False, bounce_time=0.5):
            self.pin = pin
            self.pull_up = pull_up
            self.bounce_time = bounce_time
            self.when_pressed = None

        def close(self):
            pass

# Pin-to-Key mapping for 1x4 keypad
PIN_TO_KEY = {
    23: '1',  # Button A -> Camera + AI Description
    22: '2',  # Button B -> Voice Assistant
    27: '4',  # Button C -> Unassigned
    17: 'q',  # Button D -> Quit (temporary)
}


class GPIOKeypad:
    """Manages GPIO keypad hardware interactions using gpiozero."""
    
    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.running = False
        self.buttons = {}
        self._is_available = True
    
    def setup(self):
        """Initialize GPIO pins for keypad input."""
        if not GPIOZERO_AVAILABLE:
            self._is_available = False
            print("[Hardware] gpiozero not available (running in mock mode)")
            return

        try:
            # Create Button objects for each pin
            # pull_up=False: active-high (receiver outputs HIGH when pressed)
            # bounce_time=0.5: ignore RF noise/bounces for 500ms
            for pin, key in PIN_TO_KEY.items():
                button = Button(
                    pin,
                    pull_up=False,
                    bounce_time=0.5
                )
                self.buttons[pin] = button
            
            print(f"[Hardware] Keypad initialized on pins: {list(PIN_TO_KEY.keys())}")
        except Exception as e:
            print(f"[Hardware] Failed to initialize GPIO buttons: {e}")
            self._is_available = False
    
    def monitor_loop(self):
        """Monitor loop using polling (no GPIO edge callbacks)."""
        if not self._is_available:
            while self.running:
                time.sleep(1)
            return

        button_states = {pin: False for pin in self.buttons}

        while self.running:
            for pin, button in self.buttons.items():
                is_pressed = button.is_pressed
                if not button_states[pin] and is_pressed:
                    key = PIN_TO_KEY[pin]
                    print(f"[Hardware] GPIO{pin} pressed -> '{key}'")
                    self.input_queue.put(key)
                button_states[pin] = is_pressed
            time.sleep(0.1)
    
    def cleanup(self):
        """Release GPIO resources."""
        for button in self.buttons.values():
            try:
                button.close()
            except Exception:
                pass


def has_gpio_hardware():
    """Check if running on Raspberry Pi with GPIO hardware."""
    if not GPIOZERO_AVAILABLE:
        return False

    try:
        test_button = Button(2, pull_up=False)
        test_button.close()
        return True
    except Exception:
        return False
