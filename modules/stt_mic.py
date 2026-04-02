import speech_recognition as sr
import platform
from modules.tones import listening_start, listening_end
from modules.tts import speak_text

def listen_from_mic(timeout=8, phrase_time_limit=15) -> str:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        # Pi needs longer calibration due to hardware differences
        duration = 0.8 if platform.system() == "Linux" else 0.3
        recognizer.adjust_for_ambient_noise(source, duration=duration)

        # Wait longer before cutting off — prevents losing last words
        recognizer.pause_threshold = 2.0     # 2s of silence = done talking
        recognizer.non_speaking_duration = 0.8  # Keep 0.8s buffer at end
        recognizer.phrase_threshold = 0.3    # 0.3s of speech to start a phrase

        # NOW tell the user to speak — mic is calibrated and ready
        speak_text("Listening.")
        listening_start()  # Play tone to confirm mic is active
        print("Listening...")

        # Listen for audio from mic
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        listening_end()  # Play tone to indicate listening ended
        print("Listening Ended")


    try:
        # Use Google Web Speech API (requires internet)
        # For offline: swap with recognizer.recognize_sphinx(audio)
        print("[STT] Sending audio to Google Speech API...")
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