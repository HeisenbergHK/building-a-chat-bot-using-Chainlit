import requests
import json
from openai import OpenAI
import chainlit as cl

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["HF_TOKEN"]

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_KEY,
)


def get_response(message: cl.message) -> str:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b:groq",
        messages=[{"role": "user", "content": message.content}],
    )

    response_text = completion.choices[0].message.content

    return response_text
