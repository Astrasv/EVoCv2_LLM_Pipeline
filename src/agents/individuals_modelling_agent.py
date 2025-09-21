from .base_agent import BaseAgent
from typing import Dict, Any

class IndividualsModellingAgent(BaseAgent):
    """Models individual representation and initialization"""
    
    def __init__(self):
        super().__init__("individuals_modelling", "Individuals Modelling")
        self.cell_position = 2
    
    def get_cell_type(self) -> str:
        return "individual_representation"
    
    async def generate_code(self, problem_context: Dict[str, Any]) -> str:
        """Generate individual representation and initialization code"""
        from src.services.chatgroq_service import chatgroq_service
        
        analysis = self.context.get("analysis", {})
        
        prompt = f"""
Based on this problem analysis, generate DEAP individual representation code:

Problem Type: {analysis.get('problem_type', 'optimization')}
Objectives: {analysis.get('objectives', [])}
Constraints: {analysis.get('constraints', {})}

Generate Python code that:
1. Defines individual representation (list, tree, etc.)
2. Creates initialization function
3. Registers individual creation in toolbox
4. Handles problem-specific constraints

Focus on the individual structure and initialization only.
Return only the Python code with comments.
"""
        
        self.generated_code = await chatgroq_service.generate_response(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=800
        )
        
        return self.generated_code

