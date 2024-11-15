from openai import OpenAI
import os

api_key_openai = os.getenv("OPENAI_API_KEY")

def verify_sensitivity(article1, article2):
    """
    Takes two articles and verifies the sensitivity of the association based on openAI's moderation model omni.

    Parameters:
        article1: Name of the first article
        article2: Name of the second article

    Returns:
        response: The raw response of the omni model to the prompt associating articles 1 and 2.
    """

    client = OpenAI(api_key=api_key_openai)

    prompt = str(article1) + ' is associated with ' + str(article2)

    response = client.moderations.create(
        model="omni-moderation-latest",
        input=prompt
    )

    return response
