from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class ProblemStatementBase(BaseModel):
    title: str
    description: str
    problem_type: str
    constraints: Dict[str, Any] = {}
    objectives: List[str] = []


class ProblemStatementCreate(ProblemStatementBase):
    user_id: UUID


class ProblemStatementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    problem_type: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    objectives: Optional[List[str]] = None


class ProblemStatement(ProblemStatementBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True