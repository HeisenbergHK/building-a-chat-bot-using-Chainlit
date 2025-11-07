import os

import chainlit as cl
from dotenv import load_dotenv

from openai_client import OpenAIClient

load_dotenv()

API_KEY = os.environ["HF_TOKEN"]
API_URL = os.environ["API_URL"]
MODEL = os.environ["MODEL"]
MAX_HISTORY = 10


@cl.on_chat_start
def start_chat():
    client = OpenAIClient(API_KEY=API_KEY, API_URL=API_URL, model=MODEL)
    cl.user_session.set(
        "message_history", [{"role": "system", "content": "be so angry!"}]
    )
    cl.user_session.set("openai_client", client)


@cl.on_message  # THis will call every time the user input a message in hte UI
async def main(message: cl.Message):
    openai_client = cl.user_session.get("openai_client")
    message_history = cl.user_session.get("message_history")

    message_history.append({"role": "user", "content": message.content})

    response = cl.Message(content="")
    # Sends the empty message to the frontend — the user now sees a “thinking” message bubble.
    await response.send()

    await openai_client.stream_update_response(message_history, response)

    cl.user_session.set("message_history", message_history)
