import logging
from typing import Optional
from autogen import AssistantAgent
from server.setting import SETTINGS
from .prompt import CONTENT_SUMMARY_SYSTEM_PROMPT, CONTENT_SUMMARY_HUMAN_PROMPT
import json
from .types import WebContentSummary
logger = logging.getLogger(__name__)

class WebContentSummaryAgent(AssistantAgent):
    """
    A web content summary agent that processes and summarizes web content into a markdown format.
    It retrieves content, processes it, and generates a concise markdown summary with key points.
    """
    
    def __init__(self):
        """
        Initializes the WebContentSummaryAgent with necessary configurations and system messages.
        """
        super().__init__(name="Web Content Summary Agent", 
                         system_message=CONTENT_SUMMARY_SYSTEM_PROMPT, 
                         llm_config=SETTINGS.llm_config_list[0])
        
    async def run(self, web_content: Optional[str] = None) -> str:
        """
        Processes the provided web content and generates a concise markdown summary.

        Args:
            web_content (Optional[str]): The HTML or raw content to summarize. Defaults to None.

        Returns:
            str: A markdown-formatted summary or an error message in HTML format.
        """
        if not web_content:
            logger.error("No web content provided.")
            return None

        # Format the content into a prompt suitable for the assistant's summary generation.
        prompt = CONTENT_SUMMARY_HUMAN_PROMPT.format(data=web_content)

        try:
            # Request the assistant to generate a summary in markdown format.
            response = await self.a_generate_reply(messages=[{"content": prompt, "role": "user"}])

            return response

        except Exception as e:
            logger.error(f"Error generating markdown content: {e}")
            return {"error": "Unexpected error occurred during content creation", "details": str(e)}

    