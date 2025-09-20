from langchain_postgres import PostgresChatMessageHistory
from sqlalchemy import create_engine
from typing import Optional
import logging

from .settings import settings

logger = logging.getLogger(__name__)


class ExtendedPostgresChatHistory(PostgresChatMessageHistory):
    """Extended LangChain chat history with custom metadata support"""
    
    def __init__(self, session_id: str, connection_string: str, table_name: str = "message_store"):
        super().__init__(session_id, connection_string, table_name)
        self.notebook_id = session_id
        self.logger = logging.getLogger(__name__)
    
    async def add_agent_message(self, content: str, agent_id: str, 
                               iteration_context: Optional[int] = None, 
                               metadata: Optional[dict] = None):
        """Add message with agent-specific metadata"""
        from langchain.schema import AIMessage
        
        message = AIMessage(
            content=content,
            additional_kwargs={
                "agent_id": agent_id,
                "iteration_context": iteration_context,
                "message_type": "agent_response",
                "metadata": metadata or {}
            }
        )
        self.add_message(message)
        self.logger.debug(f"Added agent message from {agent_id}")
    
    async def add_user_message(self, content: str, iteration_context: Optional[int] = None):
        """Add user message with context"""
        from langchain.schema import HumanMessage
        from datetime import datetime
        
        message = HumanMessage(
            content=content,
            additional_kwargs={
                "iteration_context": iteration_context,
                "message_type": "user_input",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.add_message(message)
        self.logger.debug("Added user message")


def get_chat_history(notebook_id: str) -> ExtendedPostgresChatHistory:
    """Get chat history for a notebook"""
    # Convert async URL to sync for LangChain compatibility
    sync_db_url = settings.database_url.replace('+asyncpg', '+psycopg2')
    
    return ExtendedPostgresChatHistory(
        session_id=str(notebook_id),
        connection_string=sync_db_url,
        table_name="message_store"
    )
