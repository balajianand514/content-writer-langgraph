from autogen import AssistantAgent, UserProxyAgent
from server.setting import SETTINGS
from typing import Dict
from .prompt import (
    CONTENT_WRITER_SYSTEM_PROMPT,
    CONTENT_WRITER_HUMAN_PROMPT,
    CONTENT_WRITER_REFLECTION_PROMPT,
)
from autogen.cache import Cache
from .types import ContentCreationResponse


class ContentCreationAgent(AssistantAgent):
    """
    The ContentCreationAgent is responsible for generating content based on a given topic, URL, and markdown content.
    It uses two agents, one for writing content and another for providing critique and recommendations.
    """

    def __init__(self, temperature: float = 0.7, max_turns: int = 2):
        """
        Initializes the ContentCreationAgent with system prompts, agent configurations, and proxy setup.

        Args:
            temperature (float): The creativity level for the agents. Default is 0.7.
            max_turns (int): Maximum turns for the user proxy agent. Default is 2.
        """
        super().__init__(name="Content Creation Agent")

        # Define the LLM configurations
        self.llm_config = {
            "timeout": 600,
            "cache_seed": 41,
            "config_list": SETTINGS.llm_config_list,
            "temperature": temperature,
        }
        self.max_turns = max_turns

        # Initialize writing assistant agent
        self.writing_assistant = AssistantAgent(
            name="writing_assistant",
            system_message=CONTENT_WRITER_SYSTEM_PROMPT,
            llm_config=self.llm_config,
        )

        # Initialize reflection assistant agent
        self.reflection_assistant = AssistantAgent(
            name="reflection_assistant",
            system_message=CONTENT_WRITER_REFLECTION_PROMPT,
            llm_config=self.llm_config,
        )

        # Initialize user proxy agent
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=5,
            code_execution_config=False,
        )

        # Register nested chats for reflection assistant
        nested_chat_queue = [
            {
                "recipient": self.reflection_assistant,
                "message": self.reflection_message,
                "max_turns": self.max_turns,
            }
        ]

        self.user_proxy.register_nested_chats(
            nested_chat_queue,
            trigger=self.writing_assistant,
        )

    def reflection_message(self, recipient, messages, sender, config) -> str:
        """
        Returns the latest message content from the sender to be used in reflection.

        Args:
            recipient (AssistantAgent): The agent that will provide critique.
            messages (list): List of messages exchanged so far.
            sender (AssistantAgent): The agent that generated the content.
            config (dict): Configuration parameters for the reflection process.

        Returns:
            str: The latest content from the sender.
        """
        if not messages:
            raise ValueError("No messages available for reflection.")

        last_message = recipient.chat_messages_for_summary(sender)
        if not last_message or not isinstance(last_message, list):
            raise ValueError("Invalid message format for reflection.")

        return last_message[-1].get("content", "No content available for reflection.")

    async def run(self, topic: str, url: str, markdown_content: str) -> ContentCreationResponse:
        """
        Executes the content creation and reflection process in two steps.

        Args:
            topic (str): The topic to write about.
            url (str): The URL associated with the content.
            markdown_content (str): The markdown content to be used for generating the content.

        Returns:
            ContentCreationResponse: A structured response using Pydantic.
        """
        try:
            # Step 1: Content Generation
            with Cache.disk(cache_seed=42) as content_cache:
                response = self.user_proxy.initiate_chat(
                    self.writing_assistant,
                    message=CONTENT_WRITER_HUMAN_PROMPT.format(topic=topic, url=url, content=markdown_content),
                    max_turns=self.max_turns,
                    cache=content_cache,
                )
 

            response = response.summary
            # Return structured response
            return ContentCreationResponse(
                status="success",
                response=response
            )

        except Exception as e:
            # Return error response
            return ContentCreationResponse(
                status="error",
                message=str(e),
            )
