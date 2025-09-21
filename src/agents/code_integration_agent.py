from .base_agent import BaseAgent
from typing import Dict, Any

class CodeIntegrationAgent(BaseAgent):
    """Integrates all code and creates DEAP toolbox registration"""
    
    def __init__(self):
        super().__init__("code_integration", "Code Integration and Validation")
        self.cell_position = 7
    
    def get_cell_type(self) -> str:
        return "toolbox_registration"
    
    async def generate_code(self, problem_context: Dict[str, Any]) -> str:
        """Generate complete DEAP toolbox registration code"""
        from src.services.chatgroq_service import chatgroq_service
        
        # Get all the generated code from other agents
        individual_code = self.context.get("individuals_modelling_code", "")
        fitness_code = self.context.get("fitness_function_code", "")
        crossover_code = self.context.get("crossover_function_code", "")
        mutation_code = self.context.get("mutation_function_code", "")
        selection_code = self.context.get("selection_strategy_code", "")
        
        prompt = f"""
Create DEAP toolbox registration code that integrates all the generated functions:

Individual Code:
{individual_code[:300]}...

Fitness Code:
{fitness_code[:300]}...

Crossover Code:
{crossover_code[:300]}...

Mutation Code:
{mutation_code[:300]}...

Selection Code:
{selection_code[:300]}...

Generate code that:
1. Creates DEAP toolbox instance
2. Registers all the functions properly
3. Sets up population creation
4. Adds any missing imports
5. Provides a complete working toolbox

Return only the Python code with comments.
"""
        
        self.generated_code = await chatgroq_service.generate_response(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1200
        )
        
        return self.generated_code
