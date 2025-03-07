from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import json

class ChatSession(BaseModel):
    session_id: str
    messages: List[Dict]  # Will store serialized messages
    last_accessed: datetime
    metadata: Dict = {}

class SessionManager:
    def __init__(self, expiry_minutes: int = 30):
        self.sessions: Dict[str, ChatSession] = {}
        self.expiry_minutes = expiry_minutes

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        session = self.sessions.get(session_id)
        if session:
            # Update last accessed time
            session.last_accessed = datetime.now()
            return session
        return None

    def create_session(self, session_id: str) -> ChatSession:
        session = ChatSession(
            session_id=session_id,
            messages=[],
            last_accessed=datetime.now()
        )
        self.sessions[session_id] = session
        return session

    def add_message(self, session_id: str, message: BaseMessage):
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        
        # Convert message to dict for storage
        message_dict = {
            "type": message.__class__.__name__,
            "content": message.content,
            "timestamp": datetime.now().isoformat()
        }
        session.messages.append(message_dict)

    def get_messages(self, session_id: str) -> List[BaseMessage]:
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Convert stored dicts back to BaseMessage objects
        messages = []
        for msg in session.messages:
            if msg["type"] == "HumanMessage":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["type"] == "AIMessage":
                messages.append(AIMessage(content=msg["content"]))
        return messages

    def cleanup_expired_sessions(self):
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session.last_accessed > timedelta(minutes=self.expiry_minutes)
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]