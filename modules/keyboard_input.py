"""
Keyboard Input Module
Manages keyboard text input (backup control method)
"""


class KeyboardInput:
    """Manages keyboard input for testing/backup control."""
    
    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.running = False
    
    def monitor_loop(self):
        """Continuously read keyboard input."""
        while self.running:
            try:
                choice = input("\nEnter choice [1=Camera, 2=Voice, q=Quit, 4=Unassigned]: ").strip().lower()
                if choice:
                    self.input_queue.put(choice)
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break
            except Exception as e:
                if self.running:
                    print(f"[Keyboard Error] {e}")
