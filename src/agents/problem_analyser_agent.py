from typing import Dict, Any

from .base_agent import BaseAgent



class ProblemAnalyserAgent(BaseAgent):
    """Analyzes problem and sets up context for other agents"""
    
    def __init__(self):
        super().__init__("problem_analyser", "Problem Analyser")
        self.cell_position = 1
    
    def get_cell_type(self) -> str:
        return "problem_analysis"
    
    async def generate_code(self, problem_context: Dict[str, Any]) -> str:
        """Analyze problem and generate setup code"""
        from src.services.chatgroq_service import chatgroq_service
        
        prompt = f"""
Analyze this optimization problem and generate DEAP setup code:

Problem: {problem_context.get('title', 'Unknown')}
Description: {problem_context.get('description', '')}
Type: {problem_context.get('problem_type', 'optimization')}
Objectives: {problem_context.get('objectives', [])}
Constraints: {problem_context.get('constraints', {})}

Generate Python code that:
1. Imports necessary DEAP modules
2. Defines the problem structure
3. Sets up creator for Individual and Fitness
4. Documents the problem characteristics

Return only the Python code with comments.
"""
        
        self.generated_code = await chatgroq_service.generate_response(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1000
        )
        
        # Extract key info for other agents
        analysis = {
            "problem_type": problem_context.get('problem_type', 'optimization'),
            "objectives": problem_context.get('objectives', []),
            "constraints": problem_context.get('constraints', {}),
            "individual_structure": "list",  # Default assumption
            "optimization_direction": "maximize" if "maximize" in str(problem_context.get('objectives', [])).lower() else "minimize"
        }
        
        self.context["analysis"] = analysis
        return self.generated_code

