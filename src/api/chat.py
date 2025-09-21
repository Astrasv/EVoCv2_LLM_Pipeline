from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import uuid

from typing import Optional

from src.config.database import get_database
from src.utils.security import get_current_user_id
from src.utils.responses import success_response, error_response
from src.services.chat_service import ChatService
from src.services.chatgroq_service import chatgroq_service
from src.services.context_service import context_service
from src.utils.prompts import get_agent_prompt

router = APIRouter()


@router.post("/chat/{notebook_id}/messages")
async def send_message(
    notebook_id: UUID,
    message_data: dict,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Send a message and get AI response"""
    
    try:
        # Verify notebook ownership first
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
        
        user_message = message_data.get("message", "")
        if not user_message:
            return error_response(
                message="Message content required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        chat_service = ChatService(db)
        
        # Add user message to chat history
        user_msg = await chat_service.add_message(
            notebook_id=notebook_id,
            message=user_message,
            sender="user",
            message_type="user_input"
        )
        
        # Get recent context for AI response
        recent_context = await chat_service.get_recent_context(notebook_id, max_messages=10)
        
        # Generate AI response
        try:
            ai_response = await chatgroq_service.generate_response(
                prompt=f"User message: {user_message}\n\nRecent conversation:\n{recent_context}",
                system_prompt="You are an AI assistant helping with evolutionary algorithm development. Provide helpful, concise responses.",
                max_tokens=1000
            )
            
            # Add AI response to chat history
            ai_msg = await chat_service.add_message(
                notebook_id=notebook_id,
                message=ai_response,
                sender="assistant",
                message_type="ai_response"
            )
            
            return success_response(
                data={
                    "user_message": user_msg,
                    "ai_response": ai_msg
                },
                message="Message sent and response generated"
            )
            
        except Exception as e:
            # Still save user message even if AI fails
            return success_response(
                data={
                    "user_message": user_msg,
                    "ai_response": None,
                    "ai_error": str(e)
                },
                message="Message saved, but AI response failed"
            )
        
    except Exception as e:
        return error_response(
            message=f"Failed to send message: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/chat/{notebook_id}/history")
async def get_chat_history(
    notebook_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Get chat history for a notebook"""
    
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
        
        chat_service = ChatService(db)
        offset = (page - 1) * size
        
        messages = await chat_service.get_chat_history(
            notebook_id=notebook_id,
            limit=size,
            offset=offset
        )
        
        return success_response(
            data={
                "messages": messages,
                "page": page,
                "size": size,
                "total": len(messages)
            },
            message="Chat history retrieved"
        )
        
    except Exception as e:
        return error_response(
            message=f"Failed to get chat history: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/chat/{notebook_id}/generate-code")
async def generate_code(
    notebook_id: UUID,
    request_data: dict,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Generate DEAP code using ChatGroq"""
    
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
        
        # Extract request parameters
        code_type = request_data.get("code_type", "fitness")  # fitness, selection, crossover, mutation
        current_code = request_data.get("current_code")
        feedback = request_data.get("feedback")
        
        if code_type not in ["fitness", "selection", "crossover", "mutation"]:
            return error_response(
                message="Invalid code_type. Must be: fitness, selection, crossover, or mutation",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Build problem description
        problem_description = f"""
Title: {notebook_row.title}
Description: {notebook_row.description}
Type: {notebook_row.problem_type}
Objectives: {notebook_row.objectives}
Constraints: {notebook_row.constraints}
        """.strip()
        
        # Get chat context
        chat_service = ChatService(db)
        chat_history = await chat_service.get_recent_context(notebook_id, max_messages=5)
        
        # Build context for code generation
        context = context_service.build_agent_context(
            problem_description=problem_description,
            agent_type=code_type,
            current_code=current_code,
            chat_history=chat_history,
            feedback=feedback
        )
        
        # Add agent-specific prompt
        agent_prompt = get_agent_prompt(code_type)
        full_prompt = f"{context['user_prompt']}\n\n{agent_prompt}"
        
        # Generate code
        result = await chatgroq_service.generate_code(
            problem_description=problem_description,
            code_type=code_type,
            current_code=current_code,
            feedback=feedback
        )
        
        if result["success"]:
            # Save the generation event to chat history
            await chat_service.add_message(
                notebook_id=notebook_id,
                message=f"Generated {code_type} code",
                sender=f"{code_type}_agent",
                message_type="code_generation",
                metadata={
                    "code_type": code_type,
                    "generation_time": result["generation_time"],
                    "has_feedback": bool(feedback)
                }
            )
        
        return success_response(
            data=result,
            message=f"Code generation {'completed' if result['success'] else 'failed'}"
        )
        
    except Exception as e:
        return error_response(
            message=f"Failed to generate code: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/chat/test-groq")
async def test_chatgroq():
    """Test ChatGroq connection"""
    try:
        response = await chatgroq_service.generate_response(
            prompt="Hello! Please respond with 'ChatGroq is working correctly'",
            system_prompt="You are a test assistant.",
            max_tokens=50
        )
        
        return success_response(
            data={"response": response},
            message="ChatGroq test successful"
        )
        
    except Exception as e:
        return error_response(
            message=f"ChatGroq test failed: {str(e)}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )