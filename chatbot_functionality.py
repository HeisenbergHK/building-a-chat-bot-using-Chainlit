import requests
import json
from openai import OpenAI, AsyncOpenAI
import chainlit as cl

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["HF_TOKEN"]

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_KEY,
)

async_client = AsyncOpenAI(base_url="https://router.huggingface.co/v1", api_key=API_KEY)


def get_response(message: cl.message) -> str:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b:groq",
        messages=[{"role": "user", "content": message.content}],
    )

    response_text = completion.choices[0].message.content

    return response_text


async def update_response_async(messages, message: cl.Message):
    stream = await async_client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b:groq",
        stream=True,
        messages=messages,
    )

    async for i in stream:
        if token := i.choices[0].delta.content or "":
            await message.stream_token(token)
