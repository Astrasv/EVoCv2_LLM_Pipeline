from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class NotebookCellBase(BaseModel):
    cell_type: str
    code: str = ""
    agent_id: Optional[str] = None
    version: int = 1
    position: int
    is_active: bool = True


class NotebookCellCreate(NotebookCellBase):
    notebook_id: UUID


class NotebookCellUpdate(BaseModel):
    cell_type: Optional[str] = None
    code: Optional[str] = None
    agent_id: Optional[str] = None
    version: Optional[int] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None


class NotebookCell(NotebookCellBase):
    id: UUID
    notebook_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotebookBase(BaseModel):
    name: str
    deap_toolbox_config: Dict[str, Any] = {}
    status: str = "draft"


class NotebookCreate(NotebookBase):
    problem_id: UUID


class NotebookUpdate(BaseModel):
    name: Optional[str] = None
    deap_toolbox_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class Notebook(NotebookBase):
    id: UUID
    problem_id: UUID
    cells: List[NotebookCell] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
