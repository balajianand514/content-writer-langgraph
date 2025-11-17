from dataclasses import dataclass, field
from typing import Dict
from pydantic import BaseModel
from typing import List
 
class Response(BaseModel):
    url: str 
    title: str 
    article_summary:str
    post_content: str


 
 
 



