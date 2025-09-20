from datetime import datetime
from typing import Any, Dict
from uuid import UUID
from pydantic import BaseModel


class PersistentSessionBase(BaseModel):
    session_data: Dict[str, Any] = {}
    agent_states: Dict[str, Any] = {}
    variables: Dict[str, Any] = {}
    is_active: bool = True


class PersistentSessionCreate(PersistentSessionBase):
    notebook_id: UUID


class PersistentSession(PersistentSessionBase):
    id: UUID
    notebook_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True