import os
import chainlit as cl
from dotenv import load_dotenv
from langfuse.openai import AsyncOpenAI
from langfuse import Langfuse, observe, propagate_attributes
from chainlit.input_widget import Select, Switch, Slider
from chainlit.types import ThreadDict

from prisma import Prisma

# temp imports
import json

load_dotenv()

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

    # Getting system prompt from langfuse --> extract compiled prompt and config
    init_prompt = langfuse.get_prompt("work assistance")
    init_config = init_prompt.config
    user = cl.user_session.get("user")
    compiled_init_prompt = init_prompt.compile(display_name=user.display_name)

    # Initialize system prompt
    cl.user_session.set("message_history", compiled_init_prompt)

    # Initialize user settings
    cl.user_session.set("user_settings", init_config)


@cl.on_chat_resume
async def resume_conversation(thread: ThreadDict):
    # Initialize user settings
    cl.user_session.set("user_settings", thread["metadata"]["chat_settings"])
    cl.user_session.set("message_history", thread["metadata"]["message_history"])


async def get_user_id():
    prisma_client = Prisma()
    await prisma_client.connect()
    # prisma_client.


@observe
@cl.on_message
async def stream_message(message: cl.Message):
    user_settings = cl.user_session.get("user_settings")
    message_history = cl.user_session.get("message_history")
    chat_profile = cl.user_session.get("chat_profile")

    message_history.append({"role": "user", "content": message.content})

    with propagate_attributes(
        user_id=cl.user_session.get("user").id, session_id=cl.user_session.get("id")
    ):
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
            display_name="Jamal",
        )
    else:
        return None


@cl.action_callback(name="explain_more_button")
async def on_action(action: cl.Action):
    await stream_message(cl.Message(content=action.payload))


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Work assistance help",
            message="I need help organizing my work tasks and priorities for this week. Can you help me create a structured plan?",
            # icon="/public/work.svg",
        ),
        cl.Starter(
            label="Code review request",
            message="Please review my code for bugs, security issues, and best practices. I want to ensure it's production-ready.",
            # icon="/public/code.svg",
            command="code",
        ),
        cl.Starter(
            label="Creative story writing",
            message="Help me write an engaging short story about a character who discovers something unexpected in their daily routine.",
            # icon="/public/write.svg",
        ),
        cl.Starter(
            label="Data analysis insights",
            message="I have some data patterns I'd like you to analyze. Can you help me identify trends and provide actionable insights?",
            # icon="/public/chart.svg",
        ),
        cl.Starter(
            label="Language learning session",
            message="I want to practice conversational skills in a new language. Can you be my tutor and help me with basic phrases?",
            # icon="/public/learn.svg",
        ),
        cl.Starter(
            label="Technical documentation",
            message="Help me create clear technical documentation for my project. I need it to be easy to understand for new developers.",
            # icon="/public/docs.svg",
        ),
        cl.Starter(
            label="Brainstorm creative ideas",
            message="I need fresh, creative ideas for improving user engagement in my app. Let's brainstorm some innovative features.",
            # icon="/public/idea.svg",
        ),
        cl.Starter(
            label="Debug code issues",
            message="I'm having trouble with a bug in my code. Can you help me identify what's wrong and how to fix it?",
            # icon="/public/terminal.svg",
            command="code",
        ),
        cl.Starter(
            label="Meeting summary",
            message="Can you help me create a concise summary of our team meeting with clear action items and next steps?",
            # icon="/public/meeting.svg",
        ),
        cl.Starter(
            label="Product strategy guidance",
            message="I need strategic advice on my product roadmap. Help me prioritize features and understand market positioning.",
            # icon="/public/strategy.svg",
        ),
    ]


# To test or debug your application files and decorated functions, you will need to provide the Chainlit context to your test suite.
# run the script from your IDE in debug mode.
if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
