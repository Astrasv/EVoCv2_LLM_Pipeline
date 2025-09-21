from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from src.config.database import get_database
from src.utils.security import get_current_user_id
from src.utils.responses import success_response, error_response
from src.services.agent_coordinator import AgentCoordinator
from src.services.cell_management_service import CellManagementService

router = APIRouter()


@router.post("/agents/{notebook_id}/coordinate")
async def coordinate_agents(
    notebook_id: UUID,
    coordination_config: dict = None,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Coordinate all agents to generate DEAP code"""
    
    try:
        # Verify notebook ownership
        from sqlalchemy import text
        notebook_check = await db.execute(
            text("""
                SELECT n.id, p.title, p.description, p.problem_type, p.objectives, p.constraints
                FROM notebooks n 
                JOIN problem_statements p ON n.problem_id = p.id 
                WHERE n.id = :notebook_id AND p.user_id = :user_id
            """),
            {"notebook_id": str(notebook_id), "user_id": current_user_id}
        )
        
        notebook_row = notebook_check.fetchone()
        if not notebook_row:
            return error_response(
                message="Notebook not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Build problem context
        problem_context = {
            "title": notebook_row.title,
            "description": notebook_row.description,
            "problem_type": notebook_row.problem_type,
            "objectives": notebook_row.objectives,
            "constraints": notebook_row.constraints
        }
        
        # Initialize agent coordinator
        coordinator = AgentCoordinator(db)
        
        # Execute agent coordination
        result = await coordinator.coordinate_agents(notebook_id, problem_context)
        
        if result["success"]:
            return success_response(
                data=result,
                message="Agent coordination completed successfully",
                status_code=status.HTTP_200_OK
            )
        else:
            return error_response(
                message=result["message"],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return error_response(
            message=f"Failed to coordinate agents: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/agents/{notebook_id}/status")
async def get_agent_status(
    notebook_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Get status of all agents for a notebook"""
    
    try:
        # Verify notebook ownership
        from sqlalchemy import text
        notebook_check = await db.execute(
            text("""
                SELECT n.id FROM notebooks n 
                JOIN problem_statements p ON n.problem_id = p.id 
                WHERE n.id = :notebook_id AND p.user_id = :user_id
            """),
            {"notebook_id": str(notebook_id), "user_id": current_user_id}
        )
        
        if not notebook_check.fetchone():
            return error_response(
                message="Notebook not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Get agent status
        coordinator = AgentCoordinator(db)
        agent_status = await coordinator.get_agent_status()
        
        # Get cell information
        cell_service = CellManagementService(db)
        cells = await cell_service.get_notebook_cells(notebook_id)
        
        return success_response(
            data={
                "notebook_id": str(notebook_id),
                "agent_status": agent_status,
                "cells": cells,
                "total_cells": len(cells)
            },
            message="Agent status retrieved successfully"
        )
        
    except Exception as e:
        return error_response(
            message=f"Failed to get agent status: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/agents/{notebook_id}/cells")
async def get_notebook_cells(
    notebook_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Get all cells for a notebook"""
    
    try:
        # Verify notebook ownership
        from sqlalchemy import text
        notebook_check = await db.execute(
            text("""
                SELECT n.id FROM notebooks n 
                JOIN problem_statements p ON n.problem_id = p.id 
                WHERE n.id = :notebook_id AND p.user_id = :user_id
            """),
            {"notebook_id": str(notebook_id), "user_id": current_user_id}
        )
        
        if not notebook_check.fetchone():
            return error_response(
                message="Notebook not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Get cells
        cell_service = CellManagementService(db)
        cells = await cell_service.get_notebook_cells(notebook_id)
        
        return success_response(
            data={
                "notebook_id": str(notebook_id),
                "cells": cells,
                "total_cells": len(cells)
            },
            message="Notebook cells retrieved successfully"
        )
        
    except Exception as e:
        return error_response(
            message=f"Failed to get notebook cells: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/agents/{notebook_id}/complete-code")
async def get_complete_code(
    notebook_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Get complete DEAP code combining all cells"""
    
    try:
        # Verify notebook ownership
        from sqlalchemy import text
        notebook_check = await db.execute(
            text("""
                SELECT n.id FROM notebooks n 
                JOIN problem_statements p ON n.problem_id = p.id 
                WHERE n.id = :notebook_id AND p.user_id = :user_id
            """),
            {"notebook_id": str(notebook_id), "user_id": current_user_id}
        )
        
        if not notebook_check.fetchone():
            return error_response(
                message="Notebook not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Get complete code
        cell_service = CellManagementService(db)
        complete_code = await cell_service.get_complete_notebook_code(notebook_id)
        
        return success_response(
            data={
                "notebook_id": str(notebook_id),
                "complete_code": complete_code,
                "code_length": len(complete_code)
            },
            message="Complete code retrieved successfully"
        )
        
    except Exception as e:
        return error_response(
            message=f"Failed to get complete code: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/agents/{notebook_id}/regenerate/{cell_type}")
async def regenerate_cell(
    notebook_id: UUID,
    cell_type: str,
    regeneration_request: dict = None,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Regenerate a specific cell type"""
    
    try:
        # Verify notebook ownership and get problem context
        from sqlalchemy import text
        notebook_check = await db.execute(
            text("""
                SELECT n.id, p.title, p.description, p.problem_type, p.objectives, p.constraints
                FROM notebooks n 
                JOIN problem_statements p ON n.problem_id = p.id 
                WHERE n.id = :notebook_id AND p.user_id = :user_id
            """),
            {"notebook_id": str(notebook_id), "user_id": current_user_id}
        )
        
        notebook_row = notebook_check.fetchone()
        if not notebook_row:
            return error_response(
                message="Notebook not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate cell type
        valid_cell_types = [
            "problem_analysis", "individual_representation", "fitness", 
            "crossover", "mutation", "selection", "toolbox_registration"
        ]
        
        if cell_type not in valid_cell_types:
            return error_response(
                message=f"Invalid cell type. Must be one of: {valid_cell_types}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Build problem context
        problem_context = {
            "title": notebook_row.title,
            "description": notebook_row.description,
            "problem_type": notebook_row.problem_type,
            "objectives": notebook_row.objectives,
            "constraints": notebook_row.constraints
        }
        
        # Initialize coordinator and get specific agent
        coordinator = AgentCoordinator(db)
        
        # Map cell types to agent IDs
        cell_to_agent = {
            "problem_analysis": "problem_analyser",
            "individual_representation": "individuals_modelling",
            "fitness": "fitness_function",
            "crossover": "crossover_function",
            "mutation": "mutation_function",
            "selection": "selection_strategy",
            "toolbox_registration": "code_integration"
        }
        
        agent_id = cell_to_agent[cell_type]
        agent = coordinator.agents[agent_id]
        
        # Get existing cells for context
        cell_service = CellManagementService(db)
        existing_cells = await cell_service.get_notebook_cells(notebook_id)
        
        # Add existing code to agent context
        for cell in existing_cells:
            if cell["cell_type"] != cell_type:  # Don't include the cell we're regenerating
                agent.context[f"{cell['cell_type']}_code"] = cell["code"]
        
        # Generate new code
        generated_code = await agent.generate_code(problem_context)
        
        # Update cell
        cell_result = await cell_service.update_or_create_cell(
            notebook_id=notebook_id,
            cell_type=cell_type,
            code=generated_code,
            agent_id=agent.agent_id,
            position=agent.cell_position
        )
        
        return success_response(
            data={
                "notebook_id": str(notebook_id),
                "cell_type": cell_type,
                "cell_id": cell_result["cell_id"],
                "action": cell_result["action"],
                "version": cell_result["version"],
                "generated_code": generated_code
            },
            message=f"Cell {cell_type} regenerated successfully"
        )
        
    except Exception as e:
        return error_response(
            message=f"Failed to regenerate cell: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )