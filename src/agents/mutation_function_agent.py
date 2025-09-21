from .base_agent import BaseAgent
from typing import Dict, Any

class MutationFunctionAgent(BaseAgent):
    """Generates mutation functions"""
    
    def __init__(self):
        super().__init__("mutation_function", "Mutation Function")
        self.cell_position = 5
    
    def get_cell_type(self) -> str:
        return "mutation"
    
    async def generate_code(self, problem_context: Dict[str, Any]) -> str:
        """Generate mutation function code"""
        from src.services.chatgroq_service import chatgroq_service
        
        analysis = self.context.get("analysis", {})
        individual_code = self.context.get("individuals_modelling_code", "")
        
        prompt = f"""
Generate a DEAP mutation function based on:

Problem Type: {analysis.get('problem_type', 'optimization')}
Individual Structure: {individual_code[:200]}...
Constraints: {analysis.get('constraints', {})}

Generate a mutation function that:
1. Takes an individual as input
2. Applies random modifications
3. Maintains solution feasibility
4. Handles problem constraints
5. Returns modified individual as tuple

Return only the Python function code with comments.
"""
        
        self.generated_code = await chatgroq_service.generate_response(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=800
        )
        
        return self.generated_code

