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

### Step 2: Run Setup

**Raspberry Pi / Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```batch
python setup.py
```

The setup script will:
- ✓ Check Python version (3.8+ required)
- ✓ Install system dependencies (espeak, audio libraries)
- ✓ Install all Python packages from `requirements.txt`
- ✓ Verify installation
- ✓ Remind you to configure `.env`

### Step 3: Configure API Keys

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```dotenv
OPENAI_API_KEY=your_api_key_here
API_VERSION=2024-02-15-preview
OPENAI_API_BASE=https://your-resource.openai.azure.com/
OPENAI_ORGANIZATION=your_organization_id
MODEL=gpt-4o
IMAGE_PATH=images
```

**⚠️ Important:** Never commit `.env` to version control!

### Step 4: Run the Program
```bash
python3 main.py
```

---

## 📋 Manual Setup (Alternative)

If automatic setup doesn't work, follow these steps:

### 1. Install System Dependencies

**Raspberry Pi / Ubuntu / Debian:**
```bash
sudo apt-get update
sudo apt-get install -y espeak alsa-utils portaudio19-dev libespeak1 python3-dev python3-pip
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install portaudio
brew install portaudio
```

**Windows:**
- No additional system packages required
- Ensure Python 3.8+ is installed from [python.org](https://python.org)

### 2. Install Python Packages
```bash
pip install -r requirements.txt
```

### 3. Install GPIO Support (Raspberry Pi Only)
```bash
pip install RPi.GPIO
```

### 4. Test Individual Components

**Test text-to-speech:**
```bash
python3 modules/tts.py
```

**Test speech recognition:**
```bash
python3 modules/stt_mic.py
```

**Test camera:**
```bash
python3 modules/cam.py
```

**Test OpenAI chat:**
```bash
python3 modules/chat.py
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
├── setup.sh                # Setup script for Linux/Mac
├── setup.py                # Setup script (cross-platform Python)
├── setup.bat               # Setup script for Windows
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .env                   # Your API keys (DO NOT COMMIT)
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── TESTING.md             # Testing documentation
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
pip install -r requirements.txt

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
