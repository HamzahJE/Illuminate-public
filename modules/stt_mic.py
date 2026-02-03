import speech_recognition as sr
import platform
from modules.tones import listening_start, listening_end

def listen_from_mic(timeout=5, phrase_time_limit=10) -> str:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        # Pi needs longer calibration due to hardware differences
        duration = 0.8 if platform.system() == "Linux" else 0.3
        recognizer.adjust_for_ambient_noise(source, duration=duration)

        listening_start()  # Play tone to indicate listening started
        print("Listening...")
        # Listen for audio from mic
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        listening_end()  # Play tone to indicate listening ended

    try:
        # Use Google Web Speech API by default (requires internet) can use with pocketsphinx for offline
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