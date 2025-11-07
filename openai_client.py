from typing import List

import chainlit as cl
from openai import AsyncOpenAI


class OpenAIClient:
    def __init__(self, API_KEY: str, API_URL: str, model: str):
        self.API_KEY = API_KEY
        self.API_URL = API_URL
        self.model = model

        # This is an async client
        self.client = AsyncOpenAI(base_url=self.API_URL, api_key=self.API_KEY)

    async def stream_update_response(
        self, message_history: List[cl.Message], response: cl.Message
    ):
        stream = await self.client.chat.completions.create(
            model=self.model, stream=True, messages=message_history
        )

        async for chunk in stream:
            if token := chunk.choices[0].delta.content:
                await response.stream_token(token)

        message_history.append({"role": "assistant", "content": response.content})
        await response.update()
