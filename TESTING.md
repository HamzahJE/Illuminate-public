# Testing & Deployment Guide

## Updated Files

**Main system files updated:**
- ✅ `main.py` - GPIO keypad + keyboard support, threading, error handling
- ✅ `modules/tts.py` - Thread-safe TTS with weak reference error fix

**Other modules remain unchanged** - they work fine with the updated main and TTS

## Running the Full System

### On Your Laptop (Test Mode - Keyboard Only)
```bash
python3 main.py
```
- GPIO disabled automatically
- Keyboard input only
- Type 1, 2, q, or 4 and press Enter

### On Raspberry Pi (Full Mode - Keypad + Keyboard)
```bash
python3 main.py
```
- GPIO keypad enabled
- Both physical keypad and keyboard work
- Press buttons or type commands

## Key Mappings

| Input | Function |
|-------|----------|
| 1 | Capture image → Describe → Speak |
| 2 | Listen to mic → Query OpenAI → Speak response |
| q | Quit program |
| 4 | Currently unassigned |

## GPIO Connections (Raspberry Pi)

```
Keypad 1x4 Configuration:
- GPIO23 → Key 1 (Image capture)
- GPIO24 → Key 2 (Voice assistant)
- GPIO25 → Key Q (Quit)
- GPIO8  → Key 4 (Unassigned)

Wiring: Connect each button between GPIO pin and Ground
        Internal pull-up resistors are enabled
        Button press = GPIO LOW
```

## Deployment to Raspberry Pi

**Copy only the updated files to Pi:**
```bash
scp main.py admin@raspberrypi:/home/admin/Desktop/Illuminate/
scp modules/tts.py admin@raspberrypi:/home/admin/Desktop/Illuminate/modules/
```

Or copy the entire project:
```bash
scp -r Illuminate/ admin@raspberrypi:/home/admin/Desktop/
```

**Install dependencies on Pi (if not already installed):**
```bash
pip3 install openai opencv-python python-dotenv pyttsx3 speech_recognition
```

**Run:**
```bash
cd /home/admin/Desktop/Illuminate
python3 main.py
```

## Key Improvements

### main.py
✅ Dual input support (GPIO keypad + keyboard)
✅ Graceful GPIO mock for laptop testing
✅ Error handling in all flows
✅ Multi-threaded for non-blocking input
✅ Clean shutdown with proper GPIO cleanup

### modules/tts.py
✅ Thread-safe with locks
✅ Lazy initialization
✅ Error recovery with automatic re-init
✅ **Fixes "ReferenceError: weakly-referenced object no longer exists" on Raspberry Pi**
✅ Prevents resource leaks from multiple engine instances
