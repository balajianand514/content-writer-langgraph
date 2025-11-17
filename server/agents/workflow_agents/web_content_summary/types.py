from pydantic import BaseModel, Field
from typing import Optional

class WebContentSummary(BaseModel):
    """
    Model to structure the response for content creation and reflection.
    """
    url: str
    title: Optional[str]
    summary: Optional[str]
   