from openai import OpenAI
import os

api_key_openai = os.getenv("OPENAI_API_KEY")

def verify_sensitivity(article1,article2):

    client = OpenAI(
        api_key=api_key_openai,
    )

    prompt = str(article1) + ' is associated with ' + str(article2)

    response = client.moderations.create(
        model="omni-moderation-latest",
        input=prompt,
    )
    return response
