from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class EvolutionStepBase(BaseModel):
    iteration: int
    agent_id: str
    generated_code: Optional[str] = None
    fitness_improvement: Optional[float] = None
    token_usage: int = 0
    reasoning: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = {}


class EvolutionStepCreate(EvolutionStepBase):
    session_id: UUID


class EvolutionStep(EvolutionStepBase):
    id: UUID
    session_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class EvolutionSessionBase(BaseModel):
    current_iteration: int = 0
    max_iterations: int = 5
    best_fitness: Optional[float] = None
    status: str = "pending"
    session_config: Dict[str, Any] = {}


class EvolutionSessionCreate(EvolutionSessionBase):
    notebook_id: UUID


class EvolutionSessionUpdate(BaseModel):
    current_iteration: Optional[int] = None
    max_iterations: Optional[int] = None
    best_fitness: Optional[float] = None
    status: Optional[str] = None
    session_config: Optional[Dict[str, Any]] = None


class EvolutionSession(EvolutionSessionBase):
    id: UUID
    notebook_id: UUID
    evolution_log: List[EvolutionStep] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True