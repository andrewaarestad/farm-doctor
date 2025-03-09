from app.managers.streaming_llm_query import StreamingLLMQuery
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from typing import AsyncIterator, Optional
from app.core.session_manager import SessionManager
from langchain_core.messages import HumanMessage, AIMessage


LLMRouter = APIRouter()
session_manager = SessionManager()
llm_query = StreamingLLMQuery()

class QueryRequestDto(BaseModel):
    question: str
    context: str = ""
    session_id: Optional[str] = None
    

@LLMRouter.post("/query")
async def query(request: QueryRequestDto):
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