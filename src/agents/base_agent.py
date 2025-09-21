import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging



logger = logging.getLogger(__name__)


class AgentMessage:
    """Simple message passing between agents"""
    
    def __init__(self, from_agent: str, to_agent: str, message_type: str, 
                 content: Any, metadata: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.messages: List[AgentMessage] = []
        self.context: Dict[str, Any] = {}
        self.generated_code: Optional[str] = None
        self.cell_position = 0
    
    async def receive_message(self, message: AgentMessage):
        """Receive message from another agent"""
        self.messages.append(message)
        logger.debug(f"{self.agent_id} received message from {message.from_agent}")
        
        # Update context based on message
        if message.message_type == "context_update":
            self.context.update(message.content)
        elif message.message_type == "code_generated":
            self.context[f"{message.from_agent}_code"] = message.content
    
    def send_message(self, to_agent: str, message_type: str, content: Any) -> AgentMessage:
        """Send message to another agent"""
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content
        )
        return message
    
    @abstractmethod
    async def generate_code(self, problem_context: Dict[str, Any]) -> str:
        """Generate code for this agent's responsibility"""
        pass
    
    @abstractmethod
    def get_cell_type(self) -> str:
        """Get the cell type this agent manages"""
        pass
    
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent"""
        return f"You are a {self.agent_type} agent for evolutionary algorithms using DEAP framework."

