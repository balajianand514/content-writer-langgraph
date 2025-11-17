from pydantic import BaseModel
from typing import Optional, List

# Pydantic Models
class RelatedSearch(BaseModel):
    text: str
    url: str


class ImageResult(BaseModel):
    title: str
    url: str
    thumbnail: str


class WebResult(BaseModel):
    title: str
    url: str
    snippet: str
    display_url: str
    date_last_crawled: Optional[str] = None  # Date when Bing last crawled the page
    about: Optional[List[dict]] = []  # List of entities related to the result
    keywords: Optional[str] = None  # Keywords if provided
    is_family_friendly: Optional[bool] = True  # Whether the result is family-friendly
    language: Optional[str] = None  # Language of the page


class BingSearchResponse(BaseModel):
    web_results: List[WebResult]
    related_searches: List[RelatedSearch]
    images: List[ImageResult]





