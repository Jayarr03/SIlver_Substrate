"""Agent orchestrator for sequential multi-agent threat modeling execution."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from .agents import AgentPersona, get_agent_set
from .models import ComponentInput
from .openai_client import OpenAIResponsesClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentContext:
    """Accumulated context passed between agents in the pipeline."""

    component: ComponentInput
    agent_outputs: dict[str, Any]  # Maps agent name to its JSON output
    
    def add_output(self, agent_name: str, output: dict[str, Any]) -> "AgentContext":
        """Return a new context with an additional agent output."""
        new_outputs = {**self.agent_outputs, agent_name: output}
        return AgentContext(component=self.component, agent_outputs=new_outputs)
    
    def to_context_payload(self) -> dict[str, Any]:
        """Convert context to JSON payload for next agent."""
        return {
            "component": self.component.to_prompt_payload(),
            "previous_agent_outputs": self.agent_outputs,
        }


@dataclass(frozen=True)
class AgentExecutionResult:
    """Result from executing a single agent."""

    agent_name: str
    success: bool
    output: dict[str, Any] | None
    error: str | None = None


class AgentOrchestrator:
    """Sequential execution of specialized threat modeling agents."""

    def __init__(
        self,
        client: OpenAIResponsesClient,
        agent_mode: str = "minimal",
        model: str | None = None,
    ):
        """Initialize orchestrator with OpenAI client and agent mode.
        
        Args:
            client: OpenAI client for making API calls
            agent_mode: 'minimal' (6 agents) or 'full' (12 agents)
            model: Optional model override
        """
        self.client = client
        self.agent_mode = agent_mode
        self.model = model
        self.agents = get_agent_set(agent_mode)
        
    def execute_agent(
        self,
        agent: AgentPersona,
        context: AgentContext,
    ) -> AgentExecutionResult:
        """Execute a single agent with accumulated context.
        
        Args:
            agent: Agent persona to execute
            context: Accumulated context from previous agents
            
        Returns:
            Execution result with agent output or error
        """
        try:
            logger.info(f"Executing agent: {agent.name} ({agent.role})")
            
            # Build messages for this agent
            context_payload = context.to_context_payload()
            
            # System message with agent's specialized prompt
            system_message = {
                "role": "system",
                "content": agent.system_prompt,
            }
            
            # User message with component and previous outputs
            user_message = {
                "role": "user",
                "content": json.dumps(context_payload, indent=2, sort_keys=True),
            }
            
            messages = (system_message, user_message)
            
            # Call OpenAI with agent's schema
            from .models import PipelineRequest
            
            request = PipelineRequest(
                component=context.component,
                messages=messages,
                response_schema=agent.output_schema,
                model=self.model,
            )
            
            output = self.client.generate(request)
            
            logger.info(f"Agent {agent.name} completed successfully")
            return AgentExecutionResult(
                agent_name=agent.name,
                success=True,
                output=output,
            )
            
        except Exception as e:
            logger.error(f"Agent {agent.name} failed: {str(e)}")
            return AgentExecutionResult(
                agent_name=agent.name,
                success=False,
                output=None,
                error=str(e),
            )
    
    def execute_pipeline(
        self,
        component: ComponentInput,
    ) -> tuple[dict[str, Any], list[AgentExecutionResult]]:
        """Execute full agent pipeline sequentially.
        
        Args:
            component: Component to analyze
            
        Returns:
            Tuple of (final accumulated outputs, execution results for each agent)
        """
        logger.info(
            f"Starting {self.agent_mode} agent pipeline with {len(self.agents)} agents"
        )
        
        # Initialize context with component input
        context = AgentContext(component=component, agent_outputs={})
        execution_results = []
        
        # Execute each agent sequentially
        for agent in self.agents:
            result = self.execute_agent(agent, context)
            execution_results.append(result)
            
            if result.success and result.output:
                # Add this agent's output to context for next agent
                context = context.add_output(result.agent_name, result.output)
            else:
                # Agent failed - log warning and continue with partial results
                logger.warning(
                    f"Agent {agent.name} failed, continuing with partial results"
                )
        
        logger.info(
            f"Pipeline complete. {len([r for r in execution_results if r.success])}/{len(self.agents)} agents succeeded"
        )
        
        return context.agent_outputs, execution_results
    
    def get_failed_agents(
        self, execution_results: list[AgentExecutionResult]
    ) -> list[str]:
        """Return names of agents that failed during execution."""
        return [r.agent_name for r in execution_results if not r.success]
