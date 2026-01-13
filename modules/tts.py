import pyttsx3

def speak_text(text: str):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    test_text = "Hello, this is a test of text to speech."
    speak_text(test_text)

