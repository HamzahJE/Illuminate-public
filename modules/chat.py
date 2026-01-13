from openai import AzureOpenAI
import os
from dotenv import load_dotenv

  #Create Query
messages=[
            {"role": "system","content": "You are a helpful assistant.keep the resonses concise and to the point and ready to be read out. less than 15 words. If you feel the question does not have enough information, politely ask for more details."}
        ]
    
def query_openai(prompt: str, default_answer="Sorry, I couldn't process your request.") -> str:
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_path = os.path.join(project_root, '.env')
    if not load_dotenv(env_path):
        raise RuntimeError("Unable to load .env file.")

#Sets the current working directory to be the same as the file.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

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