from openai import AzureOpenAI
import os
import base64
from modules.test_mode import is_test_mode, get_mock_image_description



def get_image_description():
    
    # Return mock response in test mode
    if is_test_mode():
        print("[Test Mode] Returning mock AI vision response")
        return get_mock_image_description()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Use hardcoded images folder
    image_path = os.path.join(project_root, 'images', 'image.jpg')

    # Path of the image to be analyzed
    imagedata = base64.b64encode(open(image_path, 'rb').read()).decode('ascii')

    #Create Azure client
    client = AzureOpenAI(
        api_key=os.environ['OPENAI_API_KEY'],  
        api_version=os.environ['API_VERSION'],
        azure_endpoint = os.environ['OPENAI_API_BASE'],
        organization = os.environ['OPENAI_ORGANIZATION']
    )
    #Create Query
    messages=[
            {"role": "system", "content": "As an AI tool specialized in image recognition, you will be given an image and asked to answer a question about it."},
            {"role": "user", "content": [
                {"type": "text", "text": "describe the image in detail. From an accessibility perspective, what are some important aspects of the image to note? For vision impaired users. keep the response concise and less than 25 words.I want reponse to be ready to read out to vision impared individuals."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{imagedata}"}}
            ]}
        ]

    response = client.chat.completions.create(
        model=os.environ['MODEL'],
        messages=messages,
        # temperature=0.0,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    image_path = os.environ.get('IMAGE_PATH')
    description = get_image_description(image_path)
    print(description)
