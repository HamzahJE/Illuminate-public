# Illuminate - AI Vision Assistant

Senior Design Project - Voice-controlled AI assistant with vision capabilities.

## Quick Setup

### Raspberry Pi / Linux
```bash
python3 setup.py
```

### macOS
```bash
python3 setup.py
```

### Windows
```batch
python setup.py
REM Or double-click setup.bat
```

The setup script automatically:
- ✓ Checks Python version (requires 3.8+)
- ✓ Installs system dependencies (espeak, audio libraries)
- ✓ Installs all Python packages
- ✓ Verifies installation
- ✓ Checks for .env configuration

## Manual Setup (if needed)

**1. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**2. System-specific requirements:**

**Linux/Raspberry Pi:**
```bash
sudo apt-get install espeak alsa-utils portaudio19-dev libespeak1 python3-dev
```

**macOS:**
```bash
brew install portaudio
```

**Windows:** No additional system packages needed.

**3. Configure environment:**

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```dotenv
OPENAI_API_KEY=your_api_key
API_VERSION=your_api_version
OPENAI_API_BASE=your_api_base
OPENAI_ORGANIZATION=your_organization_id
MODEL=your_model_name
IMAGE_PATH=images
```

## Running the Project

```bash
python3 main.py
```

## Features

- Voice control via microphone
- AI vision with camera capture
- Text-to-speech responses
- Physical keypad support (Raspberry Pi)
- Cross-platform compatibility

## Testing Individual Modules

```bash
python3 modules/tts.py          # Test text-to-speech
python3 modules/stt_mic.py      # Test speech recognition
python3 modules/cam.py          # Test camera capture
python3 modules/chat.py         # Test OpenAI chat
```

## Project Structure

```
Illuminate/
├── main.py                 # Main application
├── setup.py               # Cross-platform setup script
├── setup.bat              # Windows setup helper
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── modules/
    ├── tts.py            # Text-to-speech
    ├── stt_mic.py        # Speech-to-text
    ├── cam.py            # Camera capture
    ├── chat.py           # OpenAI chat
    └── openai_vision.py  # Vision AI
```

## Troubleshooting

**Import errors:**
```bash
pip install -r requirements.txt --force-reinstall
```

**No sound on Raspberry Pi:**
```bash
espeak "test"  # Test if espeak works
amixer cset numid=3 1  # Force 3.5mm jack
```

**Microphone not working:**
```bash
python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**Camera not detected:**
```bash
ls -l /dev/video*  # Check if camera device exists
```

## Requirements

- Python 3.8 or higher
- Microphone (for voice input)
- Camera (for vision features)
- Internet connection (for OpenAI API)
- Raspberry Pi GPIO pins (optional, for keypad)

## License

[Your License]
Wearable AI headgear providing real-time feedback for visually impaired users via audio/visual outputs and voice/button controls.

## Features
- 📸 Real-time image capture and AI-powered description
- 🎤 Voice interaction with OpenAI assistant
- 🔊 Text-to-speech audio feedback
- ⌨️ Dual input: GPIO keypad + keyboard (SSH compatible)
- 🤖 Accessible design for vision-impaired users

## Installation

### Dependencies
```bash
pip install openai opencv-python python-dotenv pyttsx3 speech_recognition RPi.GPIO
```

### Configuration
1. Copy `.env.example` to `.env`
2. Fill in your Azure OpenAI credentials:

```bash
OPENAI_API_KEY=your_api_key_here
API_VERSION=2024-02-15-preview
OPENAI_API_BASE=https://your-resource.openai.azure.com/
OPENAI_ORGANIZATION=your_org_id_here
MODEL=gpt-4o
IMAGE_PATH=images
```

**⚠️ Never commit your `.env` file to version control!**

## Hardware Setup (Raspberry Pi)

### GPIO Keypad Connections
```
1x4 Keypad Configuration:
- GPIO23 → Key 1 (Capture & Describe Image)
- GPIO24 → Key 2 (Voice Assistant)  
- GPIO25 → Key Q (Quit)
- GPIO8  → Key 4 (Unassigned)

Wiring: Connect each button between GPIO pin and Ground
        Internal pull-up resistors enabled
```

## Usage

### On Raspberry Pi (Full Mode)
```bash
python3 main.py
```
- Use physical keypad buttons or keyboard
- Both input methods work simultaneously

### On Laptop (Test Mode)
```bash
python3 main.py
```
- GPIO automatically disabled
- Keyboard-only mode

### Commands
- `1` - Capture image and get AI description
- `2` - Voice interaction (speak → AI response)
- `q` - Quit
- `4` - Unassigned (available for custom function)

## Project Structure
```
Illuminate/
├── main.py              # Main application with GPIO + keyboard input
├── modules/
│   ├── cam.py          # Camera capture
│   ├── openai_vision.py # Image description via OpenAI
│   ├── chat.py         # Chat with OpenAI assistant
│   ├── stt_mic.py      # Speech-to-text
│   └── tts.py          # Text-to-speech (thread-safe)
├── .env.example        # Environment template
└── README.md
```

## Security Notes
- `.env` is in `.gitignore` - never commit it
- Store API keys securely
- Rotate keys regularly
- Use least-privilege access for API keys
