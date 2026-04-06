"""
User Interface Module
Handles terminal output and user prompts
"""


def print_banner(has_gpio, has_ir=False):
    """Display welcome banner and instructions."""
    print("=" * 60)
    print("  ILLUMINATE - AI Vision Assistant")
    print("=" * 60)
    print("\nCommands:")
    print("  [1] Camera + AI Description")
    print("  [2] Voice Assistant")
    print("  [q] Quit")
    print("  [4] Unassigned")
    print("\nGPIO Button Mapping:")
    print("  [A / D0 / GPIO23] -> [1]")
    print("  [B / D1 / GPIO22] -> [2]")
    print("  [C / D2 / GPIO27] -> (not defined yet)")
    print("  [D / D3 / GPIO17] -> [q] (temporary)")
    print("\nInput:")
    if has_gpio:
        print("  • Hardware Keypad (GPIO buttons)")
    if has_ir:
        print("  • IR Remote (TL-1838 on GPIO-17)")
    print("  • Keyboard (type + Enter)")
    print("\n" + "-" * 60)
    print("Ready for input...")
    print("-" * 60 + "\n")
