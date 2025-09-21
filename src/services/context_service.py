import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ContextService:
    """Simple context management for ChatGroq token optimization"""
    
    def __init__(self, max_tokens: int = 3000):
        self.max_tokens = max_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """Simple token estimation (roughly 4 characters per token)"""
        return len(text) // 4
    
    def compress_context(self, full_context: str) -> str:
        """Simple context compression when approaching token limits"""
        
        estimated_tokens = self.estimate_tokens(full_context)
        
        if estimated_tokens <= self.max_tokens:
            return full_context
        
        # Simple compression: take first and last parts
        lines = full_context.split('\n')
        
        if len(lines) <= 10:
            # If short, just truncate
            target_chars = self.max_tokens * 3  # Conservative estimate
            return full_context[:target_chars] + "\n[...context truncated...]"
        
        # Take first 25% and last 25% of lines
        first_quarter = len(lines) // 4
        last_quarter = len(lines) - (len(lines) // 4)
        
        compressed_lines = (
            lines[:first_quarter] + 
            ["\n[...middle context compressed...]\n"] + 
            lines[last_quarter:]
        )
        
        compressed = '\n'.join(compressed_lines)
        
        logger.debug(f"Compressed context from {estimated_tokens} to ~{self.estimate_tokens(compressed)} tokens")
        
        return compressed
    
    def build_agent_context(
        self,
        problem_description: str,
        agent_type: str,
        current_code: Optional[str] = None,
        chat_history: Optional[str] = None,
        feedback: Optional[str] = None
    ) -> Dict[str, str]:
        """Build context for agent code generation"""
        
        # Build context parts
        context_parts = []
        
        context_parts.append(f"PROBLEM DESCRIPTION:\n{problem_description}")
        
        if current_code:
            context_parts.append(f"CURRENT {agent_type.upper()} CODE:\n{current_code}")
        
        if feedback:
            context_parts.append(f"USER FEEDBACK:\n{feedback}")
        
        if chat_history:
            # Compress chat history if too long
            compressed_history = self.compress_context(chat_history)
            context_parts.append(f"RECENT CONVERSATION:\n{compressed_history}")
        
        full_context = "\n\n".join(context_parts)
        
        # Compress if needed
        final_context = self.compress_context(full_context)
        
        # Build system prompt
        system_prompt = f"""You are a {agent_type} agent for evolutionary algorithms using DEAP framework.
Generate Python code that follows DEAP conventions and best practices.
Focus on writing clean, functional code that addresses the specific requirements."""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": final_context
        }


# Global service instance
context_service = ContextService()