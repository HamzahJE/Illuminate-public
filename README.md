# Illuminate - AI Vision Assistant

AI-powered vision assistant for visually impaired users. Uses camera, OpenAI Vision, and voice interaction with GPIO buttons or keyboard.

**Senior Design Project - May 2026**

---

## ⚡ Quick Start

### 1. Clone & Install
```bash
git clone <repository-url>
cd Illuminate
pip install -r requirements.txt
```

### 2. Configure API Key
Create `.env` file:
```bash
OPENAI_API_KEY=your_openai_key_here
```

### 3. Run the App

**Normal Mode** (with API calls):
```bash
python3 main.py
```

**Test Mode** (no API costs - recommended for testing):
```bash
python3 main.py --test
```

**Test mode** uses mock responses instead of real OpenAI API calls. Perfect for:
- Testing hardware/GPIO setup
- Developing without API costs
- Demo/presentation without internet

---

## 🎮 Available Commands

Once running, use these commands:
- **[1]** - Capture photo and get AI description
- **[2]** - Voice assistant (ask a question)
- **[q]** - Quit program
- **[4]** - Unassigned (available for custom features)

---

## Features
- 📸 Camera capture with AI-powered descriptions
- 🎤 Voice assistant for questions and responses  
- 🧪 Test mode for development without API costs
- 🔊 Cross-platform text-to-speech (espeak/pyttsx3)
- ⌨️ Dual input: GPIO keypad (Pi) or keyboard (any system)
- 🤖 Modular, easy-to-read code structure
- 🔄 Works on: Raspberry Pi, Mac, Windows, Linux

---

---

## 📦 Detailed Setup (Platform-Specific)

<details>
<summary><b>Raspberry Pi / Linux</b></summary>

```bash
# System packages
sudo apt update
sudo apt install -y git python3-venv python3-pip espeak portaudio19-dev python3-dev

# Virtual environment (recommended)
python3 -m venv ~/myenv
source ~/myenv/bin/activate

# Python packages
pip install -r requirements.txt
pip install RPi.GPIO  # For GPIO button support
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
# Install portaudio (requires Homebrew)
brew install portaudio

# Python packages
pip install -r requirements.txt
```
</details>

<details>
<summary><b>Windows</b></summary>

```bash
# Python packages only
pip install -r requirements.txt
```
</details>

---

## � Troubleshooting

### GPIO Keypad Wiring

| Button | GPIO Pin | Function |
|--------|----------|----------|
| Key 1  | GPIO 23  | Camera + AI Description |
| Key 2  | GPIO 24  | Voice Assistant |
| Key Q  | GPIO 25  | Quit Program |
| Key 4  | GPIO 8   | Unassigned |

**Wiring:**
- One side of button → GPIO pin
- Other side → Ground (GND)
- Pull-up resistors enabled in software
- Press = LOW signal (connects to ground)

### Hardware Needed
- Raspberry Pi (any GPIO model)
- USB microphone
- Pi Camera or USB webcam
- 4 push buttons + jumper wires
- Headphones/speaker for audio

### Customizing GPIO Pins

To change which GPIO pins are used for your buttons:

1. Open `modules/hardware.py`
2. Find the `PIN_TO_KEY` dictionary (around line 30)
3. Update the pin numbers:

```python
PIN_TO_KEY = {
    23: '1',  # GPIO23 → Button 1 (Camera)
    24: '2',  # GPIO24 → Button 2 (Voice)
    25: 'q',  # GPIO25 → Button Q (Quit)
    8:  '4',  # GPIO8  → Button 4 (Unassigned)
}
```

**Example:** To use GPIO 17 instead of GPIO 23 for Button 1:
```python
PIN_TO_KEY = {
    17: '1',  # Changed from 23 to 17
    24: '2',
    25: 'q',
    8:  '4',
}
```

Save the file and restart the program. No other changes needed!

---

## 🔧 Troubleshooting

### GPIO Not Working on Raspberry Pi
Shows "SOFTWARE-ONLY mode" even on Pi?

```bash
# Install GPIO library
pip install RPi.GPIO

# Verify
python3 -c "import RPi.GPIO; print('GPIO OK')"
```

### No Audio Output (espeak)
TTS not making sound?

```bash
# Test espeak directly
espeak "test"

# Check audio device
aplay -l

# Set default output (if needed)
sudo raspi-config  # → Audio → Force headphone jack
```

### Microphone Not Working
```bash
# List microphones
python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

---

## 🔌 GPIO Hardware Setup (Raspberry Pi)
```bash
# Check camera devices
ls -l /dev/video*

# Enable Pi Camera (if using camera module)
sudo raspi-config  # → Interface → Camera → Enable

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'Failed')"
```

### OpenAI API Errors
Check:
1. `.env` file exists with valid `OPENAI_API_KEY`
2. Internet connection working
3. API key not expired
4. Sufficient API quota

### ALSA Warnings (Harmless)
Ignore these - program still works fine. To suppress:
```bash
cat > ~/.asoundrc << EOF
pcm.!default { type pulse }
ctl.!default { type pulse }
EOF
```

---

## 📦 Dependencies

**System (Linux):**
- espeak, portaudio, python3-dev

**Python:**
- openai, opencv-python, SpeechRecognition, pyaudio, pyttsx3
- RPi.GPIO (Raspberry Pi only)

**Hardware:**
- Microphone, camera, GPIO buttons (Pi only)

---

## 📝 Code Structure

**main.py** (~90 lines)
- Imports modules
- Defines command handlers (what each button does)
- Coordinates GPIO + keyboard input
- Main event loop

**modules/hardware.py** - GPIO keypad with mock for testing
**modules/keyboard_input.py** - Keyboard input handler
**modules/tts.py** - Cross-platform text-to-speech
**modules/cam.py** - Camera capture
**modules/openai_vision.py** - AI image description
**modules/stt_mic.py** - Speech recognition
**modules/chat.py** - AI Q&A

Clean, modular design - easy to understand and extend!

---

## 🔒 Security Best Practices

- ✅ `.env` is in `.gitignore` - never commit it
- ✅ Store API keys securely
- ✅ Rotate API keys regularly
- ✅ Use least-privilege access for API credentials

**Senior Design Project - May 2026**

For issues: Check troubleshooting section, verify `.env` and dependencies.
