from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.context import Context
from typing import Any, Dict, Optional, Union
import asyncio
from src.utils.Recommend import RecommendationAgent  # Replace with actual module 

class AgentCaller:
    """
    A generic class to call and interact with MetaGPT-based agents.
    
    Attributes:
        agent_class: The agent class to instantiate (must inherit from Role)
        context: MetaGPT Context object for agent execution
        agent: Instantiated agent instance
    """
    
    def __init__(self, agent_class: type, context: Optional[Context] = None, **kwargs):
        """
        Initialize the AgentCaller with an agent class and optional context.
        
        Args:
            agent_class: The agent class to instantiate (subclass of Role)
            context: Optional MetaGPT Context object, creates new if None
            **kwargs: Additional keyword arguments for agent initialization
        """
        if not issubclass(agent_class, Role):
            raise ValueError("agent_class must be a subclass of Role")
            
        self.agent_class = agent_class
        self.context = context if context is not None else Context()
        self.agent = agent_class(context=self.context, **kwargs)
        self.last_result = None
        
    async def call(self, input_data: Union[str, Dict, Message]) -> str:
        """
        Call the agent with input data and get the response.
        
        Args:
            input_data: Input data (string, dict, or Message object)
            
        Returns:
            str: Agent's response content
        """
        # Convert input to Message if it's not already
        if isinstance(input_data, str):
            message = Message(content=input_data)
        elif isinstance(input_data, dict):
            message = Message(content=str(input_data))
        elif isinstance(input_data, Message):
            message = input_data
        else:
            raise ValueError("Input must be string, dict, or Message object")
            
        # Run the agent and store result
        result = await self.agent.run(message)
        self.last_result = result
        return result.content if hasattr(result, 'content') else str(result)
    
    async def get_last_result(self) -> Optional[str]:
        """
        Get the last computation result.
        
        Returns:
            Optional[str]: Last result or None if no previous calls
        """
        return self.last_result.content if self.last_result else None
    
    def reset(self):
        """
        Reset the agent by reinitializing it with the same context.
        """
        self.agent = self.agent_class(context=self.context)
        self.last_result = None

# Example Usage with RecommendationAgent
async def example_usage():
    # Import the RecommendationAgent from your code
    
    # Initialize the caller with RecommendationAgent
    caller = AgentCaller(RecommendationAgent)
    
    # Example input
    old_content = "The website previously had information about AI and machine learning."
    new_content = "The website now focuses on AI applications in healthcare and finance."
    keywords = ["AI", "healthcare"]
    
    input_data = f"Old Content: {old_content}\nNew Content: {new_content}\nKeywords: {keywords}"
    
    # Call the agent
    result = await caller.call(input_data)
    print("Recommendation Result:", result)
    
    # Get last result (optional)
    last_result = await caller.get_last_result()
    print("Last Result:", last_result)
    
    # Reset if needed
    caller.reset()

if __name__ == "__main__":
    asyncio.run(example_usage())