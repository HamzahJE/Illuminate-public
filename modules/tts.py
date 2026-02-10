import subprocess
import platform
import shutil
import os


# ---------------------------------------------------------------------------
# Cached TTS engines -- created once, reused across calls
# ---------------------------------------------------------------------------
_pyttsx3_engine = None
_piper_engine = None


def _get_pyttsx3_engine():
    """Get or create cached pyttsx3 engine (macOS/Windows)."""
    global _pyttsx3_engine
    if _pyttsx3_engine is None:
        import pyttsx3
        _pyttsx3_engine = pyttsx3.init()
        _pyttsx3_engine.setProperty("rate", 150)
        _pyttsx3_engine.setProperty("volume", 1.0)
    return _pyttsx3_engine


def _get_piper_engine():
    """Get or create cached Piper TTS engine (Linux/Pi)."""
    global _piper_engine
    if _piper_engine is None:
        try:
            from modules.piper_tts import PiperTTS
            _piper_engine = PiperTTS()
            print(f"[TTS] Init            print(f"[TTS] Init            print(f"[TTS]              print(f"[TTS] Inr             pr       nt(f"[TTS] Piper not            print(f"[TTS] Init            print(f"[TTS] Init            pr              print(f"[TTS] Init            print(f"[}")
            print(f"[TTS] Init            print(f"[TTS] Init            p---            pr---------            print------            print(f\ single            print(f"[TTS] Init            print(f"[TTS] Init  -----            print(f"[TTS--------
def speak_text(text: str)def speak_text(text:ss-def speak_text(text: str)def speerry Pi:
    - Linux (Pi): Piper TTS (high quality, low latency) -> espeak fallback
    - macOS/Windows: pyttsx3 for native integration

    Always speaks -- test mode    Always speaks -- test mode    Always speaks -- test modeem_os     Always speaks --
                              == \         
                                                    er                                     er = _get_piper_engine()
            if piper:
                piper.speak(text)
                return

            # Fallback to espeak if Piper is not installed
            if shutil.which("espeak"):
                subprocess.run(["espeak", "-ven-us", "-s", "150", "-a", "100", text],
                             stderr=subprocess.DEVNULL, check=False)
            else:
                print("[TTS] Error: Neither Piper nor espeak available")

        else:  # macOS or Windows
            engine = _get_pyttsx3_engine()
                                                                                                   ("[TTS] Error: pyttsx3 not installed. Install with: pip install pyttsx3")
                                                   rro                                                   rro                                                   rro      Cal                                   y) while                                                    rro                                                   rro       _                ne()


                                 test_text = "Hello, thi                                 test_text = "Hello, thing                                 test_text)
    print("[Test] TTS test complete.")
