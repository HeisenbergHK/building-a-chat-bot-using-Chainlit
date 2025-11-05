import chainlit as cl


@cl.step(type="tool")
async def tool():
    # Faking respinse time
    await cl.sleep(2)
    return "This is a sample response."


@cl.on_message  # THis will call every time the user input a message in hte UI
async def main(message: cl.Message):
    tool_response = await tool()
    await cl.Message(content=tool_response).send()
