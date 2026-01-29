"""
GPIO Keypad Module
Manages 1x4 button keypad connected to Raspberry Pi GPIO pins
"""

import time

# Try to import RPi.GPIO, use mock if not available
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    
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


# Pin-to-Key mapping for 1x4 keypad
PIN_TO_KEY = {
    23: '1',  # GPIO23 -> Button 1 (Camera + AI Description)
    24: '2',  # GPIO24 -> Button 2 (Voice Assistant)
    25: 'q',  # GPIO25 -> Button Q (Quit)
    8:  '4',  # GPIO8  -> Button 4 (Unassigned)
}


class GPIOKeypad:
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
        for pin in PIN_TO_KEY.keys():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print(f"[Hardware] Keypad initialized on pins: {list(PIN_TO_KEY.keys())}")
    
    def monitor_loop(self):
        """Continuously monitor hardware buttons for presses."""
        if not GPIO_AVAILABLE:
            # No hardware available, just wait
            while self.running:
                time.sleep(1)
            return
        
        # Track button states for edge detection
        button_states = {pin: GPIO.HIGH for pin in PIN_TO_KEY.keys()}
        
        while self.running:
            for pin, key in PIN_TO_KEY.items():
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


def has_gpio_hardware():
    """Check if running on Raspberry Pi with GPIO hardware."""
    return GPIO_AVAILABLE
