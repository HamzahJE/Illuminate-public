"""
IR Remote Module
Reads IR remote button presses via ir-keytable and maps them to commands.
Uses a TL-1838 IR receiver on GPIO-17.

Debounce strategy: "fire on release"
  - While a button is held, ir-keytable floods repeated scancodes (~110ms apart).
  - We track when a scancode was last seen.
  - A release checker thread fires the command only after the repeats stop
    (no scancode for RELEASE_THRESHOLD_MS), meaning the button was released.
  - Result: exactly ONE command per button press, no matter how long held.
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

# How long (seconds) after the last repeat before we consider the button released.
# NEC remotes repeat every ~110ms, so 200ms gap = definitely released.
RELEASE_THRESHOLD = 0.20


class IRRemote:
    """Monitors IR remote via ir-keytable and feeds commands into the input queue."""

    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.running = False
        self._process = None
        self._lock = threading.Lock()
        # Tracks the last time each scancode was seen (only for mapped codes)
        # Key: scancode str, Value: timestamp (time.monotonic)
        self._last_seen = {}
        # Tracks which scancodes have already been fired (waiting for full release)
        self._fired = set()

    def _reader_loop(self):
        """Read ir-keytable output and update last-seen timestamps."""
        while self.running:
            try:
                # Use stdbuf to force ir-keytable to line-buffer stdout.
                # Without this, glibc block-buffers pipe output (~4KB),
                # causing a long delay before Python sees any lines.
                self._process = subprocess.Popen(
                    ["stdbuf", "-oL", "ir-keytable", "--test"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    bufsize=1,
                )

                for line in self._process.stdout:
                    if not self.running:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    match = re.search(r"scancode\s*=?\s*(0x[0-9a-fA-F]+)", line)
                    if match:
                        scancode = match.group(1).lower()
                        if scancode in IR_SCANCODE_MAP:
                            with self._lock:
                                self._last_seen[scancode] = time.monotonic()

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

    def _release_checker_loop(self):
        """Poll for button releases and fire commands exactly once per press."""
        while self.running:
            now = time.monotonic()
            with self._lock:
                for scancode, last_time in list(self._last_seen.items()):
                    elapsed = now - last_time
                    if elapsed >= RELEASE_THRESHOLD and scancode not in self._fired:
                        # Button was released — fire the command once
                        command = IR_SCANCODE_MAP[scancode]
                        print(f"[IR Remote] Button released: {scancode} -> '{command}'")
                        self.input_queue.put(command)
                        self._fired.add(scancode)

                # Clean up: if a scancode hasn't been seen for a while, remove it
                # so the next fresh press is detected
                stale = [sc for sc, t in self._last_seen.items() if now - t > 0.5]
                for sc in stale:
                    del self._last_seen[sc]
                    self._fired.discard(sc)

            time.sleep(0.05)  # Check every 50ms

    def monitor_loop(self):
        """Start reader and release-checker threads."""
        print("[IR Remote] Starting ir-keytable listener (release-to-fire mode)...")

        # Start the release checker in a separate daemon thread
        checker = threading.Thread(target=self._release_checker_loop, daemon=True)
        checker.start()

        # Run the reader in this thread (blocking)
        self._reader_loop()

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
