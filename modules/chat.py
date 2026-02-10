from openai import AzureOpenAI
import os
from modules.test_mode import is_test_mode, get_mock_chat_response

  #Create Query
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

    completion_kwargs={"reasoning_effort": "low"}

    # Send a completion request.
    response = client.chat.completions.create(
            model=os.environ['MODEL'], ## Make sure you set a reasoning model in your .env file.  Example: o1, o3-mini, etc.
            # reasoning_effort="low",  ##Set your reasoning effort here.  Options are "low", "medium", "high".  Only works with reasoning models (o1, o3-mini, etc).
            ##Temperature, top_p, presence_penalty, frequency_penalty, logprobs, top_logprobs, logit_bias, max_tokensis are not supported with reasoning models.
            messages=messages)

    #Print response.
    print(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    user_input = input("Enter your question: ")
    answer = query_openai(user_input)
    print(answer)