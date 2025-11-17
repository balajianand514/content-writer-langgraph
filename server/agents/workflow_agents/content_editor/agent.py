from autogen import AssistantAgent, UserProxyAgent
from server.setting import SETTINGS
from typing import Dict
from .prompt import (
    CONTENT_EDITOR_SYSTEM_PROMPT,
    CONTENT_EDITOR_HUMAN_PROMPT,
    CONTENT_EDITOR_REFLECTION_PROMPT,
)
from autogen.cache import Cache
from .types import ContentEditingResponse  # Updated to reflect 'Editing' terminology


class ContentEditorAgent(AssistantAgent):
    """
    The ContentEditorAgent is responsible for refining content based on user feedback.
    It coordinates the content generation, reflection, and critique process using multiple agents.
    """

    def __init__(self, temperature: float = 0.7, max_turns: int = 1):
        """
        Initializes the ContentEditorAgent with system prompts, agent configurations, and proxy setup.

        Args:
            temperature (float): Creativity level for the agents. Default is 0.7.
            max_turns (int): Maximum turns for the user proxy agent. Default is 2.
        """
        super().__init__(name="Content Editor Agent")

        # Define LLM configurations
        self.llm_config = {
            "timeout": 600,
            "cache_seed": 41,
            "config_list": SETTINGS.llm_config_list,
            "temperature": temperature,
        }
        self.max_turns = max_turns

        # Initialize Writing Assistant for content editing
        self.editing_assistant = AssistantAgent(
            name="editing_assistant",
            system_message=CONTENT_EDITOR_SYSTEM_PROMPT,
            llm_config=self.llm_config,
        )

        # Initialize Reflection Assistant for critique and recommendations
        self.reflection_assistant = AssistantAgent(
            name="reflection_assistant",
            system_message=CONTENT_EDITOR_REFLECTION_PROMPT,
            llm_config=self.llm_config,
        )

        # User Proxy to facilitate communication between agents
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=5,
            code_execution_config=False,
        )

        # Register reflection step within the content editing process
        nested_chat_queue = [
            {
                "recipient": self.reflection_assistant,
                "message": self.reflection_message,
                "max_turns": self.max_turns,
            }
        ]
        self.user_proxy.register_nested_chats(
            nested_chat_queue,
            trigger=self.editing_assistant,
        )

    def reflection_message(self, recipient, messages, sender, config) -> str:
        """
        Extracts and returns the latest message content to be used for reflection.

        Args:
            recipient (AssistantAgent): The agent that will provide critique.
            messages (list): List of messages exchanged.
            sender (AssistantAgent): The agent that generated the content.
            config (dict): Configuration parameters for the reflection process.

        Returns:
            str: Latest message content from the sender.
        """
        if not messages:
            raise ValueError("No messages available for reflection.")
        
        last_message = recipient.chat_messages_for_summary(sender)
        if not last_message or not isinstance(last_message, list):
            raise ValueError("Invalid message format for reflection.")
        
        return last_message[-1].get("content", "No content available for reflection.")

    async def run(self, user_feedback: str, post_content: str) -> ContentEditingResponse:
        """
        Executes the content editing and reflection process in two steps.

        Args:
            user_feedback (str): User feedback.
            post_content (str): post_content.

        Returns:
            ContentEditingResponse: A structured response containing the result.
        """
        try:
            # Step 1: Content Editing (with cache)
            with Cache.disk(cache_seed=42) as content_cache:
                response = self.user_proxy.initiate_chat(
                    self.editing_assistant,
                    message=CONTENT_EDITOR_HUMAN_PROMPT.format(content=post_content, user_feedback=user_feedback),
                    max_turns=self.max_turns,
                    cache=content_cache,
                )
            
            if not response:
                raise ValueError("No response generated from writing assistant.")
 
            # prompt = CONTENT_EDITOR_HUMAN_PROMPT.format(content=post_content, user_feedback=user_feedback)
            # refined_post=  await self.editing_assistant.a_generate_reply(messages=[{"content": prompt, "role": "user"}])

            # Return structured content editing response with critique
            return ContentEditingResponse(
                status="success",
                response=response.summary,
            )

        except Exception as e:
            # Log and return error response
            error_message = f"Content editing process failed: {str(e)}"
            return ContentEditingResponse(
                status="error",
                message=error_message,
            )
