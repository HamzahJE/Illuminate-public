# Illuminate - AI Vision Assistant

AI-powered vision assistant for visually impaired users. Uses camera, OpenAI Vision, and voice interaction with GPIO buttons or keyboard.

**Senior Design Project - April 2026**

---

## ⚡ Quick Start

### 1. Clone & Install
```bash
git clone <repository-url>
cd Illuminate
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy the example and fill in your Azure OpenAI credentials:
```bash
cp .env.example .env
# Edit .env with your values:
#   OPENAI_API_KEY=your_key
#   API_VERSION=your_api_version
#   OPENAI_API_BASE=your_endpoint
#   OPENAI_ORGANIZATION=your_org_id
#   MODEL=your_model_name
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

**What test mode does:**
- ✅ Skips all Azure OpenAI API calls (no costs)
- ✅ Returns mock vision descriptions and chat responses
- ✅ TTS still speaks (so you can test audio hardware)
- ✅ Camera still captures (so you can test the camera)
- ✅ Microphone still listens (so you can test the mic)

**What test mode does NOT skip:**
- Audio output (Piper/pyttsx3/espeak)
- Camera capture
- Microphone input
- GPIO/keyboard input

---

## 🎮 Available Commands

Once running, use these commands:
- **[1]** - Capture photo and get AI description
- **[2]** - Voice assistant (ask a question)
- **[q]** - Quit program
- **[3]** - Unassigned (available for custom features)

### Voice Assistant UX (Button 2)
The system uses **spoken cues** so the user always knows what's happening:
1. 🔊 **"Listening."** — tells the user to start speaking
2. 🔔 **Tone** — confirms microphone is active
3. *(user speaks, silence auto-detects end of speech)*
4. 🔔 **Tone** — confirms recording stopped
5. 🔊 **"Processing."** — tells the user to wait
6. 🔊 **AI response** — the answer is spoken aloud

If no speech is detected: **"I didn't catch that."**

---

## Features
- 📸 Camera capture with AI-powered descriptions
- 🎤 Voice assistant for questions and responses  
- 🧪 Test mode for development without API costs
- 🔊 **High-quality TTS**: Piper (Pi), pyttsx3 (macOS/Windows), espeak fallback
- ⌨️ Triple input: GPIO keypad, IR remote, or keyboard
- 🤖 Modular, easy-to-read code structure
- 🔄 Works on: Raspberry Pi, Mac, Windows, Linux
- 🎯 Intelligent audio device detection for USB headsets
- 🔔 Audio cues for listening state (user always knows when to speak)

---

## 🔀 System Flow

### Overall Architecture
```
┌───────────────────────────────────────────────────────────┐
│                        main.py                            │
│                                                           │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────┐  │
│  │ GPIO Keypad  │  │ 433MHz Remote │  │ Keyboard Input │  │
│  │ (Pi only)    │  │  (RX480E-4)   │  │                │  │
│  └──────┬───────┘  └──────┬────────┘  └───────┬────────┘  │
│         │                 │                   │           │
│         └────────────┬────┴───────────────────┘           │
│                      ▼                                    │
│               ┌──────────────┐                            │
│               │ Input Queue  │                            │
│               └──────┬───────┘                            │
│                      ▼                                    │
│               ┌──────────────┐                            │
│               │   Command    │                            │
│               │   Router     │                            │
│               └──┬────┬───┬──┘                            │
│                  │    │   │                               │
│                  ▼    ▼   ▼                               │
│           Button 1  Button 2  Button Q                    │
│           (Camera)  (Voice)   (Quit)                      │
└───────────────────────────────────────────────────────────┘
```

### Button 1 — Camera + AI Description
```
Press [1]
   │
   ▼
📸 Camera captures image (cam.py)
   │  └─ 30-frame warmup for Pi auto-exposure
   ▼
🤖 Image sent to OpenAI Vision (openai_vision.py)
   │  └─ Test mode: returns mock description
   ▼
🔊 AI description spoken aloud (tts.py)
   └─ Pi: Piper TTS ──▶ USB headset
      Mac/Win: pyttsx3 ──▶ system speakers
```

### Button 2 — Voice Assistant
```
Press [2]
   │
   ▼
🔊 "Listening." spoken (tts.py)     ◀── User knows to start talking
   │
   ▼
🎤 Microphone activated (stt_mic.py)
   │  ├─ 🔔 Start tone plays
   │  ├─ Ambient noise calibration
   │  └─ Records until silence detected
   │
   ▼
🔔 End tone plays                    ◀── User knows recording stopped
   │
   ▼
🔊 "Processing." spoken (tts.py)     ◀── User knows to wait
   │
   ▼
🤖 Question sent to OpenAI (chat.py)
   │  └─ Test mode: returns mock response
   ▼
🔊 AI response spoken aloud (tts.py)
   └─ Pi: Piper TTS ──▶ USB headset
      Mac/Win: pyttsx3 ──▶ system speakers
```

### TTS Engine Selection (automatic)
```
speak_text() called
   │
   ├─ Linux/Pi ─────┬─ Piper found? ──▶ 🔊 Piper TTS (high quality)
   │                 │                      │
   │                 │                      └─▶ text ──▶ [piper] ──pipe──▶ [aplay] ──▶ USB headset
   │                 │
   │                 └─ No Piper ──────▶ 🔊 espeak (fallback)
   │
   └─ macOS/Windows ───────────────────▶ 🔊 pyttsx3 (native voices)
```

---

## 🔊 Text-to-Speech System

Illuminate features an intelligent, cross-platform TTS system that automatically selects the best available engine:

### Raspberry Pi / Linux
**Primary:** Piper TTS (high-quality neural voices)
- Industry-standard voice synthesis
- Automatic USB audio device detection
- Near-zero latency streaming
- Requires: Piper binary + ONNX model file

**Fallback:** espeak (if Piper not configured)
- Lightweight, always works
- Lower quality but reliable

### macOS / Windows
**Native:** pyttsx3
- Uses system voices (macOS: Siri voices, Windows: SAPI5)
- No additional setup required

### How It Works
The system automatically:
1. Detects your operating system
2. On Linux: Attempts to use Piper (searches PATH and common locations) → Falls back to espeak if unavailable
3. On macOS/Windows: Uses native system voices
4. On Pi with USB headset: Auto-detects and routes audio correctly
5. All paths auto-detected - no configuration needed!

**Zero configuration** - Piper binary and models are auto-detected from standard locations.

---

## ⚡ Raspberry Pi - Zero Configuration

The project is **optimized for low latency** and works automatically on Pi:

- **Audio buffer**: 512μs (optimized for instant response)
- **Camera warmup**: 30 frames (auto-adjusts exposure on Pi)
- **Piper TTS**: Auto-detected from PATH or `~/.local/bin/piper`
- **Models**: Auto-detected from `~/.local/share/piper` or project `models/` folder
- **USB audio**: Automatically prioritized over built-in audio

**Just install and run** - no manual configuration required!

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

# Piper TTS (optional - for high-quality audio, auto-detected)
pip install piper-tts
# Download a voice model (lightweight, runs in background):
python3 -m piper_tts download en_US-amy-medium
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

## 🔧 GPIO & Hardware Setup

### GPIO Keypad Wiring

| RX480E Output | GPIO Pin | Command | Function |
|---------------|----------|---------|----------|
| D0 (Button A) | GPIO 23  | `1`     | Camera + AI Description |
| D1 (Button B) | GPIO 22  | `2`     | Voice Assistant |
| D2 (Button C) | GPIO 27  | `3`     | Unassigned |
| D3 (Button D) | GPIO 17  | `q`     | Quit Program (temporary) |

**Wiring:**
- RX480E-4A `D0-D3` outputs → Raspberry Pi GPIO pins shown above
- RX480E-4A `VCC` → Pi 3.3V, RX480E-4A `GND` → Pi GND
- Input is configured as **active-high** (`pull_up=False` in `gpiozero`)
- Remote press = GPIO HIGH pulse from receiver output

> Note: GPIO17 is currently used for `D3 -> q`. If you also enable the TL-1838 IR receiver on GPIO17, the two inputs will conflict.

### Hardware Needed
- Raspberry Pi (any GPIO model)
- USB microphone
- Pi Camera or USB webcam
- QIACHIP RX480E-4A receiver + paired RF remote
- Headphones/speaker for audio

### Customizing GPIO Pins

To change which GPIO pins are used for your buttons:

1. Open `modules/hardware.py`
2. Find the `PIN_TO_KEY` dictionary (around line 30)
3. Update the pin numbers:

```python
PIN_TO_KEY = {
   23: '1',  # D0 / Button A
   22: '2',  # D1 / Button B
   27: '3',  # D2 / Button C (Unassigned)
   17: 'q',  # D3 / Button D (Quit, temporary)
}
```

**Example:** To use GPIO 17 instead of GPIO 23 for Button 1:
```python
PIN_TO_KEY = {
   17: '1',
   22: '2',
   27: '3',
   23: 'q',
}
```

Save the file and restart the program. No other changes needed!

### 📡 IR Remote Control (TL-1838)

Illuminate supports an **infrared remote control** via a TL-1838 IR receiver, giving you a wireless way to trigger commands alongside the GPIO buttons and keyboard.

#### Hardware Wiring

| TL-1838 Pin | Connect To |
|-------------|------------|
| Signal (S)  | GPIO 17    |
| VCC (+)     | 3.3V       |
| GND (-)     | GND        |

#### Software Setup

```bash
# 1. Install ir-keytable
sudo apt install -y ir-keytable

# 2. Load the gpio-ir device tree overlay (one-time)
#    Add this line to /boot/config.txt (or /boot/firmware/config.txt on newer OS):
#    dtoverlay=gpio-ir,gpio_pin=17
sudo nano /boot/config.txt
# Add:  dtoverlay=gpio-ir,gpio_pin=17
# Save and reboot:
sudo reboot

# 3. Verify the receiver is detected
sudo ir-keytable
# You should see a /dev/input/eventX device listed

# 4. Test that button presses are received
sudo ir-keytable --test
# Press buttons on your remote — you should see scancode output
```

#### Default Remote Button Mapping

| Remote Button | Scancode | Function |
|---------------|----------|----------|
| Button → 1    | `0x0c`   | Camera + AI Description |
| Button → 2    | `0x18`   | Voice Assistant |

#### Finding Your Remote's Scancodes

Different remotes send different scancodes. To find yours:

```bash
sudo ir-keytable --test
# Press a button and note the scancode, e.g.:
#   ... scancode = 0x0c
```

#### Customizing IR Button Mapping

To change which remote buttons map to which commands:

1. Open `modules/ir_remote.py`
2. Edit the `IR_SCANCODE_MAP` dictionary:

```python
IR_SCANCODE_MAP = {
    "0x0c": "1",  # Camera + AI Description
    "0x18": "2",  # Voice Assistant
    "0x1e": "q",  # Quit (add your own!)
}
```

3. Save and restart the program.

#### Troubleshooting IR Remote

```bash
# Check that gpio-ir overlay is loaded
dtoverlay -l

# Check for the IR input device
ls /dev/input/event*

# Make sure ir-keytable can see the device
sudo ir-keytable

# If no device found, verify /boot/config.txt has:
#   dtoverlay=gpio-ir,gpio_pin=17
# then reboot

# Test raw input
sudo ir-keytable --test
# If you see scancodes when pressing buttons, the hardware is working
```

> **Note:** `ir-keytable --test` may require `sudo`. The program runs it automatically — if IR isn't working, try running Illuminate with `sudo python3 main.py`.

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

### gpiozero "Failed to add edge detection" on Pi
If you see this error while initializing GPIO buttons, install the `rpi-lgpio` build prerequisites first:

```bash
sudo apt update
sudo apt install swig python3-dev liblgpio-dev liblgpio1 -y
```

Then install/upgrade GPIO Python packages:

```bash
pip install -U gpiozero rpi-lgpio
```

After installing, reboot the Pi and run the app again.

### No Audio Output (espeak/Piper)
TTS not making sound?

```bash
# Test audio devices
aplay -l  # List all audio devices

# Test espeak fallback
espeak "test"

# Set default output (if needed)
sudo raspi-config  # → Audio → Force headphone jack

# Piper troubleshooting:
# - System auto-detects Piper binary and models
# - Check if installed: which piper
# - Verify model downloaded: ls ~/.local/share/piper/
# - Falls back to espeak automatically if Piper unavailable
```

### Microphone Not Working
```bash
# List microphones
python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

### Camera Not Working
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

**System (Linux/Pi):**
- espeak, portaudio19-dev, python3-dev
- Piper TTS (optional, for high-quality audio)
- ir-keytable (optional, for IR remote control)

**Python (installed via requirements.txt):**
- openai (Azure OpenAI SDK)
- python-dotenv
- opencv-python
- SpeechRecognition, pyaudio
- pyttsx3 (macOS/Windows TTS)
- RPi.GPIO (Raspberry Pi only — install manually)

**Hardware (Pi deployment):**
- USB microphone
- Pi Camera Module or USB webcam
- USB headphones/speaker
- QIACHIP RX480E-4A receiver + RF remote (GPIO input)
- TL-1838 IR receiver + IR remote (optional wireless control)

---

## 📝 Code Structure

```
Illuminate/
├── main.py                  # Entry point, command routing, event loop
├── .env                     # API keys (never committed)
├── .env.example             # Template for .env setup
├── requirements.txt         # Python dependencies
├── images/                  # Captured images (auto-managed)
├── models/                  # Piper voice models (Pi only)
└── modules/
    ├── cam.py               # Camera capture (OpenCV)
    ├── chat.py              # Azure OpenAI chat (Q&A)
    ├── openai_vision.py     # Azure OpenAI Vision (image description)
    ├── stt_mic.py           # Speech-to-text via microphone
    ├── tts.py               # Cross-platform TTS router (Piper/pyttsx3/espeak)
    ├── piper_tts.py         # Piper TTS engine - Pi audio streaming
    ├── tones.py             # Audio feedback tones (listening start/stop)
    ├── hardware.py          # GPIO keypad input (with mock for non-Pi)
    ├── ir_remote.py         # IR remote control via TL-1838 + ir-keytable
    ├── keyboard_input.py    # Keyboard input handler
    ├── ui.py                # Terminal UI (banner, prompts)
    └── test_mode.py         # Mock responses for --test mode
```

---

## 🔒 Security Best Practices

- ✅ `.env` is in `.gitignore` - never commit it
- ✅ `.copilotignore` and `.aidigestignore` block AI agents from accessing secrets
- ✅ Store API keys securely in `.env` file only
- ✅ Rotate API keys regularly
- ✅ Use least-privilege access for API credentials
- ⚠️ **Never share your `.env` file or commit it to version control**

**AI Protection**: This project includes `.copilotignore` and `.aidigestignore` to prevent
AI assistants from reading sensitive files containing API keys.

**Senior Design Project - April 2026**

For issues: Check troubleshooting section, verify `.env` and dependencies.
