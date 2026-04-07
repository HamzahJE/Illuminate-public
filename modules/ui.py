"""
User Interface Module
Handles terminal output and user prompts
"""


def print_banner(has_gpio):
    """Display welcome banner and instructions."""
    print("=" * 60)
    print("  ILLUMINATE - AI Vision Assistant")
    print("=" * 60)
    print("\nCommands:")
    print("  [1] Camera + AI Description")
    print("  [2] Voice Assistant")
    print("  [3] Image Follow-Up Q&A")
    print("  [4] OCR (Read Text - Tesseract)")
    print("  [5] OCR (Read Text - EasyOCR)")
    print("  [q] Quit (keyboard only)")
    print("\nGPIO Button Mapping:")
    print("  [A / D0 / GPIO23] -> [1] Camera")
    print("  [B / D1 / GPIO22] -> [2] Voice")
    print("  [C / D2 / GPIO27] -> [3] Image Q&A")
    print("  [D / D3 / GPIO17] -> [4] OCR")
    print("\nInput:")
    if has_gpio:
        print("  • Hardware Keypad (GPIO buttons)")
    print("  • Keyboard (type + Enter)")
    print("\n" + "-" * 60)
    print("Ready for input...")
    print("-" * 60 + "\n")
