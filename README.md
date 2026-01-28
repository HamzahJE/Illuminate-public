# Illuminate
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
