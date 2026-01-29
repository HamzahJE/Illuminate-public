# Illuminate - AI Vision Assistant

Wearable AI headgear providing real-time feedback for visually impaired users via audio/visual outputs and voice/button controls.

**Senior Design Project - May 2026**

## Features
- 📸 Real-time image capture with AI-powered descriptions
- 🎤 Voice interaction with OpenAI assistant
- 🔊 Natural text-to-speech audio feedback
- ⌨️ Dual input: Physical keypad + keyboard
- 🤖 Designed for accessibility and ease of use
- 🔄 Cross-platform: Raspberry Pi, Mac, Windows

---

## 🚀 Quick Start

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd Illuminate
```

### Step 2: Install Dependencies

**Raspberry Pi / Linux:**
```bash
# Update system and install Git
sudo apt update
sudo apt install -y git python3-venv python3-full python3-pip

# Create and activate virtual environment (recommended)
python3 -m venv myenv
source ~/myenv/bin/activate

# Install system packages for audio and speech
sudo apt install -y espeak espeak-ng libespeak1 portaudio19-dev \
    python3-dev libasound2-dev alsa-utils ffmpeg flac

# Install Python packages
pip install
pip install RPi.GPIO
```

**macOS:**
```bash
# Install Homebrew first (visit brew.sh)
# Install portaudio
brew install portaudio

# Install Python packages
pip install
```

**Windows:**
```bash
# Install Python packages
pip install
```

### Step 3: Configure API Keys

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your API credentials:
```dotenv
OPENAI_API_KEY=<your_api_key>
API_VERSION=<api_version>
OPENAI_API_BASE=<your_api_endpoint>
OPENAI_ORGANIZATION=<your_org_id>
MODEL=<model_name>
IMAGE_PATH=images
```

**⚠️ Important:** Never commit `.env` to version control!

### Step 4: Run the Program
```bash
python3 main.py
```

---

## 🎮 Using the Program

### On Raspberry Pi (Full Mode)
When running on a Raspberry Pi with GPIO pins connected:
```bash
python3 main.py
```
- Use physical keypad buttons **or** keyboard
- Both input methods work simultaneously
- SSH access supported for remote keyboard control

### On Mac/Windows (Test Mode)
When running on development machines:
```bash
python3 main.py
```
- GPIO automatically disabled
- Keyboard-only mode
- Uses native TTS (pyttsx3)

### Available Commands
- **`1`** - Capture image and get AI description (vision mode)
- **`2`** - Voice assistant (speak your question)
- **`q`** - Quit the program
- **`4`** - Unassigned (available for custom features)

---

## 🔌 Hardware Setup (Raspberry Pi)

### GPIO Keypad Wiring

Connect a 1x4 button keypad to these GPIO pins:

| Button | GPIO Pin | Function |
|--------|----------|----------|
| Key 1  | GPIO 23  | Capture & Describe Image |
| Key 2  | GPIO 24  | Voice Assistant |
| Key Q  | GPIO 25  | Quit Program |
| Key 4  | GPIO 8   | Unassigned |

**Wiring Instructions:**
1. Connect one side of each button to the GPIO pin
2. Connect the other side to **Ground (GND)**
3. Internal pull-up resistors are enabled in software
4. Buttons work on LOW signal (press = connect to ground)

### Required Hardware
- Raspberry Pi (any model with GPIO)
- USB microphone or Pi camera with mic
- Pi Camera Module or USB webcam
- 4 push buttons
- Jumper wires
- Optional: headphones/speaker for audio output

---

## 📁 Project Structure

```
Illuminate/
├── main.py                 # Main application loop
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .env                   # Your API keys (DO NOT COMMIT)
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── modules/
    ├── cam.py             # Camera capture module
    ├── openai_vision.py   # Image description via OpenAI Vision
    ├── chat.py            # Conversational AI with OpenAI
    ├── stt_mic.py         # Speech-to-text from microphone
    └── tts.py             # Text-to-speech (cross-platform)
```

---

## 🔧 Troubleshooting

### GPIO Not Detected (Raspberry Pi)
**Problem:** Shows "TEST MODE (no GPIO hardware)" even on Raspberry Pi

**Solution:**
```bash
# Activate your virtual environment first (if using one)
source ~/myenv/bin/activate

# Install RPi.GPIO
pip install RPi.GPIO

# Verify installation
python3 -c "import RPi.GPIO; print('GPIO installed successfully')"
```

### No Sound Output (Raspberry Pi)
**Problem:** TTS doesn't produce audio

**Solution:**
```bash
# Test espeak directly
espeak "Hello world"

# If no sound, check audio output device
amixer cset numid=3 1  # Set to 3.5mm jack
amixer cset numid=3 2  # Set to HDMI

# Check volume
alsamixer  # Use arrow keys to adjust, M to unmute
```

### TTS Voice Error (Raspberry Pi - pyttsx3)
**Problem:** `SetVoiceByName failed with unknown return code -1` or voice errors

**This occurs when using pyttsx3 on Raspberry Pi.** The library defaults to a non-existent voice.

**Solution:**
```bash
# Activate your virtual environment
source ~/myenv/bin/activate

# Edit the pyttsx3 driver file
vi ~/myenv/lib/python3.13/site-packages/pyttsx3/drivers/espeak.py

# Find the line with: _defaultVoice = "gmw/en"
# Change it to: _defaultVoice = "en-us"
# Save and exit

# Or use nano if preferred
nano ~/myenv/lib/python3.13/site-packages/pyttsx3/drivers/espeak.py
```

**Note:** The current TTS implementation uses subprocess with espeak directly, which avoids this issue. This is only needed if you modify the code to use pyttsx3 on Linux.

### Microphone Not Working
**Problem:** Speech recognition fails or doesn't detect mic

**Solution:**
```bash
# List available microphones
python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Test microphone with arecord
arecord -d 3 test.wav
aplay test.wav

# Adjust microphone levels
alsamixer
# Press F4 to select capture device
```

### Camera Not Detected
**Problem:** OpenCV can't access camera

**Solution:**
```bash
# Check if camera device exists
ls -l /dev/video*

# For Pi Camera Module, enable camera interface
sudo raspi-config
# Select: Interface Options → Camera → Enable

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera failed')"
```

### ALSA Warnings (Harmless)
**Problem:** Lots of ALSA error messages when using microphone

**These warnings are harmless** - the program still works. To suppress them:
```bash
# Create ALSA config file
cat > ~/.asoundrc << EOF
pcm.!default {
    type pulse
}
ctl.!default {
    type pulse
}
EOF
```

### Import Errors
**Problem:** `ModuleNotFoundError` when running

**Solution:**
```bash
# Reinstall all dependencies
pip install

# Or install missing package individually
pip install <package-name>
```

### OpenAI API Errors
**Problem:** API calls fail or return errors

**Check:**
1. Verify `.env` file exists and has correct credentials
2. Ensure API key is valid and not expired
3. Check internet connection
4. Verify model name matches your Azure deployment
5. Check API quota/usage limits

---

## 🛠️ Requirements

- **Python:** 3.8 or higher
- **Hardware (Pi):** Microphone, camera, GPIO pins
- **Hardware (Mac/Win):** Microphone, camera
- **Network:** Internet connection for OpenAI API
- **API:** Valid OpenAI (Azure) API credentials

---

## 🔒 Security Best Practices

- ✅ `.env` is in `.gitignore` - never commit it
- ✅ Store API keys securely
- ✅ Rotate API keys regularly
- ✅ Use least-privilege access for API credentials
- ✅ Don't share your `.env` file or paste keys publicly

---

## 📝 License

[Your License Here]

## 👥 Team

Senior Design Project - Graduating May 2026

---

## 🆘 Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review terminal error messages carefully
3. Verify all dependencies are installed
4. Ensure `.env` is configured correctly
5. Test individual modules separately
