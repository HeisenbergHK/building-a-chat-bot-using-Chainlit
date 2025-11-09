import os
import chainlit as cl
from dotenv import load_dotenv
from langfuse.openai import AsyncOpenAI
from langfuse import Langfuse
from chainlit.input_widget import Select, Switch, Slider
from chainlit.types import ThreadDict

# temp imports
import json

load_dotenv()

# Debug Langfuse config
print(f"LANGFUSE_HOST: {os.environ.get('LANGFUSE_HOST')}")
print(f"LANGFUSE_PUBLIC_KEY: {os.environ.get('LANGFUSE_PUBLIC_KEY')}")
print(f"LANGFUSE_SECRET_KEY exists: {bool(os.environ.get('LANGFUSE_SECRET_KEY'))}")

# Initialize Langfuse
langfuse = Langfuse()

API_KEY = os.environ["HF_TOKEN"]
API_URL = os.environ["API_URL"]
MODEL_NUM1 = os.environ["MODEL_NUM1"]
MODEL_NUM2 = os.environ["MODEL_NUM2"]

# ------- openai ---------
cl.instrument_openai
client = AsyncOpenAI(base_url=API_URL, api_key=API_KEY)


@cl.on_chat_start
async def init_chat():
    setting = await cl.ChatSettings(
        [
            Slider(
                id="temperature",
                label="Temperature",
                min=0,
                max=1,
                step=0.1,
                initial=0.5,
            ),
            Slider(id="top_p", label="Top P", min=0.1, max=1, step=0.1, initial=1.0),
            Slider(
                id="frequency_penalty",
                label="Frequency Penalty",
                min=-2,
                max=2,
                step=0.1,
                initial=0.0,
            ),
            Slider(
                id="presence_penalty",
                label="Presence Penalty",
                min=-2,
                max=2,
                step=0.1,
                initial=0.0,
            ),
        ]
    ).send()

    # Initialize user settings
    cl.user_session.set(
        "user_settings",
        {
            "temperature": 0.5,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        },
    )

    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": f"You are a helpful assistant. Keep answers concise.",
            },
        ],
    )


@cl.on_chat_resume
async def resume_conversation(thread: ThreadDict):
    # Initialize user settings
    cl.user_session.set("user_settings", thread["metadata"]["chat_settings"])
    cl.user_session.set("message_history", thread["metadata"]["message_history"])


@cl.on_message
async def stream_message(message: cl.Message):
    user_settings = cl.user_session.get("user_settings")
    message_history = cl.user_session.get("message_history")
    chat_profile = cl.user_session.get("chat_profile")

    message_history.append({"role": "user", "content": message.content})

    stream = await client.chat.completions.create(
        model=chat_profile,
        stream=True,
        messages=message_history,
        temperature=user_settings["temperature"],
        top_p=user_settings["top_p"],
        frequency_penalty=user_settings["frequency_penalty"],
        presence_penalty=user_settings["presence_penalty"],
    )

    # Custom action
    actions = [
        cl.Action(
            label="Explain more",
            name="explain_more_button",
            icon="chart-no-axes-gantt",
            payload={"role": "system", "message": "Explain more!"},
        )
    ]

    response = cl.Message(content="", actions=actions)

    async with stream:

        async for chunk in stream:
            try:
                if token := chunk.choices[0].delta.content or "":
                    await response.stream_token(token)
            except (IndexError, AttributeError):
                continue  # Handle malformed chunks

        message_history.append({"role": "assistant", "content": response.content})
        await response.update()

    cl.user_session.set("message_history", message_history)


@cl.on_settings_update
async def get_setting(settings):
    # Override user settings
    cl.user_session.set("user_settings", settings)

    # Send a message to confirm settings were updated
    await cl.Message(
        content=f"Settings updated: Temperature={settings.get('temperature', 0.5)}, "
        f"Top P={settings.get('top_p', 1.0)}, "
        f"Frequency Penalty={settings.get('frequency_penalty', 0.0)}, "
        f"Presence Penalty={settings.get('presence_penalty', 0.0)}"
    ).send()


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
    ]


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin",
            metadata={"role": "admin", "provider": "credentials"},
        )
    else:
        return None


@cl.action_callback(name="explain_more_button")
async def on_action(action: cl.Action):
    await stream_message(cl.Message(content=action.payload))


# To test or debug your application files and decorated functions, you will need to provide the Chainlit context to your test suite.
# run the script from your IDE in debug mode.
if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
