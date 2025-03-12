from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.actions import Action
from metagpt.environment import Environment
from typing import List, Dict
from metagpt.context import Context
from typing import ClassVar
from pydantic import BaseModel



## 用于推荐的角色


class RecommendationAgent(Role):
    """
    A recommendation agent based on MetaGPT framework.
    This agent analyzes changes in web content and generates recommendations based on user-defined keywords.
    """
    name:str = "Zata"
    profile: str = "RecommendationAgent"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeContentChange(), GenerateRecommendation()])

    async def _act(self) -> Message:
        """Main action loop for the recommendation agent."""
        # Get the latest message from the environment
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        content = await todo.run(msg.content)
        response = Message(content=content, role=self.profile,cause_by=type(todo))
        return response


class AnalyzeContentChange(Action):
    """Action to analyze changes between two versions of web content."""
    PROMPT_TEMPLATE:ClassVar[str]  = """
    Analyze the differences between the old content and the new content.

    Task: Identify significant changes related to the user's keywords and summarize them.
    {context}
    """
    name:str = "AnalyzeContentChange"

    async def run(self, context: Message) -> Message:
        prompt = self.PROMPT_TEMPLATE.format(context = context)
        # Simulate calling an LLM or MetaGPT's reasoning engine
        rsp = await self._aask(prompt)
        
        return rsp
    



class GenerateRecommendation(Action):
    """Action to generate recommendations based on the analysis result."""
    PROMPT_TEMPLATE:ClassVar[str]= """
    Based on the analysis result, generate personalized recommendations for the user.
    Analysis Result: {analysis_result}
    User Keywords: ai
    Task: Provide actionable suggestions that align with the user's interests.
    """

    async def run(self, context: Message) -> Message:
        data = context
        prompt = self.PROMPT_TEMPLATE.format(
            analysis_result=data,
        )
        # Simulate calling an LLM or MetaGPT's reasoning engine
        rsp = await self._aask(prompt)
        return rsp


# Encapsulated Function
async def get_recommendation(prompt) -> str:
    """
    Encapsulated function to get recommendations based on web content changes and user keywords.

    Args:
        old_content (str): The original version of the web content.
        new_content (str): The updated version of the web content.
        keywords (List[str]): User-defined keywords for filtering significant changes.

    Returns:
        str: Generated recommendation.
    """
    # Initialize environment and agent
    context = Context()
    role = RecommendationAgent(context=context)
    result = await role.run(prompt)
    print (result)
    # Run the agent and get the recommendation
    return result


# Example Usage
if __name__ == "__main__":
    import asyncio

    async def main():
        old_content = "The website previously had information about AI and machine learning."
        new_content = "The website now focuses on AI applications in healthcare and finance."
        keywords = ["AI", "healthcare"]
        
        content = f"Old Content: {old_content}\nNew Content: {new_content}\nKeywords: {keywords}"

        recommendation = await get_recommendation(content)
        print("Recommendation:", recommendation)

    asyncio.run(main())