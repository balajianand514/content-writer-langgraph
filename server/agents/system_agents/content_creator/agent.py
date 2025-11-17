import asyncio
import logging
from typing import List, Dict, AsyncGenerator
from server.agents.workflow_agents.azure_bing_search.agent import AzureBingSearchAgent
from server.agents.workflow_agents.web_extraction.agent import WebContentExtractorAgent
from server.agents.workflow_agents.content_creator.agent import ContentCreationAgent
from server.agents.workflow_agents.web_content_summary.agent import WebContentSummaryAgent
from server.agents.workflow_agents.azure_bing_search.types import BingSearchResponse
from autogen import Agent
from .types import WebContent


# Setup a logger for the system agent
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CACHE:Dict[str,WebContent] = {}
class ContentCreationSystemAgent(Agent):
    """
    A system agent that coordinates content creation by performing web searches, extracting content from URLs,
    and generating posts based on the gathered information.
    """

    def __init__(self, req_id: str, user: str):
        """
        Initializes the agent with a unique request ID and user identifier.

        Args:
            req_id (str): A unique identifier for the request.
            user (str): The user who is making the request.
        """
        super().__init__(name="ContentCreationSystemAgent", description="Coordinates content creation tasks.")
        self.req_id = req_id
        self.user = user

        # Instantiate other agents required for tasks
        self.azure_bing_search_agent = AzureBingSearchAgent()
        self.web_content_extractor_agent = WebContentExtractorAgent()
        self.content_creation_agent = ContentCreationAgent()
        self.web_content_summary_agent = WebContentSummaryAgent()

    async def _search_and_create_content(self, topic: str, sources: List[str]) -> AsyncGenerator[str, None]:
        """
        Orchestrates the web search, content extraction, and content creation process for a given topic and list of sources.

        Args:
            topic (str): The content topic to search for.
            sources (List[str]): List of sources (URLs or domains) to search for content.

        Yields:
            str: The results or status messages from each step of the process.
        """
        try:
            # Step 1: Web search for relevant content
            logger.info(f"[{self.req_id}] Starting web search for topic: {topic}.")
            yield f"<status>status_message</status><data>Conducting web search on: {topic}.</data>"

            bing_search_response = await self.azure_bing_search_agent.run(topic, sources)

            # Step 2: Process each search result concurrently
            logger.info(f"[{self.req_id}] Processing {len(bing_search_response)} search results.")
            yield f"<status>status_message</status><data>Analyzing web sources for content creation.</data>"

            # tasks = [
            #     self._process_search_result(topic, web_result)
            #     for response in bing_search_response
            #     for web_result in response.web_results
            # ]

            # # Run all tasks concurrently and yield the results
            # for task in tasks:
            #     async for result in task:
            #         yield result

            tasks = [
                self._create_web_content_summary(web_result)
                for response in bing_search_response
                for web_result in response.web_results
            ]

            # Run all tasks concurrently and yield the results
            for task in tasks:
                async for result in task:
                    yield result
                    
        except Exception as e:
            logger.error(f"[{self.req_id}] Error during content creation process: {str(e)}")
            # yield f"<status>error_message</status><data>An error occurred: {str(e)}</data>"

    async def _create_web_content_summary(self,web_result: Dict) -> AsyncGenerator[str, None]:
        """
        Handles the process of extracting content from a web result and generating a LinkedIn post.

        Args:
            topic (str): The content topic for which the post is being created.
            web_result (Dict): The search result (URL, title, and snippet).

        Yields:
            str: The result of the content extraction and LinkedIn post creation.
        """
        try:
            url = web_result.url
            title = web_result.title
            summary = web_result.snippet

            # Step 1: Extract content from the URL
            logger.info(f"[{self.req_id}] Extracting content from URL: {url}.")
            yield f"<event_type>STATUS</event_type><event_data>Extracting content from {title}.</event_data><source></source>"

            markdown_content = await self.web_content_extractor_agent.run(url)
            if markdown_content is not None:    
                # Step 2: Create web summary from the extracted content
                web_content_summary = await self.web_content_summary_agent.run(markdown_content)
                # yield f"<status>status_message</status><data>Creating post from {title}.</data>"

                # post_content = await self.content_creation_agent.run(topic, url, markdown_content)
                if web_content_summary is not None:
    
                    yield f"<event_type>WEB_DATA</event_type><event_data>{web_content_summary}</event_data><source>{url}</source>"

        except Exception as e:
            logger.error(f"[{self.req_id}] Error while processing {web_result.url}: {str(e)}")
            # yield f"<status>error_message</status><data>Error processing {web_result.url}: {str(e)}</data>"

    async def _process_search_result(self, topic: str, web_result: Dict) -> AsyncGenerator[str, None]:
        """
        Handles the process of extracting content from a web result and generating a LinkedIn post.

        Args:
            topic (str): The content topic for which the post is being created.
            web_result (Dict): The search result (URL, title, and snippet).

        Yields:
            str: The result of the content extraction and LinkedIn post creation.
        """
        try:
            url = web_result.url
            title = web_result.title
            summary = web_result.snippet

            # Step 1: Extract content from the URL
            logger.info(f"[{self.req_id}] Extracting content from URL: {url}.")
            yield f"<status>status_message</status><data>Extracting content from {title}.</data>"

            markdown_content = await self.web_content_extractor_agent.run(url)

            # Step 2: Create LinkedIn post content from the extracted content
            logger.info(f"[{self.req_id}] Generating LinkedIn post content for {title}.")
            yield f"<status>status_message</status><data>Creating post from {title}.</data>"

            post_content = await self.content_creation_agent.run(topic, url, markdown_content)

 
            yield f"<status>data_message</status><data>{post_content.response}</data><source>{url}</source>"

        except Exception as e:
            logger.error(f"[{self.req_id}] Error while processing {web_result.url}: {str(e)}")
            # yield f"<status>error_message</status><data>Error processing {web_result.url}: {str(e)}</data>"

    async def run(self, topic: str, sources: List[str]) -> AsyncGenerator[str, None]:
        """
        Orchestrates the entire process: web search, content extraction, and post creation.

        Args:
            topic (str): The topic for content creation.
            sources (List[str]): The sources for gathering content.

        Yields:
            str: Status updates and content results.
        """
        logger.info(f"[{self.req_id}] Starting content creation process for topic: {topic}.")
        yield f"<event_type>STATUS</event_type><event_data>Starting content creation process for topic: {topic}.</event_data><source></source>"
        # Call the main search and content creation handler
        async for result in self._search_and_create_content(topic, sources):
            yield result
                    # Final status after completion
        yield f"<event_type>WEB_DATA</event_type><event_data>Process completed successfully.</event_data><source></source>"
