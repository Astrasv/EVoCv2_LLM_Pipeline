from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.problem import ProblemStatementCreate, ProblemStatementUpdate
from src.config.database import get_database
from src.utils.security import get_current_user_id
from src.utils.responses import success_response, error_response, paginated_response
from src.persistence.repositories.problem_repo import ProblemRepository

router = APIRouter()


def convert_problem_orm_to_response(problem_orm) -> dict:
    """Convert ProblemORM to response dict"""
    return {
        "id": str(problem_orm.id),
        "user_id": str(problem_orm.user_id),
        "title": problem_orm.title,
        "description": problem_orm.description,
        "problem_type": problem_orm.problem_type,
        "constraints": problem_orm.constraints,
        "objectives": problem_orm.objectives,
        "created_at": problem_orm.created_at.isoformat(),
        "updated_at": problem_orm.updated_at.isoformat()
    }


@router.post("/problems", status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemStatementCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Create a new problem statement"""
    problem_repo = ProblemRepository(db)
    
    try:
        # Create problem with user_id from authentication
        problem_orm = await problem_repo.create_for_user(problem_data, UUID(current_user_id))
        
        # Convert to dict for JSON serialization
        problem_dict = convert_problem_orm_to_response(problem_orm)
        
        return success_response(
            data=problem_dict,
            message="Problem created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return error_response(
            message=f"Failed to create problem: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/problems")
async def list_problems(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    problem_type: Optional[str] = Query(None, description="Filter by problem type"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """List user's problems with pagination"""
    problem_repo = ProblemRepository(db)
    
    try:
        problems_orm, total = await problem_repo.list_by_user(
            user_id=UUID(current_user_id),
            page=page,
            size=size,
            problem_type=problem_type
        )
        
        # Convert all problems to dicts
        problems_dict = [convert_problem_orm_to_response(p) for p in problems_orm]
        
        return paginated_response(
            items=problems_dict,
            total=total,
            page=page,
            size=size,
            message="Problems retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve problems: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/problems/{problem_id}")
async def get_problem(
    problem_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Get a specific problem by ID"""
    problem_repo = ProblemRepository(db)
    
    problem_orm = await problem_repo.get_by_id_and_user(problem_id, UUID(current_user_id))
    if not problem_orm:
        return error_response(
            message="Problem not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Convert to dict for JSON serialization
    problem_dict = convert_problem_orm_to_response(problem_orm)
    
    return success_response(data=problem_dict, message="Problem retrieved successfully")


@router.put("/problems/{problem_id}")
async def update_problem(
    problem_id: UUID,
    problem_update: ProblemStatementUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Update a problem statement"""
    problem_repo = ProblemRepository(db)
    
    # Verify ownership
    existing_problem = await problem_repo.get_by_id_and_user(problem_id, UUID(current_user_id))
    if not existing_problem:
        return error_response(
            message="Problem not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    try:
        problem_orm = await problem_repo.update(problem_id, problem_update)
        
        # Convert to dict for JSON serialization
        problem_dict = convert_problem_orm_to_response(problem_orm)
        
        return success_response(data=problem_dict, message="Problem updated successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to update problem: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/problems/{problem_id}")
async def delete_problem(
    problem_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Delete a problem statement"""
    problem_repo = ProblemRepository(db)
    
    # Verify ownership
    existing_problem = await problem_repo.get_by_id_and_user(problem_id, UUID(current_user_id))
    if not existing_problem:
        return error_response(
            message="Problem not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    try:
        await problem_repo.delete(problem_id)
        return success_response(message="Problem deleted successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to delete problem: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/problems/{problem_id}/questionnaire")
async def submit_problem_questionnaire(
    problem_id: UUID,
    questionnaire_data: dict,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Submit questionnaire data for a problem"""
    problem_repo = ProblemRepository(db)
    
    # Verify ownership
    existing_problem = await problem_repo.get_by_id_and_user(problem_id, UUID(current_user_id))
    if not existing_problem:
        return error_response(
            message="Problem not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # TODO: Implement questionnaire processing logic in future modules
    return success_response(
        data={"questionnaire_id": "placeholder"},
        message="Questionnaire submitted successfully (placeholder implementation)"
    )