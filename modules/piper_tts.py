import os
import re
import time
import threading
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

class PiperTTS:
    """
    Industry-standard wrapper for Piper TTS on Raspberry Pi.
    Features:
    - Auto-detects local model files.
    - Persistent sounddevice streaming (No ALSA cold-starts).
    - Dynamic USB headset detection.
    - On-the-fly NumPy resampling.
    - Sentence chunking & background buffering for minimal Time-to-First-Audio.
    """
    
    def __init__(self, model_path=None):    
        # 1. Auto-detect model file if none is provided
        self.model_path = model_path or self._find_model()
        if not self.model_path:
            raise FileNotFoundError("Piper model not found. Check your models directory.")
        
        print(f"Loading Piper model: {self.model_path}")
        self.voice = PiperVoice.load(self.model_path)
        self.piper_sr = self.voice.config.sample_rate 
        
        # 2. Dynamically find the USB hardware and its native sample rate
        self.device_id, self.native_sr = self._detect_usb_audio()
        
        # 3. Thread-safe audio buffer to prevent script blocking
        self._buffer = np.array([], dtype=np.int16)
        self._lock = threading.Lock()
        
        print(f"Opening background audio channel at {self.native_sr}Hz...")
        
        # 4. Use 'callback' to keep the stream running continuously
        self.stream = sd.OutputStream(
            device=self.device_id,
            samplerate=self.native_sr, 
            channels=1, 
            dtype='int16',
            latency='low',
            callback=self._audio_callback
        )
        self.stream.start()
        print("System Ready! Headset is now locked awake.\n")

    def _find_model(self):
        """Auto-detect Piper model location."""
        # Common model locations and names
        model_dirs = [
            os.path.join(os.path.dirname(__file__), '..', 'models'),
            os.path.expanduser('~/.local/share/piper'),
            os.path.expanduser('~/piper/models'),
            '/usr/share/piper',
            os.path.join(os.path.dirname(__file__), 'models'),
        ]
        
        model_names = [
            'en_US-amy-medium.onnx'
            'en_US-lessac-low.onnx',
            'en_US-amy-low.onnx',
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
        """Scans sounddevice to find the dedicated USB Audio Device."""
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if "USB" in dev.get('name', '') and dev.get('max_output_channels', 0) > 0:
                    native_sr = int(dev.get('default_samplerate', 44100))
                    print(f"Auto-detected USB Audio: {dev['name']} (ID: {i}, Native Rate: {native_sr}Hz)")
                    return i, native_sr
        except Exception as e:
            print(f"[Warning] Audio detection failed: {e}")
            
        print("[Warning] No USB output found. Falling back to system default.")
        try:
            default_dev = sd.query_devices(kind='output')
            return None, int(default_dev['default_samplerate'])
        except Exception:
            return None, 44100

    def _fast_resample(self, audio_bytes):
        """Ultra-fast NumPy linear interpolation to match the hardware's sample rate."""
        data = np.frombuffer(audio_bytes, dtype=np.int16)
        if self.piper_sr == self.native_sr:
            return data
            
        t_orig = np.linspace(0, 1, len(data), endpoint=False)
        t_target = np.linspace(0, 1, int(len(data) * self.native_sr / self.piper_sr), endpoint=False)
        return np.interp(t_target, t_orig, data).astype(np.int16)

    def _audio_callback(self, outdata, frames, time_info, status):
        """
        Runs continuously in the background. 
        Pulls from buffer, or sends pure silence to keep the DAC awake.
        """
        with self._lock:
            if len(self._buffer) >= frames:
                # We have enough speech data to play
                outdata[:, 0] = self._buffer[:frames]
                self._buffer = self._buffer[frames:]
            else:
                # Not enough speech data. Play what we have, pad the rest with silence.
                available = len(self._buffer)
                if available > 0:
                    outdata[:available, 0] = self._buffer
                
                # Magic line that prevents the USB headset from sleeping
                outdata[available:, 0] = 0 
                self._buffer = np.array([], dtype=np.int16)

    def speak(self, text):
        """
        Synthesizes and streams speech to the background buffer instantly.
        Returns: dict: {"started_at": float | None, "finished_at": float | None}
        """
        text_to_speak = str(text).strip() if text is not None else ""
        if not text_to_speak:
            return {"started_at": None, "finished_at": None}

        started_at = None
        
        try:
            sentences = re.split(r'(?<=[.!?]) +', text_to_speak)

            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                for chunk in self.voice.synthesize(sentence):
                    if started_at is None:
                        started_at = time.time()
                    
                    resampled_audio = self._fast_resample(chunk.audio_int16_bytes)
                    
                    # Dump audio to the background thread without blocking
                    with self._lock:
                        self._buffer = np.concatenate((self._buffer, resampled_audio))

        except Exception as e:
            print(f"[Error] TTS Failed: {e}")

        # Note: finished_at marks when queuing is done, the actual audio is playing in the background
        return {"started_at": started_at, "finished_at": time.time()}

    def wait_until_done(self):
        """Keeps the script alive until the background buffer finishes playing."""
        while len(self._buffer) > 0:
            time.sleep(0.1)
        time.sleep(0.5) # Let the final tail frames finish naturally
        
    def close(self):
        """Cleanly shut down the audio stream when your app exits."""
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

# --- Usage Example ---
if __name__ == "__main__":
    try:
        # Initialize the engine
        tts = PiperTTS()
        
        # Speak
        print("Testing...")
        metrics = tts.speak("The system is ready.")
        print(f"Queuing Metrics: {metrics}")
        
        # Keep alive while background thread plays the audio
        tts.wait_until_done()
        tts.close()
        
    except Exception as e:
        print(f"Initialization Failed: {e}")