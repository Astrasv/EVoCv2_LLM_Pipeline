from .base_agent import BaseAgent
from typing import Dict, Any

class CrossoverFunctionAgent(BaseAgent):
    """Generates crossover/recombination functions"""
    
    def __init__(self):
        super().__init__("crossover_function", "Crossover Function")
        self.cell_position = 4
    
    def get_cell_type(self) -> str:
        return "crossover"
    
    async def generate_code(self, problem_context: Dict[str, Any]) -> str:
        """Generate crossover function code"""
        from src.services.chatgroq_service import chatgroq_service
        
        analysis = self.context.get("analysis", {})
        individual_code = self.context.get("individuals_modelling_code", "")
        
        prompt = f"""
Generate a DEAP crossover function based on:

Problem Type: {analysis.get('problem_type', 'optimization')}
Individual Structure: {individual_code[:200]}...
Constraints: {analysis.get('constraints', {})}

Generate a crossover function that:
1. Takes two parent individuals
2. Creates offspring through recombination
3. Maintains individual structure integrity
4. Handles problem constraints
5. Returns modified individuals

Return only the Python function code with comments.
"""
        
        self.generated_code = await chatgroq_service.generate_response(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=800
        )
        
        return self.generated_code
