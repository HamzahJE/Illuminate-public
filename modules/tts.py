import subprocess
import platform
import shutil


# ---------------------------------------------------------------------------
# Cached TTS engines — created once, reused across calls
# ---------------------------------------------------------------------------
_pyttsx3_engine = None
_piper_engine = None


def _get_pyttsx3_engine():
    """Get or create cached pyttsx3 engine (macOS/Windows)."""
    global _pyttsx3_engine
    if _pyttsx3_engine is None:
        import pyttsx3
        _pyttsx3_engine = pyttsx3.init()
        _pyttsx3_engine.setProperty('rate', 150)
        _pyttsx3_engine.setProperty('volume', 1.0)
    return _pyttsx3_engine


def _get_piper_engine():
    """Get or create cached Piper TTS engine (Linux/Pi)."""
    global _piper_engine
    if _piper_engine is None:
        try:
            from modules.piper_tts import PiperTTS
            _piper_engine = PiperTTS()
            print(f"[TTS] Initialized Piper on device: {_piper_engine.audio_device}")
        except FileNotFoundError as e:
            print(f"[TTS] Piper not available: {e}")
            return None
        except Exception as e:
            print(f"[TTS] Failed to initialize Piper: {e}")
            return None
    return _piper_engine


# ---------------------------------------------------------------------------
# Public API — single entry point for all TTS
# ---------------------------------------------------------------------------
def speak_text(text: str):
    """
    Cross-platform TTS optimized for Raspberry Pi:
    - Linux (Pi): Piper TTS (high quality, low latency) → espeak fallback
    - macOS/Windows: pyttsx3 for native integration

    Always speaks — test mode only skips API calls, not audio output.
    """
    system_os = platform.system()

    try:
        if system_os == "Linux":
            # Try Piper first (neural TTS, much better quality than espeak)
            piper = _get_piper_engine()
            if piper:
                piper.speak(text)
                return

            # Fallback to espeak if Piper isn't installed
            if shutil.which('espeak'):
                subprocess.run(['espeak', '-ven-us', '-s', '150', '-a', '100', text],
                             stderr=subprocess.DEVNULL, check=False)
            else:
                print("[TTS] Error: Neither Piper nor espeak available")

        else:  # macOS or Windows
            engine = _get_pyttsx3_engine()
            engine.say(text)
            engine.runAndWait()

    except ImportError:
        print("[TTS] Error: pyttsx3 not installed. Install with: pip install pyttsx3")
    except Exception as e:
        print(f"[TTS] Error: {e}")


if __name__ == "__main__":
    test_text = "Hello, this is a test of text to speech."
    print("[Test] Testing TTS module...")
    speak_text(test_text)
    print("[Test] TTS test complete.")