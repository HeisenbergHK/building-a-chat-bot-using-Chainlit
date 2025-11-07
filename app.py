import os

import chainlit as cl
from dotenv import load_dotenv

from openai_client import OpenAIClient

load_dotenv()

API_KEY = os.environ["HF_TOKEN"]
API_URL = os.environ["API_URL"]
MODEL_NUM1 = os.environ["MODEL_NUM1"]
MODEL_NUM2 = os.environ["MODEL_NUM2"]
MODEL_NUM3 = os.environ["MODEL_NUM3"]
MAX_HISTORY = 10


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == (
        "admin",
        "admin",
    ):  # TODO This is a fake authentication system!
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_chat_start
async def start_chat():

    current_user = cl.user_session.get("user")
    display_name = current_user.display_name

    if not display_name:
        response = await cl.AskUserMessage(
            content="What should I call you?", timeout=180, raise_on_timeout=True
        ).send()

        current_user.display_name = response["output"]
        # current_user.display_name = response.output

        cl.user_session.set("user", current_user)

    chat_profile = cl.user_session.get("chat_profile")

    client = OpenAIClient(API_KEY=API_KEY, API_URL=API_URL, model=chat_profile)
    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": f"You are a helpful assistant. The user's name is {current_user.display_name}. Keep answers concise.",
            },
        ],
    )
    cl.user_session.set("openai_client", client)
    cl.user_session.set("message_counter", 1)

    await main(cl.Message(content=f"My name is {current_user.display_name}"))


@cl.on_message  # This will call every time the user input a message in hte UI
async def main(message: cl.Message):
    actions = [
        cl.Action(
            label="Explain more",
            name="explain_more_button",
            icon="chart-no-axes-gantt",
            payload={"role": "user", "message": "Explain more!"},
        )
    ]

    openai_client = cl.user_session.get("openai_client")
    message_history = cl.user_session.get("message_history")
    message_counter = cl.user_session.get("message_counter")

    message_history.append({"role": "user", "content": message.content})
    message_counter += 1

    response = cl.Message(content="", actions=actions)

    # Sends the empty message to the frontend — the user now sees a “thinking” message bubble.
    await response.send()

    await openai_client.stream_update_response(message_history, response)

    message_counter += 1

    cl.user_session.set("message_history", message_history)
    cl.user_session.set("message_counter", message_counter)


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Do you want to know me?",
            message="Introduce yourself.",
            icon="/public/icon/bulb.svg",
        ),
        cl.Starter(
            label="Want to create a daily routine?",
            message="Create a daily routine for me.",
            icon="/public/icon/list.svg",
        ),
    ]


@cl.action_callback(name="explain_more_button")
async def on_action(action: cl.Action):
    message = cl.Message(content=action.payload)
    await main(message)


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name=f"{MODEL_NUM1}",
            markdown_description=f"The underlying LLM model is **{MODEL_NUM1}**",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name=f"{MODEL_NUM2}",
            markdown_description=f"The underlying LLM model is **{MODEL_NUM2}**",
            icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name=f"{MODEL_NUM3}",
            markdown_description=f"The underlying LLM model is **{MODEL_NUM3}**",
            icon="https://picsum.photos/300",
        ),
    ]
