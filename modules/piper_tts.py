import subprocess
import re
import os
import time
import importlib
import io
import wave

class PiperTTS:
    """
    Industry-standard wrapper for Piper TTS on Raspberry Pi.
    Handles dynamic USB audio detection and low-latency streaming.
    """
    
    def __init__(self):
        # Auto-detect model file
        self.model_path = self._find_model()
        if not self.model_path:
            raise FileNotFoundError("Piper model not found. Install with: piper-tts --download")
        
        # Auto-detect Piper binary location for CLI fallback
        self.piper_binary = self._find_piper_binary()
        
        # Pi-specific optimization: Smaller buffer for lower latency
        # 50ms buffer (50000 µs) — was 512ms, causing audible delay before first word
        self.buffer_size = 50  # milliseconds → µs via *1000 in speak()
        self.length_scale = 0.8
        
        # Dynamically find the USB hardware once on startup
        self.audio_device = self._detect_usb_audio()
        self.sample_rate = 22050
        self.voice = None
        self.backend = None

        self._initialize_backend()

    def _initialize_backend(self):
        """Prefer the in-process Python API so the ONNX model stays loaded."""
        try:
            PiperVoice = importlib.import_module("piper").PiperVoice

            config_path = f"{self.model_path}.json"
            self.voice = PiperVoice.load(self.model_path, config_path=config_path)
            self.sample_rate = self.voice.config.sample_rate
            self.backend = "python"
            print(f"[TTS] Piper backend: python API ({self.sample_rate} Hz)")

            if hasattr(self.voice, "synthesize_stream_raw"):
                print("[TTS] Python API mode: streaming raw audio")
            elif hasattr(self.voice, "synthesize"):
                print("[TTS] Python API mode: synthesize WAV fallback")
            else:
                raise AttributeError("PiperVoice has neither synthesize_stream_raw nor synthesize")

            # Warm the inference session once at startup so the first real
            # response doesn't pay the ONNX/session initialization cost.
            t0 = time.time()
            for _ in self._voice_audio_stream("Okay."):
                break
            print(f"[TTS] Piper warm-up complete  +{time.time() - t0:.2f}s")
            return
        except Exception as e:
            print(f"[TTS] Python API unavailable, falling back to CLI: {e}")

        if self.piper_binary:
            self.backend = "cli"
            print("[TTS] Piper backend: CLI")
            return

        raise FileNotFoundError("Neither Piper Python API nor Piper CLI is available. Install with: pip install piper-tts")

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

    def _build_aplay_cmd(self):
        """Build ALSA playback command for raw mono 16-bit audio."""
        return [
            "aplay",
            "-D", self.audio_device,
            "-r", str(self.sample_rate),
            "-f", "S16_LE",
            "-t", "raw",
            "-B", str(self.buffer_size * 1000),
            "-q"
        ]

    def _voice_audio_stream(self, text):
        """Return raw audio chunks from the loaded Piper Python API.

        Supports both newer streaming APIs and older WAV-writing APIs.
        """
        if hasattr(self.voice, "synthesize_stream_raw"):
            yield from self.voice.synthesize_stream_raw(
                text,
                length_scale=self.length_scale,
                sentence_silence=0.0,
            )
            return

        if hasattr(self.voice, "synthesize"):
            import inspect
            sig_params = set(inspect.signature(self.voice.synthesize).parameters.keys())

            # Only pass kwargs the installed version actually accepts
            kwargs = {}
            if "length_scale" in sig_params:
                kwargs["length_scale"] = self.length_scale
            if "sentence_silence" in sig_params:
                kwargs["sentence_silence"] = 0.0

            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                self.voice.synthesize(text, wav_file, **kwargs)

            wav_buffer.seek(0)
            with wave.open(wav_buffer, "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                if sample_rate != self.sample_rate:
                    self.sample_rate = sample_rate
                while True:
                    chunk = wav_file.readframes(2048)
                    if not chunk:
                        break
                    yield chunk
            return

        raise AttributeError("PiperVoice has neither synthesize_stream_raw nor synthesize")

    def _play_stream(self, audio_stream, t0):
        """Play a stream of raw audio chunks through aplay."""
        aplay_process = None

        try:
            aplay_process = subprocess.Popen(
                self._build_aplay_cmd(),
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )

            first_chunk_time = None
            total_bytes = 0

            for chunk in audio_stream:
                if not chunk:
                    continue

                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    print(f"[TTS] First audio chunk ready  +{first_chunk_time - t0:.2f}s")

                aplay_process.stdin.write(chunk)
                total_bytes += len(chunk)

            if aplay_process.stdin:
                aplay_process.stdin.close()

            aplay_process.wait()
            aplay_stderr = aplay_process.stderr.read().decode('utf-8', errors='replace').strip()

            t_done = time.time()
            if first_chunk_time is None:
                print(f"[TTS] No audio generated  +{t_done - t0:.2f}s")
            else:
                print(f"[TTS] Playback finished  +{t_done - t0:.2f}s total ({total_bytes} bytes)")

            if aplay_process.returncode != 0:
                print(f"[TTS] aplay error (rc={aplay_process.returncode}): {aplay_stderr}")
            elif aplay_stderr:
                print(f"[TTS] aplay warning: {aplay_stderr}")

        except BrokenPipeError:
            print("[TTS] Audio pipe broke — is the USB audio device disconnected?")
        finally:
            if aplay_process and aplay_process.stdin and not aplay_process.stdin.closed:
                aplay_process.stdin.close()

    def speak(self, text):
        """
        Synthesizes and streams speech to the USB headset with near-zero latency.
        """
        if not text:
            return

        t0 = time.time()

        try:
            if self.backend == "python":
                print("[TTS] Speaking with cached Piper model")
                audio_stream = self._voice_audio_stream(text)
                self._play_stream(audio_stream, t0)
                return

            # CLI fallback: still works, but slower because each call spawns piper
            piper_cmd = [
                self.piper_binary,
                "--model", self.model_path,
                "--output-raw",
                "--length_scale", str(self.length_scale)
            ]

            piper_process = subprocess.Popen(
                piper_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            try:
                audio_stream = iter(lambda: piper_process.stdout.read(4096), b"")

                print("[TTS] Speaking with Piper CLI fallback")
                piper_process.stdin.write((text.strip() + "\n").encode('utf-8'))
                piper_process.stdin.close()

                self._play_stream(audio_stream, t0)
            finally:
                if piper_process.stdout:
                    piper_process.stdout.close()

            piper_process.wait()

        except BrokenPipeError:
            print("[TTS] Audio pipe broke — is the USB audio device disconnected?")
        except Exception as e:
            print(f"[TTS] Error: {e}")

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