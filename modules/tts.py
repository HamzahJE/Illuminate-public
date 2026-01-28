# modules/tts.py
import pyttsx3
import threading

# Initialize globally within the module with thread safety
_engine = None
_engine_lock = threading.Lock()

def _get_engine():
    """Get or create TTS engine with proper reference management."""
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty('rate', 150)
        _engine.setProperty('volume', 0.9)
    return _engine

def speak_text(text: str):
    """Speak text with thread safety."""
    print(f"[TTS] Speaking: {text}")
    
    # Use lock to prevent concurrent access in multi-threaded environment
    with _engine_lock:
        try:
            engine = _get_engine()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[TTS Error] {e}")
            # Try to reinitialize engine on error
            global _engine
            _engine = None
            try:
                engine = _get_engine()
                engine.say(text)
                engine.runAndWait()
            except Exception as e2:
                print(f"[TTS Critical Error] {e2}")

# Optional: cleanup function
def stop_tts():
    global _engine
    with _engine_lock:
        if _engine:
            try:
                _engine.stop()
            except:
                pass

# Test the module independently
if __name__ == "__main__":
    test_text = "Hello, this is a test of text to speech."
    print("[Test] Testing TTS module...")
    speak_text(test_text)
    print("[Test] TTS test complete.")