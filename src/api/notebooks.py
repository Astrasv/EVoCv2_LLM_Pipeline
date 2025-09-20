from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.models.notebook import NotebookCreate, NotebookUpdate, NotebookCellUpdate

from src.config.database import get_database
from src.utils.security import get_current_user_id
from src.utils.responses import success_response, error_response, paginated_response
from src.persistence.repositories.notebook_repo import NotebookRepository
from src.persistence.repositories.problem_repo import ProblemRepository

router = APIRouter()


def convert_cell_to_dict(cell_orm) -> dict:
    """Convert NotebookCellORM to response dict"""
    return {
        "id": str(cell_orm.id),
        "notebook_id": str(cell_orm.notebook_id),
        "cell_type": cell_orm.cell_type,
        "code": cell_orm.code,
        "agent_id": cell_orm.agent_id,
        "version": cell_orm.version,
        "position": cell_orm.position,
        "is_active": cell_orm.is_active,
        "created_at": cell_orm.created_at.isoformat(),
        "updated_at": cell_orm.updated_at.isoformat()
    }


def convert_notebook_orm_to_response(notebook_orm) -> dict:
    """Convert NotebookORM to response dict"""
    return {
        "id": str(notebook_orm.id),
        "problem_id": str(notebook_orm.problem_id),
        "name": notebook_orm.name,
        "deap_toolbox_config": notebook_orm.deap_toolbox_config,
        "status": notebook_orm.status,
        "created_at": notebook_orm.created_at.isoformat(),
        "updated_at": notebook_orm.updated_at.isoformat(),
        "cells": [convert_cell_to_dict(cell) for cell in notebook_orm.cells] if hasattr(notebook_orm, 'cells') and notebook_orm.cells else []
    }


@router.post("/notebooks", status_code=status.HTTP_201_CREATED)
async def create_notebook(
    notebook_data: NotebookCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Create a new notebook for a problem"""
    try:
        # Step 1: Verify problem ownership
        from sqlalchemy import text
        problem_check = await db.execute(
            text("SELECT id FROM problem_statements WHERE id = :problem_id AND user_id = :user_id"),
            {"problem_id": str(notebook_data.problem_id), "user_id": current_user_id}
        )
        
        if not problem_check.fetchone():
            return error_response(
                message="Problem not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Step 2: Insert notebook with consistent named parameters
        import uuid
        from datetime import datetime
        import json
        
        notebook_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        insert_stmt = text("""
            INSERT INTO notebooks (id, problem_id, name, deap_toolbox_config, status, created_at, updated_at)
            VALUES (:id, :problem_id, :name, :config, :status, :created_at, :updated_at)
            RETURNING id, problem_id, name, status, created_at, updated_at
        """)
        
        result = await db.execute(insert_stmt, {
            "id": notebook_id,
            "problem_id": str(notebook_data.problem_id),
            "name": notebook_data.name,
            "config": json.dumps(notebook_data.deap_toolbox_config),  # Convert to JSON string
            "status": "draft",
            "created_at": now,
            "updated_at": now
        })
        
        # Step 3: Build response
        row = result.fetchone()
        notebook_dict = {
            "id": str(row.id),
            "problem_id": str(row.problem_id),
            "name": row.name,
            "status": row.status,
            "deap_toolbox_config": notebook_data.deap_toolbox_config,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
            "cells": []
        }
        
        await db.commit()
        
        return success_response(
            data=notebook_dict,
            message="Notebook created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        await db.rollback()
        return error_response(
            message=f"Failed to create notebook: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@router.get("/notebooks")
async def list_notebooks(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """List user's notebooks with pagination"""
    notebook_repo = NotebookRepository(db)
    
    try:
        notebooks_orm, total = await notebook_repo.list_by_user(
            user_id=UUID(current_user_id),
            page=page,
            size=size,
            status=status_filter
        )
        
        # Convert all notebooks to dicts
        notebooks_dict = [convert_notebook_orm_to_response(n) for n in notebooks_orm]
        
        return paginated_response(
            items=notebooks_dict,
            total=total,
            page=page,
            size=size,
            message="Notebooks retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve notebooks: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/notebooks/{notebook_id}")
async def get_notebook(
    notebook_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Get a specific notebook with cells"""
    notebook_repo = NotebookRepository(db)
    
    notebook_orm = await notebook_repo.get_by_id_and_user(notebook_id, UUID(current_user_id))
    if not notebook_orm:
        return error_response(
            message="Notebook not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Convert to dict for JSON serialization
    notebook_dict = convert_notebook_orm_to_response(notebook_orm)
    
    return success_response(data=notebook_dict, message="Notebook retrieved successfully")


@router.put("/notebooks/{notebook_id}")
async def update_notebook(
    notebook_id: UUID,
    notebook_update: NotebookUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Update a notebook"""
    notebook_repo = NotebookRepository(db)
    
    # Verify ownership
    existing_notebook = await notebook_repo.get_by_id_and_user(notebook_id, UUID(current_user_id))
    if not existing_notebook:
        return error_response(
            message="Notebook not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    try:
        notebook_orm = await notebook_repo.update(notebook_id, notebook_update)
        
        # Convert to dict for JSON serialization
        notebook_dict = convert_notebook_orm_to_response(notebook_orm)
        
        return success_response(data=notebook_dict, message="Notebook updated successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to update notebook: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/notebooks/{notebook_id}")
async def delete_notebook(
    notebook_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Delete a notebook"""
    notebook_repo = NotebookRepository(db)
    
    # Verify ownership
    existing_notebook = await notebook_repo.get_by_id_and_user(notebook_id, UUID(current_user_id))
    if not existing_notebook:
        return error_response(
            message="Notebook not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    try:
        await notebook_repo.delete(notebook_id)
        return success_response(message="Notebook deleted successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to delete notebook: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/notebooks/{notebook_id}/cells/{cell_id}")
async def update_notebook_cell(
    notebook_id: UUID,
    cell_id: UUID,
    cell_update: NotebookCellUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Update a specific notebook cell"""
    notebook_repo = NotebookRepository(db)
    
    # Verify notebook ownership
    existing_notebook = await notebook_repo.get_by_id_and_user(notebook_id, UUID(current_user_id))
    if not existing_notebook:
        return error_response(
            message="Notebook not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    try:
        cell_orm = await notebook_repo.update_cell(cell_id, cell_update)
        if not cell_orm:
            return error_response(
                message="Cell not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Convert to dict for JSON serialization
        cell_dict = convert_cell_to_dict(cell_orm)
        
        return success_response(data=cell_dict, message="Cell updated successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to update cell: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/notebooks/{notebook_id}/execute")
async def execute_notebook(
    notebook_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Execute notebook (placeholder for future implementation)"""
    notebook_repo = NotebookRepository(db)
    
    # Verify ownership
    existing_notebook = await notebook_repo.get_by_id_and_user(notebook_id, UUID(current_user_id))
    if not existing_notebook:
        return error_response(
            message="Notebook not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # TODO: Implement notebook execution logic in future modules
    # This will involve running DEAP code generation and evolution
    
    return success_response(
        data={"execution_id": "placeholder"},
        message="Notebook execution started (placeholder implementation)"
    )


@router.get("/notebooks/{notebook_id}/deap-export")
async def export_deap_code(
    notebook_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Export DEAP-ready code from notebook"""
    notebook_repo = NotebookRepository(db)
    
    # Verify ownership
    existing_notebook = await notebook_repo.get_by_id_and_user(notebook_id, UUID(current_user_id))
    if not existing_notebook:
        return error_response(
            message="Notebook not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # TODO: Implement DEAP code export logic in future modules
    # This will involve combining all cells into a complete DEAP script
    
    return success_response(
        data={"code": "# DEAP code will be generated here"},
        message="DEAP code exported successfully (placeholder implementation)"
    )
    

@router.post("/notebooks/debug")
async def debug_notebook_creation(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Debug endpoint to isolate the issue"""
    try:
        # Test 1: Simple query
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1 as test"))
        test_val = result.scalar()
        
        # Test 2: Check if problem exists
        from sqlalchemy import select
        from src.persistence.repositories.user_repo import ProblemStatementORM
        stmt = select(ProblemStatementORM).limit(1)
        problem_result = await db.execute(stmt)
        
        return success_response(
            data={
                "test_query": test_val,
                "problems_table_accessible": "yes"
            },
            message="Debug successful"
        )
    except Exception as e:
        return error_response(
            message=f"Debug failed: {str(e)}",
            status_code=500
        )