"""
Test Mode Module
Provides mock responses for testing without hitting APIs
"""

import random

# Global flag controlled by command-line argument
_TEST_MODE = False


def set_test_mode(enabled):
    """Enable or disable test mode."""
    global _TEST_MODE
    _TEST_MODE = enabled


def is_test_mode():
    """Check if test mode is enabled."""
    return _TEST_MODE


def get_mock_image_description():
    """Return mock AI vision response."""
    descriptions = [
        "A wooden desk with a laptop and coffee mug. Well-lit room with natural light from a window.",
        "A smartphone on a white surface. The screen shows the time 3:45 PM.",
        "A bookshelf filled with colorful books. Three plants visible on the top shelf.",
        "A kitchen counter with a fruit bowl containing apples and bananas.",
    ]
    return random.choice(descriptions)


def get_mock_chat_response(user_text):
    """Return mock chat response based on user input."""
    responses = {
        "weather": "The weather today is sunny with a high of 72 degrees.",
        "time": "The current time is 3:45 PM.",
        "hello": "Hello! How can I help you today?",
        "help": "I can describe images, answer questions, and help with daily tasks.",
    }
    
    # Simple keyword matching
    text_lower = user_text.lower()
    for keyword, response in responses.items():
        if keyword in text_lower:
            return response
    
    return f"I heard you say: '{user_text}'. This is a test response - API calls are disabled in test mode."


def get_mock_image_followup(user_text):
    """Return mock image follow-up response based on user input."""
    responses = {
        "exit": "The exit sign is visible in the top-right corner, above the far door.",
        "color": "The dominant colors are brown and white, with natural lighting.",
        "read": "There is text on the laptop screen, but it's too small to read clearly.",
        "people": "No people are visible in the image.",
        "where": "Based on the image, you appear to be in an indoor room with furniture.",
    }

    text_lower = user_text.lower()
    for keyword, response in responses.items():
        if keyword in text_lower:
            return response

    return f"Based on the captured image, I can see details related to your question: '{user_text}'. This is a test response."


def get_mock_speech_text():
    """Return mock speech recognition result."""
    phrases = [
        "What time is it",
        "Tell me about the weather",
        "What do you see",
        "Hello there",
    ]
    return random.choice(phrases)


def print_test_mode_banner():
    """Display test mode indicator."""
    if is_test_mode():
        print("\n" + "!" * 60)
        print("  TEST MODE ENABLED - No API calls will be made")
        print("  Run without --test flag to use real APIs")
        print("!" * 60 + "\n")
