import speech_recognition as sr
import platform
import ctypes
from modules.tones import listening_start, listening_end
from modules.tts import speak_text


# ---------------------------------------------------------------------------
# Suppress ALSA warnings on Linux
# ---------------------------------------------------------------------------
# PyAudio's C layer prints harmless ALSA warnings when scanning audio devices.
# They clutter the console but don't affect functionality.  We redirect
# ALSA's internal error handler to a silent no-op so output stays clean.
# ---------------------------------------------------------------------------
def _suppress_alsa_warnings():
    """Redirect ALSA error messages to a silent handler."""
    try:
        asound = ctypes.cdll.LoadLibrary("libasound.so.2")
        ERROR_HANDLER = ctypes.CFUNCTYPE(None,
                                         ctypes.c_char_p,
                                         ctypes.c_int,
                                         ctypes.c_char_p,
                                         ctypes.c_int,
                                         ctypes.c_char_p)
        _silent = ERROR_HANDLER(lambda *_: None)
        asound.snd_lib_error_set_handler(_silent)
        _suppress_alsa_warnings._handler = _silent
    except OSError:
        pass


if platform.system() == "Linux":
    _suppress_alsa_warnings()


# ---------------------------------------------------------------------------
# Microphone listener
# ---------------------------------------------------------------------------
def listen_from_mic(timeout=8, phrase_time_limit=15) -> str:
    """Listen for speech via microphone and return the transcribed text."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        # Pi needs longer calibration due to USB audio hardware differences
        duration = 0.8 if platform.system() == "Linux" else 0.3
        recognizer.adjust_for_ambient_noise(source, duration=duration)

        # Tuned thresholds — prevent cutting off the last word
        recognizer.pause_threshold = 2.0      # 2s of silence = done talking
        recognizer.non_speaking_duration = 0.8 # Keep 0.8s buffer at end
        recognizer.phrase_threshold = 0.3     # 0.3s of speech to start a phrase

        # NOW tell the user to speak — mic is calibrated and truly ready
        speak_text("Listening.")
        listening_start()  # Play tone to confirm mic is active
        print("Listening...")

        # Listen for audio — catch timeout so silence doesn't crash the app
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            # No speech detected within the timeout window — not an error
            listening_end()
            print("No speech detected (timed out)")
            return ""

        listening_end()  # Play tone to indicate listening ended

    try:
        # Use Google Web Speech API (requires internet)
        # For offline: swap with recognizer.recognize_sphinx(audio)
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""

if __name__ == "__main__":
    listen_from_mic()