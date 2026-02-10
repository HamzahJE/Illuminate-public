import subprocess
import re
import os
import sys

class PiperTTS:
    """
    Industry-standard wrapper for Piper TTS on Raspberry Pi.
    Handles dynamic USB audio detection and low-latency streaming.
    """
    
    def __init__(self):
        # Auto-detect Piper binary location
        self.piper_binary = self._find_piper_binary()
        if not self.piper_binary:
            raise FileNotFoundError("Piper binary not found. Install with: pip install piper-tts")
        
        # Auto-detect model file
        self.model_path = self._find_model()
        if not self.model_path:
            raise FileNotFoundError("Piper model not found. Install with: piper-tts --download")
        
        # Pi-specific optimization: Smaller buffer for lower latency
        self.buffer_size = 512  # Optimized for low latency on Pi
        
        # Dynamically find the USB hardware once on startup
        self.audio_device = self._detect_usb_audio()

    def _find_piper_binary(self):
        """Auto-detect Piper binary location."""
        # Check if piper is in PATH
        import shutil
        piper_in_path = shutil.which('piper')
        if piper_in_path:
            return piper_in_path
        
        # Common installation locations
        common_paths = [
            os.path.expanduser('~/.local/bin/piper'),
            '/usr/local/bin/piper',
            '/usr/bin/piper',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None

    def _find_model(self):
        """Auto-detect Piper model location."""
        # Common model locations and names
        model_dirs = [
            os.path.join(os.path.dirname(__file__), '..', 'models'),
            os.path.expanduser('~/.local/share/piper'),
            os.path.expanduser('~/piper/models'),
            '/usr/share/piper',
        ]
        
        model_names = [
            'en_US-amy-medium.onnx',
            'en_US-lessac-medium.onnx',
            'en_GB-alan-medium.onnx',
        ]
        
        for model_dir in model_dirs:
            if not os.path.exists(model_dir):
                continue
            for model_name in model_names:
                model_path = os.path.join(model_dir, model_name)
                if os.path.exists(model_path):
                    return model_path
        
        return None

    def _detect_usb_audio(self):
        """Scans system hardware to find the dedicated USB Audio Device."""
        try:
            # List all audio devices
            result = subprocess.check_output(["aplay", "-l"], text=True)
            
            for line in result.split('\n'):
                # Look for the specific USB card line, ignoring the internal 'bcm2835'
                if line.startswith("card") and "USB" in line:
                    # Extract the ALSA card name (e.g., 'Headphones' or 'Device')
                    # Format: card 1: Name [Long Name], ...
                    match = re.search(r'card \d+: (.+?) \[', line)
                    if match:
                        card_name = match.group(1)
                        # Return the direct hardware plugin address
                        return f"plughw:CARD={card_name},DEV=0"
                        
        except Exception as e:
            print(f"[Warning] Audio detection failed: {e}")
            
        # Fallback to system default if USB is missing
        return "default"

    def speak(self, text):
        """
        Synthesizes and streams speech to the USB headset with near-zero latency.
        """
        if not text:
            return

        # 1. Prepare the Piper Command (Producer)
        piper_cmd = [
            self.piper_binary,
            "--model", self.model_path,
            "--output-raw",
            "--length_scale", "1.0" # Adjust speed here (1.0 = normal, 0.8 = fast)
        ]

        # 2. Prepare the Aplay Command (Consumer) - Pi-optimized for low latency
        aplay_cmd = [
            "aplay",
            "-D", self.audio_device,
            "-r", "22050",
            "-f", "S16_LE",
            "-t", "raw",
            "-B", str(self.buffer_size * 1000),  # Buffer in microseconds for low latency
            "-q" # Quiet mode (suppress logs)
        ]

        try:
            # 3. Start Processes with a Pipe
            piper_process = subprocess.Popen(
                piper_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL # Suppress ONNX warnings
            )

            aplay_process = subprocess.Popen(
                aplay_cmd,
                stdin=piper_process.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )

            # 4. Feed the text
            piper_process.stdin.write(text.encode('utf-8'))
            piper_process.stdin.close()

            # 5. Wait for audio to complete
            aplay_process.wait()
            piper_process.wait()

        except BrokenPipeError:
            print("[Error] Audio pipe broke. Is the device disconnected?")
        except Exception as e:
            print(f"[Error] TTS Failed: {e}")

# --- Usage Example ---
if __name__ == "__main__":
    try:
        # Initialize the engine
        tts = PiperTTS()
        print(f"Initialized TTS on device: {tts.audio_device}")
        
        # Speak
        tts.speak("Integration Design and Architecture is online.")
        
    except Exception as e:
        print(f"Initialization Failed: {e}")