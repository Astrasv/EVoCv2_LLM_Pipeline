from .base_agent import BaseAgent
from typing import Dict, Any

class FitnessFunctionAgent(BaseAgent):
    """Generates fitness evaluation functions"""
    
    def __init__(self):
        super().__init__("fitness_function", "Fitness Function")
        self.cell_position = 3
    
    def get_cell_type(self) -> str:
        return "fitness"
    
    async def generate_code(self, problem_context: Dict[str, Any]) -> str:
        """Generate fitness function code"""
        from src.services.chatgroq_service import chatgroq_service
        
        analysis = self.context.get("analysis", {})
        individual_code = self.context.get("individuals_modelling_code", "")
        
        prompt = f"""
Generate a DEAP fitness function based on:

Problem Analysis: {analysis}
Individual Structure: {individual_code[:200]}...

Objectives: {analysis.get('objectives', [])}
Constraints: {analysis.get('constraints', {})}
Optimization: {analysis.get('optimization_direction', 'maximize')}

Generate a fitness function that:
1. Takes an individual as input
2. Evaluates against the objectives
3. Handles constraints appropriately
4. Returns fitness as a tuple
5. Is DEAP-compatible

Return only the Python function code with comments.
"""
        
        self.generated_code = await chatgroq_service.generate_response(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1000
        )
        
        return self.generated_code
