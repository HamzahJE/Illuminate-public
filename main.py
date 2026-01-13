from modules.cam import capture_image
from modules.openai_vision import get_image_description
from modules.tts import speak_text
from modules.stt_mic import listen_from_mic
from modules.chat import query_openai


def button_1_flow():
    print("[Button 1] Capture image, query LLM, speak description")
    capture_image()
    description = get_image_description()
    print("Image description:", description)
    speak_text(description)

def button_2_flow():
    print("[Button 2] Listen to mic and convert speech to text")
    text = listen_from_mic()
    print("Recognized text:", text)
    response=query_openai(text)
    speak_text(response)

    
    

def main():
    print("Press 1 for image capture + description + TTS")
    print("Press 2 for speech-to-text listening")
    print("Press q to quit")
    while True:
        choice = input("Enter choice: ").strip()
        if choice == '1':
            button_1_flow()
        elif choice == '2':
            button_2_flow()
        elif choice.lower() == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
    

