from fastapi import APIRouter, HTTPException
from app.models.schema import LLMRequest, LLMResponse

LLMRouter = APIRouter()

@LLMRouter.post("/llm", response_model=LLMResponse)
async def query_llm(request: LLMRequest):
    try:
        # This is where you'd typically make a call to your LLM API
        # For example: OpenAI, Anthropic, etc.
        response = f"Processed prompt: {request.prompt}"
        return LLMResponse(
            text=response,
            model=request.model,
            tokens_used=len(response.split())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional
import asyncio
from app.core.session_manager import SessionManager
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

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




session_manager = SessionManager()
llm_query = StreamingLLMQuery()

class QueryRequest(BaseModel):
    question: str
    context: str = ""
    session_id: Optional[str] = None

async def stream_response(query_iterator: AsyncIterator[str]):
    async for chunk in query_iterator:
        yield f"data: {chunk}\n\n"

@LLMRouter.post("/query")
async def query(request: QueryRequest):
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get existing chat history or create new session
    chat_history = session_manager.get_messages(session_id)
    
    # Add the new user message to history
    session_manager.add_message(
        session_id,
        HumanMessage(content=request.question)
    )

    # Create streaming response
    async def response_generator():
        response_content = []
        async for chunk in llm_query.aquery(
            question=request.question,
            context=request.context,
            chat_history=chat_history
        ):
            response_content.append(chunk)
            yield f"data: {chunk}\n\n"
        
        # After completion, add AI response to history
        full_response = "".join(response_content)
        session_manager.add_message(
            session_id,
            AIMessage(content=full_response)
        )

    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream",
        headers={
            "X-Session-ID": session_id
        }
    )

# @app.get("/chat_history/{session_id}")
# async def get_chat_history(session_id: str):
#     messages = session_manager.get_messages(session_id)
#     return {
#         "session_id": session_id,
#         "messages": [
#             {"role": "user" if isinstance(m, HumanMessage) else "assistant",
#              "content": m.content}
#             for m in messages
#         ]
#     }

# # Periodically clean up expired sessions
# @app.on_event("startup")
# @app.on_event("shutdown")
async def cleanup_sessions():
    session_manager.cleanup_expired_sessions()