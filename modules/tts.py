import subprocess
import platform
import shutil

# Cache TTS engine to avoid re-initialization delay
_tts_engine = None

def _get_tts_engine():
    """Get or create cached TTS engine."""
    global _tts_engine
    if _tts_engine is None:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty('rate', 150)
        _tts_engine.setProperty('volume', 1.0)
    return _tts_engine

def speak_text(text: str):
    """
    Cross-platform TTS:
    - Linux (Pi): Uses espeak via subprocess
    - macOS/Windows: Uses pyttsx3 library for native integration
    """
    system_os = platform.system()
    
    try:
        if system_os == "Linux":  # Raspberry Pi
            if shutil.which('espeak'):
                subprocess.run(['espeak', '-ven-us', '-s', '150', '-a', '100', text], 
                             stderr=subprocess.DEVNULL, check=False)
            else:
                print("[TTS] Error: espeak not installed")
        
        else:  # macOS or Windows - use pyttsx3
            engine = _get_tts_engine()
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