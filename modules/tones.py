"""
Simple audio tones for user feedback.
Uses system sounds for simplicity and reliability.
"""

import subprocess
import platform

def play_tone(frequency=800, duration=0.15):
    """Play a simple tone. Works on macOS using afplay with system sounds."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Use system sound for reliability
        subprocess.run(
            ["afplay", "/System/Library/Sounds/Tink.aiff"],
            capture_output=True
        )
    elif system == "Linux":
        # Try beep command or print bell character
        try:
            subprocess.run(["beep", "-f", str(frequency), "-l", str(int(duration * 1000))], 
                         capture_output=True, timeout=1)
        except:
            print("\a", end="", flush=True)  # Terminal bell fallback
    else:
        print("\a", end="", flush=True)  # Terminal bell fallback


def listening_start():
    """Play tone indicating listening has started."""
    play_tone()


def listening_end():
    """Play tone indicating listening has ended."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run(
            ["afplay", "/System/Library/Sounds/Pop.aiff"],
            capture_output=True
        )
    else:
        play_tone()


if __name__ == "__main__":
    print("Testing tones...")
    print("Start tone:")
    listening_start()
    import time
    time.sleep(1)
    print("End tone:")
    listening_end()
