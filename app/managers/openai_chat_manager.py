from typing import Any, AsyncIterator, Dict, List
from openai import AsyncOpenAI
from langchain_core.messages import BaseMessage, HumanMessage

client = AsyncOpenAI()
default_model = 'gpt-4o-2024-08-06'

class OpenAIChatManager:
    def __init__(self, model_name: str = default_model, temperature: float = 0.7, streaming: bool = True):
        self.model_name = model_name
        self.temperature = temperature
        self.streaming = streaming


    async def aquery(
        self,
        question: str,
        context: str = "",
        chat_history: List[BaseMessage] = None,
        config: Dict[str, Any] = None
                     ) -> AsyncIterator[str]:

        messages = [
            { 'role': "system", 'content': "You are a helpful assistant." }
        ] + [{
            'role': 'user' if m.type == 'human' else 'assistant',
            'content': m.content
        } for m in chat_history] + [{
            'role': 'user',
            'content': question
        }]

        print('messages for request:')
        for message in messages:
            print('  - ', message)

        async with client.beta.chat.completions.stream(
            model=self.model_name,
            messages=messages,
        ) as stream:
            async for event in stream:
                if event.type == 'content.delta':
                    yield event.delta
            