import httpx
from autogen import Agent
import asyncio
from typing import List, Dict, Union
from server.setting import SETTINGS
from .types import BingSearchResponse, WebResult, ImageResult, RelatedSearch

class AzureBingSearchAgent(Agent):
    """
    A class to interact with the Azure Bing Search API for web searches.
    """

    SEARCH_COUNT: int = 2  # Default number of results to fetch per query

    def __init__(self) -> None:
        """
        Initializes the AzureBingSearchAgent with subscription key and endpoint from settings.
        """
        super().__init__(name="Azure Bing Search Agent")
        self.subscription_key: str = SETTINGS.azure._bing.subscription_key
        self.web_search_endpoint: str = SETTINGS.azure._bing.endpoint

        # Validate critical settings
        if not self.subscription_key or not self.web_search_endpoint:
            raise ValueError("Azure Bing Search subscription key or endpoint is not configured properly.")

    async def _bing_search(self, search_term: str, search_site: str = None) -> Union[BingSearchResponse, Dict[str, str]]:
        """
        Performs a web search using the Azure Bing Search API.

        Args:
            search_term (str): The term to search for.
            search_site (str): Optional domain to restrict search to a specific site.

        Returns:
            Union[BingSearchResponse, Dict[str, str]]: A BingSearchResponse model or an error dictionary.
        """
        query = self.construct_search_query(search_term, search_site)
        headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
        params = {
            "q": query,
            "textDecorations": True,
            "textFormat": "HTML",
            "count": self.SEARCH_COUNT,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.web_search_endpoint, headers=headers, params=params)

            response.raise_for_status()
            return self.process_search_results(response.json())

        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            return {"error": "Request error occurred", "details": str(e)}
        except Exception as e:
            return {"error": "Unexpected error occurred", "details": str(e)}

    @staticmethod
    def construct_search_query(search_term: str, search_site: str = None) -> str:
        """
        Constructs the search query string for Bing.

        Args:
            search_term (str): The term to search for.
            search_site (str): Optional site to restrict the search.

        Returns:
            str: The constructed query string.
        """
        return f"{search_term} site:{search_site}" if search_site else search_term

    def process_search_results(self, response_json: Dict) -> BingSearchResponse:
        """
        Processes the JSON response from the Bing Search API and extracts all available information.

        Args:
            response_json (Dict): The parsed JSON response from the Bing API.

        Returns:
            BingSearchResponse: A Pydantic model containing all the search results and related information.
        """
        try:
            # Processing web results
            web_results = [
                WebResult(
                    title=result.get("name", "N/A"),
                    url=result.get("url", "N/A"),
                    snippet=result.get("snippet", "N/A"),
                    display_url=result.get("displayUrl", "N/A"),
                    date_last_crawled=result.get("dateLastCrawled", "N/A"),
                    about=result.get("about", []),
                    keywords=result.get("keywords", "N/A"),
                    is_family_friendly=result.get("isFamilyFriendly", True),
                    language=result.get("language", "N/A")
                )
                for result in response_json.get("webPages", {}).get("value", [])
            ]

            # Processing related searches
            related_searches = [
                RelatedSearch(
                    text=search.get("text", "N/A"),
                    url=search.get("url", "N/A")
                )
                for search in response_json.get("relatedSearches", {}).get("value", [])
            ]

            # Processing image results
            images = [
                ImageResult(
                    title=image.get("name", "N/A"),
                    url=image.get("contentUrl", "N/A"),
                    thumbnail=image.get("thumbnailUrl", "N/A")
                )
                for image in response_json.get("images", {}).get("value", [])
            ]

            # Return structured response
            return BingSearchResponse(
                web_results=web_results,
                related_searches=related_searches,
                images=images
            )
        except (KeyError, TypeError) as e:
            return BingSearchResponse(web_results=[], related_searches=[], images=[])

    async def run(self, topic: str, sources: List[str]) -> List[BingSearchResponse]:
        """
        Executes a search query for the given topic across multiple sources.

        Args:
            topic (str): The topic to search for.
            sources (List[str]): List of domains to restrict the search.

        Returns:
            List[BingSearchResponse]: A list of BingSearchResponse models for each source.
        """
        if not sources:
            raise ValueError("Sources list cannot be empty or None.")

        tasks = [self._bing_search(topic, source) for source in sources]
        search_results = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for result in search_results:
            if isinstance(result, BingSearchResponse):
                results.append(result)  # Successful result
            elif isinstance(result, dict):  # Error response
                results.append(result)

        return results
