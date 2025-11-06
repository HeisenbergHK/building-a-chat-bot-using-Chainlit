import chainlit as cl

from chatbot_functionality import get_response, update_response_async

MAX_HISTORY = 10


@cl.on_chat_start
def start_chat():
    cl.user_session.set("message_history", [{"role": "system", "content": "be so angry!"}])


@cl.on_message  # THis will call every time the user input a message in hte UI
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    # Prevent infinite history
    if len(message_history) > MAX_HISTORY + 1:
        message_history = [message_history[0]] + message_history[-MAX_HISTORY:]
    print(message_history)

    result = cl.Message(content="")
    await update_response_async(message_history, message=result)

    message_history.append({"role": "assistant", "content": result.content})
    cl.user_session.set("message_history", message_history)
