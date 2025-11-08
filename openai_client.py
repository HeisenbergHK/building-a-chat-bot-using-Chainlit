from typing import List, Optional

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
        self,
        message_history: List[cl.Message],
        response: cl.Message,
        temperature=0.5,  # A lower temperature results in more predictable and focused responses
        top_p: Optional[
            float
        ] = 1.0,  # Top-p, or nucleus sampling, determines the range of tokens the model considers when generating each word.
        frequency_penalty: Optional[
            float
        ] = 0.0,  # This parameter is used to discourage the model from repeating the same words or phrases too frequently within the generated text.
        presence_penalty: Optional[
            float
        ] = 0.0,  # This parameter is used to encourage the model to include a diverse range of tokens in the generated text.
        max_tokens: Optional[int] = None,
    ):
        stream = await self.client.chat.completions.create(
            model=self.model,
            stream=True,
            messages=message_history,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            max_tokens=max_tokens,
        )

        async with stream:

            async for chunk in stream:
                try:
                    if token := chunk.choices[0].delta.content or "":
                        await response.stream_token(token)
                except (IndexError, AttributeError):
                    continue  # Handle malformed chunks

            message_history.append({"role": "assistant", "content": response.content})
            await response.update()
