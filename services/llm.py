import os
import traceback
from typing import List, Dict, AsyncGenerator

import openai
from openai.error import OpenAIError

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read environment variables
openai_model = os.getenv('OPENAI_API_MODEL')
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE_URL')

print(f"openai_model: {openai_model} openai.api_key: {openai.api_key} openai.api_base: {openai.api_base}")


async def converse(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """
    Given a conversation history, generate an iterative response of strings from the OpenAI API.

    :param messages: a conversation history with the following format:
    `[ { "role": "user", "content": "Hello, how are you?" },
       { "role": "assistant", "content": "I am doing well, how can I help you today?" } ]`

    :return: a generator of delta string responses
    """
    try:
        async for chunk in await openai.ChatCompletion.acreate(
                model=openai_model,
                messages=messages,
                max_tokens=1600,
                stream=True
        ):
            content = chunk['choices'][0]['delta'].get('content', '')
            if content:
                yield content

    except OpenAIError as e:
        traceback.print_exc()
        yield f"EXCEPTION {str(e)}"
    except Exception as e:
        yield f"EXCEPTION {str(e)}"


def create_conversation_starter(user_prompt: str) -> List[Dict[str, str]]:
    """
    Given a user prompt, create a conversation history with the following format:
    `[ { "role": "user", "content": user_prompt } ]`

    :param user_prompt: a user prompt string
    :return: a conversation history
    """
    return [{"role": "user", "content": user_prompt}]
