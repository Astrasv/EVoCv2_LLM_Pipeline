from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel


class ChatThreadBase(BaseModel):
    title: Optional[str] = None
    message_count: int = 0
    is_active: bool = True


class ChatThreadCreate(ChatThreadBase):
    notebook_id: UUID


class ChatThread(ChatThreadBase):
    id: UUID
    notebook_id: UUID
    created_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    message: str
    sender: str
    message_type: str = "user_input"
    iteration_context: Optional[int] = None
    metadata: Dict[str, Any] = {}


class ChatMessageCreate(ChatMessageBase):
    notebook_id: UUID
    thread_id: Optional[UUID] = None
    parent_message_id: Optional[UUID] = None


class ChatMessage(ChatMessageBase):
    id: UUID
    notebook_id: UUID
    thread_id: Optional[UUID] = None
    parent_message_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatContext(BaseModel):
    id: UUID
    notebook_id: UUID
    context_summary: str
    message_range_start: datetime
    message_range_end: datetime
    token_count: int = 0
    created_at: datetime
    is_current: bool = True

    class Config:
        from_attributes = True
