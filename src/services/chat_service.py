import json
from datetime import datetime
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func

from src.config.database import get_database

logger = logging.getLogger(__name__)


class ChatService:
    """Simple chat history service using direct SQL"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def add_message(
        self,
        notebook_id: UUID,
        message: str,
        sender: str,  # 'user' or agent name like 'fitness_agent'
        message_type: str = 'user_input',
        iteration_context: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a chat message"""
        
        try:
            message_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            stmt = text("""
                INSERT INTO chat_messages 
                (id, notebook_id, message, sender, message_type, iteration_context, metadata, created_at, updated_at)
                VALUES (:id, :notebook_id, :message, :sender, :message_type, :iteration_context, :metadata, :created_at, :updated_at)
                RETURNING id, created_at
            """)
            
            result = await self.db.execute(stmt, {
                "id": message_id,
                "notebook_id": str(notebook_id),
                "message": message,
                "sender": sender,
                "message_type": message_type,
                "iteration_context": iteration_context,
                "metadata": json.dumps(metadata or {}),
                "created_at": now,
                "updated_at": now
            })
            
            row = result.fetchone()
            await self.db.commit()
            
            return {
                "id": message_id,
                "notebook_id": str(notebook_id),
                "message": message,
                "sender": sender,
                "message_type": message_type,
                "iteration_context": iteration_context,
                "metadata": metadata or {},
                "created_at": row.created_at.isoformat()
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to add message: {e}")
            raise
    
    async def get_chat_history(
        self,
        notebook_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get chat history for a notebook"""
        
        try:
            stmt = text("""
                SELECT id, notebook_id, message, sender, message_type, iteration_context, 
                       metadata, created_at, updated_at
                FROM chat_messages 
                WHERE notebook_id = :notebook_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            
            result = await self.db.execute(stmt, {
                "notebook_id": str(notebook_id),
                "limit": limit,
                "offset": offset
            })
            
            messages = []
            for row in result.fetchall():

                if row.metadata:
                    metadata = row.metadata if isinstance(row.metadata, dict) else json.loads(row.metadata)
                else:
                    metadata = {}
                
                messages.append({
                    "id": str(row.id),
                    "notebook_id": str(row.notebook_id),
                    "message": row.message,
                    "sender": row.sender,
                    "message_type": row.message_type,
                    "iteration_context": row.iteration_context,
                    "metadata": metadata,
                    "created_at": row.created_at.isoformat(),
                    "updated_at": row.updated_at.isoformat()
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            raise
    
    async def get_recent_context(
        self,
        notebook_id: UUID,
        max_messages: int = 10
    ) -> str:
        """Get recent chat context as formatted string"""
        
        try:
            messages = await self.get_chat_history(notebook_id, limit=max_messages)
            
            if not messages:
                return "No previous conversation."
            
            context_parts = []
            for msg in reversed(messages):  # Reverse to get chronological order
                sender = msg['sender']
                message = msg['message']
                context_parts.append(f"{sender}: {message}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get recent context: {e}")
            return "Error retrieving context."
