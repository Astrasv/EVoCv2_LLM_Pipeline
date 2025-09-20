from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
import time
import logging
from typing import Optional

from .settings import settings

logger = logging.getLogger(__name__)


class ChatGroqClient:
    """Wrapper for ChatGroq LLM client with retry logic using LangChain"""
    
    def __init__(self, api_key: str, model: str = None):
        self.client = ChatGroq(
            groq_api_key=api_key,
            model_name=model or settings.groq_model,
            temperature=0.1,
            max_retries=settings.groq_max_retries,
            timeout=settings.groq_timeout
        )
        self.model = model or settings.groq_model
        self.max_retries = settings.groq_max_retries
        self.retry_delay = 2
        self.logger = logging.getLogger(__name__)
    
    async def complete(self, prompt: str, max_tokens: int = 4000, 
                      temperature: float = 0.1, system_prompt: Optional[str] = None) -> str:
        """Complete a prompt with retry logic"""
        for attempt in range(self.max_retries):
            try:
                messages = []
                
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                else:
                    messages.append(SystemMessage(
                        content="You are an expert evolutionary algorithm developer using DEAP framework."
                    ))
                
                messages.append(HumanMessage(content=prompt))
                
                self.logger.debug(f"Sending request to ChatGroq (attempt {attempt + 1})")
                
                response = await self.client.ainvoke(
                    messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9
                )
                
                self.logger.debug("Received response from ChatGroq")
                return response.content.strip()
                
            except Exception as e:
                self.logger.warning(f"ChatGroq API attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"ChatGroq API failed after {self.max_retries} attempts")
                    raise Exception(f"ChatGroq API failed after {self.max_retries} attempts: {str(e)}")


# Global ChatGroq client instance
chatgroq_client = ChatGroqClient(api_key=settings.groq_api_key)