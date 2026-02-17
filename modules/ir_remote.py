"""
IR Remote Module
Reads IR remote button presses via ir-keytable and maps them to commands.
Uses a TL-1838 IR receiver on GPIO-17.
"""

import subprocess
import threading
import re
import time


# Scancode-to-command mapping
# Add more entries here to map additional remote buttons
IR_SCANCODE_MAP = {
    "0x0c": "1",  # Remote button -> Camera + AI Description
    "0x18": "2",  # Remote button -> Voice Assistant
}


class IRRemote:
    """Monitors IR remote via ir-keytable and feeds commands into the input queue."""

    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.running = False
        self._process = None

    def monitor_loop(self):
        """Continuously read IR events from ir-keytable --test."""
        print("[IR Remote] Starting ir-keytable listener...")

        while self.running:
            try:
                # Launch ir-keytable in test mode to stream key events
                self._process = subprocess.Popen(
                    ["ir-keytable", "--test"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line-buffered
                )

                for line in self._process.stdout:
                    if not self.running:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    # ir-keytable output typically looks like:
                    #   <timestamp>: lirc protocol(...): scancode = 0x0c
                    #   <timestamp>: event ... key_down
                    # We look for scancode lines
                    match = re.search(r"scancode\s*=?\s*(0x[0-9a-fA-F]+)", line)
                    if match:
                        scancode = match.group(1).lower()
                        if scancode in IR_SCANCODE_MAP:
                            command = IR_SCANCODE_MAP[scancode]
                            print(f"[IR Remote] Scancode {scancode} -> '{command}'")
                            self.input_queue.put(command)
                            # Debounce: ignore repeat presses briefly
                            time.sleep(0.4)

                # If the process exits, wait before restarting
                if self.running:
                    print("[IR Remote] ir-keytable exited, restarting in 2s...")
                    time.sleep(2)

            except FileNotFoundError:
                print("[IR Remote] ir-keytable not found. IR remote disabled.")
                break
            except Exception as e:
                if self.running:
                    print(f"[IR Remote] Error: {e}, retrying in 3s...")
                    time.sleep(3)

    def stop(self):
        """Stop the IR monitoring process."""
        self.running = False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                pass


def has_ir_keytable():
    """Check if ir-keytable is available on the system."""
    try:
        result = subprocess.run(
            ["which", "ir-keytable"],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False
