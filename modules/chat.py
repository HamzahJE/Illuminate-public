from openai import AzureOpenAI
import os
from modules.test_mode import is_test_mode, get_mock_chat_response, get_mock_image_followup

# ============================================================================
# GENERAL CHAT (text-only, button 2)
# ============================================================================

messages=[
            {"role": "system","content": "You are a helpful assistant.keep the resonses concise and to the point and ready to be read out. less than 15 words. If you feel the question does not have enough information, politely ask for more details."}
        ]

def query_openai(prompt: str, default_answer="Sorry, I couldn't process your request.") -> str:

    # Return mock response in test mode
    if is_test_mode():
        print("[Test Mode] Returning mock chat response")
        return get_mock_chat_response(prompt)

    #Create Azure client
    client = AzureOpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
        api_version=os.environ['API_VERSION'],
        azure_endpoint = os.environ['OPENAI_API_BASE'],
        organization = os.environ['OPENAI_ORGANIZATION']
    )

    messages.append({"role": "user", "content": prompt})

    # Send a completion request.
    response = client.chat.completions.create(
            model=os.environ['MODEL'],
            messages=messages)

    #Print response.
    print(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content


# ============================================================================
# IMAGE CONVERSATION (with photo context, buttons 1 + 3)
# ============================================================================

IMAGE_SYSTEM_PROMPT = (
    "You are a helpful AI assistant for visually impaired users. "
    "You can describe images and answer follow-up questions about them. "
    "Keep responses concise, under 25 words, ready to be read aloud."
)

_image_messages = [{"role": "system", "content": IMAGE_SYSTEM_PROMPT}]
_has_image_context = False


def set_image_context(image_base64, description):
    """Reset image conversation and inject a new image + its description."""
    global _image_messages, _has_image_context
    _image_messages = [
        {"role": "system", "content": IMAGE_SYSTEM_PROMPT},
        {"role": "user", "content": [
            {"type": "text", "text": "I just took a photo. Describe what you see for a visually impaired person."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]},
        {"role": "assistant", "content": description},
    ]
    _has_image_context = True


def has_image_context():
    """Check if an image has been captured for follow-up questions."""
    return _has_image_context


def query_image_followup(prompt: str) -> str:
    """Ask a follow-up question about the captured image."""
    global _image_messages

    # Return mock response in test mode
    if is_test_mode():
        print("[Test Mode] Returning mock image follow-up response")
        return get_mock_image_followup(prompt)

    client = AzureOpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
        api_version=os.environ['API_VERSION'],
        azure_endpoint=os.environ['OPENAI_API_BASE'],
        organization=os.environ['OPENAI_ORGANIZATION']
    )

    _image_messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=os.environ['MODEL'],
        messages=_image_messages)

    reply = response.choices[0].message.content
    print(reply)
    _image_messages.append({"role": "assistant", "content": reply})
    return reply


# Example usage
if __name__ == "__main__":
    user_input = input("Enter your question: ")
    answer = query_openai(user_input)
    print(answer)