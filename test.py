import re
import time
import threading
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

class PiperTTS:
    def __init__(self, model_path="/home/admin/Desktop/Illuminate-public/mo>
        self.model_path = model_path
        
        print(f"Loading Piper model: {self.model_path}")
        self.voice = PiperVoice.load(self.model_path)
        self.piper_sr = self.voice.config.sample_rate 
        
        self.device_id, self.native_sr = self._detect_usb_audio()
        
        # --- NEW: Thread-safe audio buffer ---
        self._buffer = np.array([], dtype=np.int16)
        self._lock = threading.Lock()
        
        print(f"Opening background audio channel at {self.native_sr}Hz...")
        
        # Notice we use 'callback' instead of writing to the stream manually
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
    def _detect_usb_audio(self):
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if "USB" in dev.get('name', '') and dev.get('max_output_cha>
                    native_sr = int(dev.get('default_samplerate', 44100))
                    return i, native_sr
        except Exception:
            pass
        return None, 44100
    def _fast_resample(self, audio_bytes):
        data = np.frombuffer(audio_bytes, dtype=np.int16)
        if self.piper_sr == self.native_sr:
            return data
            
        t_orig = np.linspace(0, 1, len(data), endpoint=False)
        t_target = np.linspace(0, 1, int(len(data) * self.native_sr / self.>
        return np.interp(t_target, t_orig, data).astype(np.int16)

    def _audio_callback(self, outdata, frames, time_info, status):
        """
        This runs continuously in the background. 
        It pulls from our buffer, or sends pure silence to keep the DAC awa>
        """
        with self._lock:
            if len(self._buffer) >= frames:
                # We have enough speech data to play
                outdata[:, 0] = self._buffer[:frames]
                self._buffer = self._buffer[frames:]
            else:
                # Not enough speech data. Play what we have, pad the rest w>
                available = len(self._buffer)
                if available > 0:
                    outdata[:available, 0] = self._buffer
                
                # THIS is the magic line that prevents the USB headset from>
                outdata[available:, 0] = 0 
                self._buffer = np.array([], dtype=np.int16)
    def speak(self, text):
        text_to_speak = str(text).strip() if text is not None else ""
        if not text_to_speak:
            return

        start_call = time.time()
        started_at = None

        try:
            sentences = re.split(r'(?<=[.!?]) +', text_to_speak)

            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                for chunk in self.voice.synthesize(sentence):
                    if started_at is None:
                        started_at = time.time()
                        ttfa_ms = (started_at - start_call) * 1000
                        print(f"--> Time to First Audio (TTFA): {ttfa_ms:.2>
                    
                    resampled_audio = self._fast_resample(chunk.audio_int16>
                    
                    # Instead of blocking the script, we instantly dump aud>
                    with self._lock:
                        self._buffer = np.concatenate((self._buffer, resamp>

        except Exception as e:
            print(f"[Error] TTS Failed: {e}")

    def wait_until_done(self):
        """Keeps the script alive until the background buffer finishes play"""
        while len(self._buffer) > 0:
            time.sleep(0.1)
        time.sleep(0.5) # Let the final tail frames finish naturally
        
    def close(self):
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

# --- Usage Example ---
if __name__ == "__main__":
    tts = PiperTTS()
    
    test_text = "This is a true background streaming test. The headset is k>
    
    print(f'Speaking: "{test_text}"')
    
    # Notice how this returns instantly now! The speaking happens in the ba>
    tts.speak(test_text)
    
    # We must wait for the audio to finish before closing the script
    tts.wait_until_done()
    tts.close()

