import chainlit as cl
from chatbot_functionality import get_response, update_response_async


@cl.on_chat_start
def start_chat():
    cl.user_session.set("message_history", [{"role": "system", "content": "Be angry!"}])


@cl.on_message  # THis will call every time the user input a message in hte UI
async def main(message: cl.Message):

    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    print(message_history)

    result = cl.Message(content="")
    await update_response_async(message_history, message=result)

    message_history.append({"role": "assistant", "content": result.content})
    cl.user_session.set("message_history", message_history)
