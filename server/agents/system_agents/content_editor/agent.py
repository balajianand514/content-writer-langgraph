import asyncio
import logging
from typing import AsyncGenerator
from server.agents.workflow_agents.content_editor.agent import ContentEditorAgent
from autogen import Agent


# Setup a logger for the system agent
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ContentEditorSystemAgent(Agent):
    """
    A system agent that coordinates content editing by refining posts based on user feedback
    and ensuring alignment with organizational goals.
    """

    def __init__(self, req_id: str, user: str):
        """
        Initializes the agent with a unique request ID and user identifier.

        Args:
            req_id (str): A unique identifier for the request.
            user (str): The user who is making the request.
        """
        super().__init__(name="ContentEditorSystemAgent", description="Coordinates content editing tasks.")
        self.req_id = req_id
        self.user = user

        # Instantiate the content editing agent
        self.content_editing_agent = ContentEditorAgent()

    async def run(self, user_feedback: str, post_content: str) -> AsyncGenerator[str, None]:
        """
        Orchestrates the content editing process: refining posts based on feedback.

        Args:
            user_feedback (str): The feedback provided by the user for improving the content.
            post_content (str): The original post content that requires editing.

        Yields:
            str: Status updates and the revised content in Markdown format.
        """
        logger.info(f"Content editing initiated by user: {self.user}, Request ID: {self.req_id}")
        
        try:
            # Log the input details
            logger.debug(f"Original post content: {post_content}")
            logger.debug(f"User feedback: {user_feedback}")
            
            # Step 1: Refine the post using the content editing agent
            revised_post = await self.content_editing_agent.run(
                user_feedback=user_feedback,
                post_content=post_content,
            )
            
 
            yield f"<status>data_message</status><data>{revised_post.response}</data>"

        except Exception as e:
            error_message = f"An error occurred during content editing: {str(e)}"
            logger.exception(error_message)
            yield f"<status>error</status><message>{error_message}</message>"


 