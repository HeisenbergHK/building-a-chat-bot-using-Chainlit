import chainlit as cl
from chatbot_functionality import get_response


@cl.step(type="tool")
async def tool(message: cl.Message):
    response = get_response(message)

    return response

@cl.on_message  # THis will call every time the user input a message in hte UI
async def main(message: cl.Message):
    tool_response = await tool(message)
    await cl.Message(content=tool_response).send()
