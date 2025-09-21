"""Simple prompt templates for different agent types"""

AGENT_PROMPTS = {
    "fitness": """
Generate a DEAP-compatible fitness function for this optimization problem.
The function should:
1. Take an individual as input
2. Evaluate the individual against the problem objectives
3. Return a tuple of fitness values
4. Handle constraints appropriately

Return only the Python function code, no explanations.
""",
    
    "selection": """
Generate a DEAP-compatible selection function for this optimization problem.
The function should:
1. Take a population and selection size as input
2. Select individuals based on fitness
3. Return the selected individuals
4. Use appropriate selection pressure

Return only the Python function code, no explanations.
""",
    
    "crossover": """
Generate a DEAP-compatible crossover function for this optimization problem.
The function should:
1. Take two parent individuals as input
2. Create offspring through recombination
3. Maintain individual structure integrity
4. Return modified individuals

Return only the Python function code, no explanations.
""",
    
    "mutation": """
Generate a DEAP-compatible mutation function for this optimization problem.
The function should:
1. Take an individual as input
2. Apply random modifications
3. Maintain solution feasibility
4. Return the modified individual as a tuple

Return only the Python function code, no explanations.
"""
}


def get_agent_prompt(agent_type: str) -> str:
    """Get prompt template for agent type"""
    return AGENT_PROMPTS.get(agent_type, AGENT_PROMPTS["fitness"])