from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.actions import Action
from metagpt.environment import Environment
from typing import List, Dict
from metagpt.context import Context
from typing import ClassVar
from pydantic import BaseModel


## 用于总结多个网站内容的角色
class ContentSummarizationAgent(Role):
    """
    An agent that summarizes content from multiple websites based on the MetaGPT framework.
    """
    name: str = "Summa"
    profile: str = "ContentSummarizationAgent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SummarizeWebsiteContents()])

    async def _act(self) -> Message:
        """Main action loop for the summarization agent."""
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        content = await todo.run(msg.content)
        response = Message(content=content, role=self.profile, cause_by=type(todo))
        return response


class SummarizeWebsiteContents(Action):
    """Action to summarize content from multiple websites."""
    PROMPT_TEMPLATE: ClassVar[str] = """
        Summarize the content from the following websites:

        {websites_content}

        Task:


        <URL>: <保留原本的内容，但是更有利于阅读，总结>. ...

        """


    name: str = "SummarizeWebsiteContents"

    async def run(self, context: Message) -> str:
        # Parse the input dictionary from the message content
        input_data = eval(context)  # Assuming the input is a stringified dict
        websites_content = "\n".join(
            [f"{item['url']}: {item['content']}" for item in input_data]
        )
        
        prompt = self.PROMPT_TEMPLATE.format(websites_content=websites_content)
        print(prompt)
        # Simulate calling an LLM or MetaGPT's reasoning engine
        rsp = await self._aask(prompt)
        return rsp


# Encapsulated Function
async def get_website_summary(input_data: str) -> str:
    """
    Encapsulated function to summarize content from multiple websites.

    Args:
        input_data (str): A stringified dictionary with website URLs and their contents.
                        Example: "{'websites': [{'url': 'http://example1.com', 'content': 'Text'}]}"

    Returns:
        str: A formatted summary of all website contents.
    """
    context = Context()
    role = ContentSummarizationAgent(context=context)
    result = await role.run(input_data)
    return result.content  # Return the content of the Message object


# Example Usage
if __name__ == "__main__":
    import asyncio

    async def main():
        input_data = [
                {"url": "http://example1.com", "content": "This site talks about AI advancements in 2025."},
                {"url": "http://example2.com", "content": "This site discusses healthcare innovations."},
                {"url": "http://example3.com", "content": "This site covers AI and finance trends."}
            ]
        
        
        # Convert input_data to string for passing to the agent
        input_str = str(input_data)
        summary = await get_website_summary(input_str)
        print("Summary:\n", summary)

    asyncio.run(main())