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
    print("  [q] Quit")
    print("  [4] Unassigned")
    print("\nInput:")
    if has_gpio:
        print("  • Hardware Keypad (GPIO buttons)")
        print("  • Keyboard (type + Enter)")
    else:
        print("  • Keyboard Only (type + Enter)")
    print("\n" + "-" * 60)
    print("Ready for input...")
    print("-" * 60 + "\n")
