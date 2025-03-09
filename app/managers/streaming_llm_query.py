
from typing import List

from typing import Any, AsyncIterator, Dict, List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

class StreamingLLMQuery:
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        streaming: bool = True
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            streaming=streaming
        )
        # Modified prompt template to include chat history
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Use the following context and chat history to answer the question.\n\nContext: {context}"),
            ("system", "Chat History:\n{chat_history}"),
            ("human", "{question}")
        ])
        
        self.output_parser = StrOutputParser()

    def format_chat_history(self, messages: List[BaseMessage]) -> str:
        if not messages:
            return "No previous messages"
        
        formatted = []
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)

    async def aquery(
        self,
        question: str,
        context: str = "",
        chat_history: List[BaseMessage] = None,
        config: Dict[str, Any] = None
    ) -> AsyncIterator[str]:
        if chat_history is None:
            chat_history = []

        if config is None:
            config = {"callbacks": None}

        formatted_history = self.format_chat_history(chat_history)
        
        chain = self.prompt | self.llm | self.output_parser

        async for chunk in chain.astream(
            {
                "context": context,
                "chat_history": formatted_history,
                "question": question
            },
            config=config
        ):
            yield chunk

