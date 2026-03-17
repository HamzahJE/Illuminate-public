import subprocess
import re
import os
import time
import tempfile
import wave
from piper.voice import PiperVoice  # type: ignore[import-not-found]

try:
    import onnxruntime as ort  # type: ignore[import-not-found]
except Exception:
    ort = None

class PiperTTS:
    """
    Industry-standard wrapper for Piper TTS on Raspberry Pi.
    Handles dynamic USB audio detection and low-latency streaming.
    """
    
    def __init__(self):
        # Reduce ONNX Runtime console noise (e.g., GPU discovery warnings on Pi)
        if ort is not None:
            try:
                ort.set_default_logger_severity(3)  # 0=verbose, 1=info, 2=warning, 3=error, 4=fatal
            except Exception:
                pass

        # Auto-detect model file
        self.model_path = self._find_model()
        if not self.model_path:
            raise FileNotFoundError("Piper model not found. Install with: piper-tts --download")
        
        # Pi-specific optimization: lower playback buffer for faster audible start
        self.buffer_size = 200  # milliseconds; passed to aplay as microseconds
        self.preroll_ms = 5  # small silence to prevent first-word clipping on some USB devices
        
        # Dynamically find the USB hardware once on startup
        self.audio_device = self._detect_usb_audio()

        # Load Piper voice once (persistent in-process model)
        self.voice = PiperVoice.load(self.model_path)

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
            'en_US-lessac-low.onnx',
            'en_US-amy-low.onnx',
            # 'en_US-amy-medium.onnx',
            # 'en_US-lessac-medium.onnx',
            # 'en_GB-alan-medium.onnx',
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

    def _synthesize_and_play_wav(self, text_to_speak):
        """Fallback path: synthesize to WAV file and play via aplay."""
        wav_path = None
        started_at = None
        finished_at = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                wav_path = tmp_wav.name

            with wave.open(wav_path, "wb") as wav_file:
                if hasattr(self.voice, "synthesize_wav"):
                    self.voice.synthesize_wav(text_to_speak, wav_file)
                else:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(22050)
                    self.voice.synthesize(text_to_speak, wav_file)

            started_at = time.time()
            play_wav = subprocess.Popen(
                ["aplay", "-D", self.audio_device, "-q", wav_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            play_wav.wait()
            finished_at = time.time()
            return {"started_at": started_at, "finished_at": finished_at}
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass

    def speak(self, text):
        """
        Synthesizes and streams speech to the USB headset with near-zero latency.

        Returns:
            dict: {"started_at": float | None, "finished_at": float | None}
        """
        text_to_speak = str(text).strip() if text is not None else ""
        if not text_to_speak:
            return {"started_at": None, "finished_at": None}

        started_at = None
        finished_at = None
        aplay_process = None

        def _start_aplay(sample_rate=22050, sample_channels=1, sample_width=2):
            fmt_map = {
                1: "S8",
                2: "S16_LE",
                4: "S32_LE",
            }
            sample_format = fmt_map.get(sample_width, "S16_LE")
            return subprocess.Popen(
                [
                    "aplay",
                    "-D", self.audio_device,
                    "-r", str(sample_rate),
                    "-c", str(sample_channels),
                    "-f", sample_format,
                    "-t", "raw",
                    "-B", str(self.buffer_size * 1000),
                    "-q",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )

        try:
            # 4. Stream synthesized PCM chunks from Piper Python API
            if not hasattr(self.voice, "synthesize"):
                return self._synthesize_and_play_wav(text_to_speak)

            for chunk in self.voice.synthesize(text_to_speak):
                if not chunk:
                    continue

                if hasattr(chunk, "audio_int16_bytes"):
                    chunk_bytes = chunk.audio_int16_bytes
                    sample_rate = getattr(chunk, "sample_rate", 22050)
                    sample_channels = getattr(chunk, "sample_channels", 1)
                    sample_width = getattr(chunk, "sample_width", 2)
                else:
                    chunk_bytes = bytes(chunk) if not isinstance(chunk, bytes) else chunk
                    sample_rate = 22050
                    sample_channels = 1
                    sample_width = 2

                if not chunk_bytes:
                    continue

                if aplay_process is None:
                    aplay_process = _start_aplay(
                        sample_rate=sample_rate,
                        sample_channels=sample_channels,
                        sample_width=sample_width,
                    )

                    # Prime output device to avoid clipping first spoken phonemes.
                    bytes_per_sample = sample_width if sample_width in (1, 2, 4) else max(1, sample_width // 8)
                    silence_bytes = int(sample_rate * sample_channels * bytes_per_sample * (self.preroll_ms / 1000.0))
                    if silence_bytes > 0:
                        aplay_process.stdin.write(b"\x00" * silence_bytes)

                if started_at is None:
                    started_at = time.time()
                aplay_process.stdin.write(chunk_bytes)

            if aplay_process is None:
                return self._synthesize_and_play_wav(text_to_speak)

            aplay_process.stdin.close()

            # 5. Wait for audio to complete
            aplay_process.wait()

            # If stream path produced no playable PCM, use WAV fallback.
            if started_at is None:
                return self._synthesize_and_play_wav(text_to_speak)

            finished_at = time.time()
            return {"started_at": started_at, "finished_at": finished_at}

        except BrokenPipeError:
            print("[Error] Audio pipe broke. Is the device disconnected?")
        except Exception as e:
            print(f"[Error] TTS Failed: {e}")

        return {"started_at": started_at, "finished_at": finished_at}

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