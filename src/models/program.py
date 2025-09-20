from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class ProgramDatabaseBase(BaseModel):
    program_code: str
    program_type: str
    deap_operators: Dict[str, Any] = {}
    performance_metrics: Dict[str, Any] = {}
    problem_characteristics: Dict[str, Any] = {}
    test_results: Dict[str, Any] = {}
    generation: int = 1
    is_best_performer: bool = False
    tags: List[str] = []


class ProgramDatabaseCreate(ProgramDatabaseBase):
    notebook_id: UUID
    parent_program_id: Optional[UUID] = None


class ProgramDatabase(ProgramDatabaseBase):
    id: UUID
    notebook_id: UUID
    parent_program_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EvaluatorResultBase(BaseModel):
    evaluator_type: str
    test_input: Optional[Any] = None
    expected_output: Optional[Any] = None
    actual_output: Optional[Any] = None
    score: Optional[float] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}


class EvaluatorResultCreate(EvaluatorResultBase):
    program_id: UUID


class EvaluatorResult(EvaluatorResultBase):
    id: UUID
    program_id: UUID
    evaluated_at: datetime

    class Config:
        from_attributes = True
