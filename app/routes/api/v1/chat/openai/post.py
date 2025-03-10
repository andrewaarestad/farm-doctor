from app.managers.openai_chat_manager import OpenAIChatManager
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from typing import AsyncIterator, Optional
from app.core.session_manager import SessionManager
from langchain_core.messages import HumanMessage, AIMessage


openai_router = APIRouter()
openai_session_manager = SessionManager()
chat_manager = OpenAIChatManager()

class QueryRequestDto(BaseModel):
    question: str
    context: str = ""
    session_id: Optional[str] = None
    

@openai_router.post("/chat/openai")
async def chat_controller(request: QueryRequestDto):
    if request.session_id is None:
        print('Creating new session')
    else:
        print('continuing session ', request.session_id)
    session_id = request.session_id or str(uuid.uuid4())
    print("session", session_id, "received question: ", request.question)
    chat_history = openai_session_manager.get_messages(session_id)
    # print("fetched chat history: ", chat_history)
    openai_session_manager.add_message(
        session_id,
        HumanMessage(content=request.question)
    )
    async def response_generator():
        response_content = []
        async for chunk in chat_manager.aquery(
            question=request.question,
            context=request.context,
            chat_history=chat_history
        ):
            response_content.append(chunk)
            yield f"data: {chunk}\n\n"
        

        # Save response to session cache
        full_response = "".join(response_content)
        print('finished streaming response: ', full_response)
        print('saving to session cache ', session_id)
        openai_session_manager.add_message(
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

@openai_router.get("/chat_history/{session_id}")
async def get_chat_history(session_id: str):
    messages = openai_session_manager.get_messages(session_id)
    return {
        "session_id": session_id,
        "messages": [
            {"role": "user" if isinstance(m, HumanMessage) else "assistant",
             "content": m.content}
            for m in messages
        ]
    }

# # Periodically clean up expired sessions
@openai_router.on_event("startup")
@openai_router.on_event("shutdown")
async def cleanup_sessions():
    openai_session_manager.cleanup_expired_sessions()