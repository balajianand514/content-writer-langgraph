from dataclasses import dataclass, field
from typing import Dict
from pydantic import BaseModel
from typing import List, Optional
 
class Response(BaseModel):
    url: str 
    title: str 
    article_summary:str
    post_content: str

class WebContent(BaseModel):

    url: str
    web_content: Optional[str]
    summary: Optional[str]
    post_content: Optional[str] = ""
   


 
 
 



