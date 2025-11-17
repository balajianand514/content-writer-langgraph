from pydantic import BaseModel, Field
from typing import Optional


class ContentCreationResponse(BaseModel):
    """
    Model to structure the response for content creation and reflection.
    """
    status: str = Field(..., description="Status of the process, e.g., 'success' or 'error'.")
    response: Optional[str] = Field(None, description="The generated content, if successful.")
    message: Optional[str] = Field(None, description="Error message if the process failed.")
