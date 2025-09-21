import asyncio
import logging
import time
from typing import Optional, Dict, Any
from groq import AsyncGroq
import json

from src.config.settings import settings

logger = logging.getLogger(__name__)


class ChatGroqService:
    """Simple ChatGroq service with retry logic"""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.max_retries = 3
        self.base_delay = 1
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.1
    ) -> str:
        """Generate response from ChatGroq with retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                messages = []
                
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                
                messages.append({"role": "user", "content": prompt})
                
                logger.debug(f"ChatGroq request attempt {attempt + 1}")
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9
                )
                
                content = response.choices[0].message.content.strip()
                logger.debug(f"ChatGroq response received: {len(content)} characters")
                
                return content
                
            except Exception as e:
                logger.warning(f"ChatGroq attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"ChatGroq failed after {self.max_retries} attempts")
                    raise Exception(f"ChatGroq API failed: {str(e)}")
    
    async def generate_code(
        self, 
        problem_description: str,
        code_type: str,  # 'fitness', 'selection', 'crossover', 'mutation'
        current_code: Optional[str] = None,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate DEAP code for specific operator type"""
        
        system_prompt = f"""You are an expert evolutionary algorithm developer using the DEAP framework.
Generate Python code for {code_type} operators that follows DEAP conventions.
Return valid Python code that can be executed directly."""
        
        prompt_parts = [f"Problem: {problem_description}"]
        
        if current_code:
            prompt_parts.append(f"Current {code_type} code:\n{current_code}")
        
        if feedback:
            prompt_parts.append(f"Improvement feedback: {feedback}")
        
        prompt_parts.append(f"Generate an improved {code_type} function for DEAP:")
        
        prompt = "\n\n".join(prompt_parts)
        
        try:
            start_time = time.time()
            generated_code = await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1500,
                temperature=0.2
            )
            generation_time = time.time() - start_time
            
            return {
                "code": generated_code,
                "code_type": code_type,
                "generation_time": generation_time,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Code generation failed for {code_type}: {e}")
            return {
                "code": None,
                "code_type": code_type,
                "generation_time": 0,
                "success": False,
                "error": str(e)
            }


# Global service instance
chatgroq_service = ChatGroqService()
