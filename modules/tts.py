import subprocess
import platform
import shutil
import os
from modules.test_mode import is_test_mode

# Cache TTS engines to avoid re-initialization delay
_tts_engine = None
_piper_tts = None

def _get_pyttsx3_engine():
    """Get or create cached pyttsx3 engine."""
    global _tts_engine
    if _tts_engine is None:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty('rate', 150)
        _tts_engine.setProperty('volume', 1.0)
    return _tts_engine

def _get_piper_engine():
    """Get or create cached Piper TTS engine."""
    global _piper_tts
    if _piper_tts is None:
        try:
            from modules.piper_tts import PiperTTS
            _piper_tts = PiperTTS()
            print(f"[TTS] Initialized Piper on device: {_piper_tts.audio_device}")
        except FileNotFoundError as e:
            print(f"[TTS] Piper model not found: {e}")
            return None
        except Exception as e:
            print(f"[TTS] Failed to initialize Piper: {e}")
            return None
    return _piper_tts

def speak_text(text: str):
    """
    Cross-platform TTS optimized for Raspberry Pi:
    - Linux (Pi): Prefers Piper TTS (high quality, low latency), falls back to espeak
    - macOS/Windows: Uses pyttsx3 library for native integration
    - Test Mode: Prints text instead of speaking
    
    Pi optimization: Piper engine cached on first call for instant subsequent responses
    """
    # In test mode, just print what would be spoken
    if is_test_mode():
        print(f"[TTS Test Mode] Would speak: '{text}'")
        return
    
    system_os = platform.system()
    
    try:
        if system_os == "Linux":  # Raspberry Pi or Linux
            # Try Piper first (if configured)
            piper = _get_piper_engine()
            if piper:
                piper.speak(text)
                return
            
            # Fallback to espeak
            if shutil.which('espeak'):
                subprocess.run(['espeak', '-ven-us', '-s', '150', '-a', '100', text], 
                             stderr=subprocess.DEVNULL, check=False)
            else:
                print("[TTS] Error: Neither Piper nor espeak available")
        
        else:  # macOS or Windows - use pyttsx3
            engine = _get_pyttsx3_engine()
            engine.say(text)
            engine.runAndWait()

    except ImportError:
        print(f"[TTS] Error: pyttsx3 not installed. Install with: pip install pyttsx3")
    except Exception as e:
        print(f"[TTS] Error: {e}")

if __name__ == "__main__":
    test_text = "Hello, this is a test of text to speech."
    print("[Test] Testing TTS module...")
    speak_text(test_text)
    print("[Test] TTS test complete.")