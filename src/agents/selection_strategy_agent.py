from .base_agent import BaseAgent
from typing import Dict, Any

class SelectionStrategyAgent(BaseAgent):
    """Generates selection strategy functions"""
    
    def __init__(self):
        super().__init__("selection_strategy", "Selection Strategy")
        self.cell_position = 6
    
    def get_cell_type(self) -> str:
        return "selection"
    
    async def generate_code(self, problem_context: Dict[str, Any]) -> str:
        """Generate selection function code"""
        from src.services.chatgroq_service import chatgroq_service
        analysis = self.context.get("analysis", {})
        fitness_code = self.context.get("fitness_function_code", "")
        
        prompt = f"""
Generate a DEAP selection function based on:

Problem Type: {analysis.get('problem_type', 'optimization')}
Optimization Direction: {analysis.get('optimization_direction', 'maximize')}
Fitness Function: {fitness_code[:200]}...

Generate a selection function that:
1. Takes population and selection size
2. Selects individuals based on fitness
3. Uses appropriate selection pressure
4. Handles the optimization direction correctly
5. Returns selected individuals

Return only the Python function code with comments.
"""
        
        self.generated_code = await chatgroq_service.generate_response(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=800
        )
        
        return self.generated_code
