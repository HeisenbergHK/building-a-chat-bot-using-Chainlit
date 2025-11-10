from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()

langfuse = Langfuse()

langfuse.create_prompt(
    name="work assistance",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a nice but professional work assistance that are concise. You work for {{display_name}}. ",
        },
    ],
    labels=["production"],
    config={
        "temperature": 0.4,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "supported_languages": ["en", "fr"],
    },
)

langfuse.create_prompt(
    name="code reviewer",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are an expert code reviewer. Analyze code for bugs, security issues, and best practices.",
        },
    ],
    labels=["production"],
    config={"temperature": 0.2, "top_p": 0.9},
)

langfuse.create_prompt(
    name="creative writer",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a creative writer who crafts engaging stories and content.",
        },
    ],
    labels=["production"],
    config={"temperature": 1, "top_p": 0.95},
)

langfuse.create_prompt(
    name="data analyst",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a data analyst who provides insights from data patterns and trends.",
        },
    ],
    labels=["production"],
    config={"temperature": 0.3, "top_p": 0.9},
)

langfuse.create_prompt(
    name="language tutor",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a patient language tutor who helps students learn {{language}}.",
        },
    ],
    labels=["production"],
    config={"temperature": 0.5, "supported_languages": ["en", "es", "fr", "de"]},
)

langfuse.create_prompt(
    name="technical writer",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a technical writer who creates clear documentation and guides.",
        },
    ],
    labels=["production"],
    config={"temperature": 0.3, "top_p": 0.8},
)

langfuse.create_prompt(
    name="brainstorm facilitator",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are an energetic brainstorm facilitator who generates creative ideas.",
        },
    ],
    labels=["production"],
    config={"temperature": 0.9, "top_p": 0.95},
)

langfuse.create_prompt(
    name="debug assistant",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a debugging expert who helps identify and fix code issues.",
        },
    ],
    labels=["production"],
    config={"temperature": 0.1, "top_p": 0.8},
)

langfuse.create_prompt(
    name="meeting summarizer",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a meeting summarizer who creates concise action-oriented summaries.",
        },
    ],
    labels=["production"],
    config={"temperature": 0.2, "top_p": 0.85},
)

langfuse.create_prompt(
    name="product manager",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a strategic product manager who provides product insights and roadmap guidance.",
        },
    ],
    labels=["production"],
    config={"temperature": 0.4, "top_p": 0.9},
)

