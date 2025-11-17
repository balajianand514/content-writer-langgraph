import httpx
from bs4 import BeautifulSoup
import asyncio
import logging
from typing import List, Dict
from autogen import AssistantAgent
from server.setting import SETTINGS
import json
from .prompt import HTML_CONTENT_SYSTEM_PROMPT, HTML_CONTENT_HUMAN_PROMPT

logger = logging.getLogger(__name__)

class WebContentExtractorAgent(AssistantAgent):
    """
    This agent is responsible for fetching and processing web content.
    It retrieves content from a given URL and generates a markdown version of it.
    """
    
    def __init__(self):
        """
        Initializes the WebContentExtractorAgent with necessary configurations
        and system messages for the assistant.
        """
        super().__init__(name="Web Content Extraction Agent", system_message=HTML_CONTENT_SYSTEM_PROMPT, llm_config=SETTINGS.llm_config_list[0])
        self.timeout = 10  # Timeout in seconds for HTTP requests
        
    async def fetch_content(self, url: str) -> str:
        """
        Fetches the content from a web URL and extracts the main body text.

        Args:
            url (str): The URL from which to fetch content.

        Returns:
            str: The cleaned HTML content of the page, or an error message if fetching fails.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
                return self.clean_content(BeautifulSoup(response.content, 'html.parser').body)
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def clean_content(self, body: BeautifulSoup) -> str:
        """
        Cleans the HTML body by removing unnecessary tags and attributes.

        Args:
            body (BeautifulSoup): The BeautifulSoup object representing the HTML body.

        Returns:
            str: The cleaned HTML content.
        """
        if not body:
            return None
        
        # Remove unwanted tags like meta, style, script, img, and link
        for tag in body(['meta', 'style', 'script', 'img', 'link']):
            tag.decompose()
        
        # Clear attributes for all other tags
        for element in body.find_all(True):
            element.attrs.clear()
        
        # Return the cleaned HTML as a string
        return str(body).strip()

    async def run(self, web_url: str = None) -> str:
        """
        Fetches the content from the provided URL and generates a markdown version.

        Args:
            web_url (str): The URL to fetch content from.

        Returns:
            str: The markdown content generated from the fetched HTML.
        """
        if not web_url:
            raise None
        
        # Fetch and clean the content from the web page
        web_content = await self.fetch_content(web_url)
        
        # If no content was retrieved, return an error message
        if web_content is None:
            return None
        
        # Prepare the prompt for content generation using the fetched web content
        prompt = HTML_CONTENT_HUMAN_PROMPT.format(data=web_content)
        
        # Generate the markdown content from the assistant
        try:
            return await self.a_generate_reply(messages=[{"content": prompt, "role": "user"}])
 
        except Exception as e:
            logger.error(f"Error generating markdown content: {e}")
            return None

