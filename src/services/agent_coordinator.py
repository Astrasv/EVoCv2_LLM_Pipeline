import asyncio
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from src.agents.base_agent import BaseAgent, AgentMessage
from src.agents.problem_analyser_agent import ProblemAnalyserAgent
from src.agents.individuals_modelling_agent import IndividualsModellingAgent
from src.agents.fitness_function_agent import FitnessFunctionAgent
from src.agents.crossover_function_agent import CrossoverFunctionAgent
from src.agents.mutation_function_agent import MutationFunctionAgent
from src.agents.selection_strategy_agent import SelectionStrategyAgent
from src.agents.code_integration_agent import CodeIntegrationAgent
from src.services.cell_management_service import CellManagementService

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordinates multi-agent execution following the specified flow"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.cell_service = CellManagementService(db_session)
        
        # Initialize agents in execution order
        self.agents = {
            "problem_analyser": ProblemAnalyserAgent(),
            "individuals_modelling": IndividualsModellingAgent(),
            "fitness_function": FitnessFunctionAgent(),
            "crossover_function": CrossoverFunctionAgent(),
            "mutation_function": MutationFunctionAgent(),
            "selection_strategy": SelectionStrategyAgent(),
            "code_integration": CodeIntegrationAgent(),
        }
        
        # Define execution flow based on your diagram
        self.execution_flow = [
            "problem_analyser",
            "individuals_modelling",
            "fitness_function",
            "crossover_function",
            "mutation_function",
            "selection_strategy",
            "code_integration"
        ]
    
    async def coordinate_agents(self, notebook_id: UUID, problem_context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate all agents following the communication flow"""
        
        results = {}
        
        try:
            logger.info(f"Starting agent coordination for notebook {notebook_id}")
            
            for i, agent_id in enumerate(self.execution_flow):
                logger.info(f"=== Executing agent {i+1}/7: {agent_id} ===")
                agent = self.agents[agent_id]
                
                # Generate code
                logger.info(f"Generating code for {agent_id}")
                try:
                    generated_code = await agent.generate_code(problem_context)
                    logger.info(f"Code generation successful for {agent_id}: {len(generated_code)} characters")
                except Exception as e:
                    logger.error(f"Code generation failed for {agent_id}: {e}")
                    raise Exception(f"Agent {agent_id} code generation failed: {e}")
                
                # Store code in appropriate cell  
                logger.info(f"Storing code in cell for {agent_id}")
                try:
                    cell_result = await self.cell_service.update_or_create_cell(
                        notebook_id=notebook_id,
                        cell_type=agent.get_cell_type(),
                        code=generated_code,
                        agent_id=agent.agent_id,
                        position=agent.cell_position
                    )
                    logger.info(f"Cell storage successful for {agent_id}: {cell_result}")
                except Exception as e:
                    logger.error(f"Cell storage failed for {agent_id}: {e}")
                    raise Exception(f"Agent {agent_id} cell storage failed: {e}")
                
                results[agent_id] = {
                    "agent_id": agent.agent_id,
                    "cell_id": cell_result["cell_id"],
                    "code": generated_code,
                    "cell_type": agent.get_cell_type(),
                    "success": True
                }
                
                # Pass context to next agents
                logger.info(f"Propagating context from {agent_id}")
                await self._propagate_context_to_remaining_agents(i, agent_id, generated_code)
                
                # Small delay for better logging
                await asyncio.sleep(0.1)
            
            logger.info("Agent coordination completed successfully")
            return {
                "success": True,
                "results": results,
                "message": "All agents executed successfully"
            }
            
        except Exception as e:
            logger.error(f"Agent coordination failed: {e}")
            import traceback
            traceback.print_exc()  # This will show the full stack trace
            return {
                "success": False,
                "results": results,
                "error": str(e),
                "message": f"Agent coordination failed: {str(e)}"
            }
    
    async def _propagate_context_to_remaining_agents(self, current_index: int, agent_id: str, generated_code: str):
        """Propagate context to remaining agents in the flow"""
        
        # Send generated code to remaining agents
        remaining_agents = self.execution_flow[current_index + 1:]
        
        for next_agent_id in remaining_agents:
            next_agent = self.agents[next_agent_id]
            
            # Create message with generated code
            message = AgentMessage(
                from_agent=agent_id,
                to_agent=next_agent_id,
                message_type="code_generated",
                content=generated_code
            )
            
            # Send message to next agent
            await next_agent.receive_message(message)
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {}
        
        for agent_id, agent in self.agents.items():
            status[agent_id] = {
                "agent_type": agent.agent_type,
                "cell_type": agent.get_cell_type(),
                "position": agent.cell_position,
                "has_generated_code": agent.generated_code is not None,
                "message_count": len(agent.messages),
                "context_keys": list(agent.context.keys())
            }
        
        return status
