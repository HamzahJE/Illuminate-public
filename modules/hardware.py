"""
GPIO Keypad Module
Manages 1x4 button keypad connected to Raspberry Pi GPIO pins
Uses gpiozero for clean, high-level GPIO handling and software debouncing.
"""

import time

try:
    from gpiozero import Button  # type: ignore[import-not-found]
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False

    class Button:
        """Mock gpiozero Button for non-Pi environments."""
        def __init__(self, pin, pull_up=False, bounce_time=0.1):
            self.pin = pin
            self.pull_up = pull_up
            self.bounce_time = bounce_time
            self.when_pressed = None

        def close(self):
            pass

# Pin-to-Key mapping for 1x4 keypad (BCM Pin Numbers)
PIN_TO_KEY = {
    23: '1',  # Button A -> Camera + AI Description
    22: '2',  # Button B -> Voice Assistant
    27: '3',  # Button C -> Unassigned
    17: '4',  # Button D -> OCR
}

class GPIOKeypad:
    """Manages GPIO keypad hardware interactions using gpiozero."""
    
    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.running = False
        self.buttons = {}
        self._is_available = True
    
    def setup(self):
        """Initialize GPIO pins and assign event callbacks."""
        if not GPIOZERO_AVAILABLE:
            self._is_available = False
            print("[Hardware] gpiozero not available (running in mock mode)")
            return

        try:
            # Create Button objects for each pin
            # pull_up=False: active-high (receiver outputs HIGH when pressed)
            # bounce_time=0.1: ignores CPU voltage spikes and RF noise for 100ms
            for pin, key in PIN_TO_KEY.items():
                button = Button(
                    pin,
                    pull_up=False
                )
                button.when_pressed = self._make_callback(pin, key)
                self.buttons[pin] = button
            
            print(f"[Hardware] Keypad initialized on BCM pins: {list(PIN_TO_KEY.keys())}")
        except Exception as e:
            print(f"[Hardware] Failed to initialize GPIO buttons: {e}")
            self._is_available = False

    def _make_callback(self, pin, key):
        """Factory function to create a unique callback for each button."""
        def callback():
            print(f"[Hardware] GPIO{pin} pressed -> '{key}'")
            self.input_queue.put(key)
        return callback
    
    def monitor_loop(self):
        """
        Keeps the hardware thread alive. 
        Because we use event callbacks (when_pressed), we do not need to poll.
        """
        if not self._is_available:
            while self.running:
                time.sleep(1)
            return

        # Simply keep the thread awake. The callbacks handle the rest asynchronously.
        while self.running:
            time.sleep(1)
    
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
        # Use a high GPIO number (26) for testing to avoid I2C/SPI pin conflicts
        test_button = Button(26, pull_up=False)
        test_button.close()
        return True
    except Exception:
        return False