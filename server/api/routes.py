from fastapi import APIRouter
from .handlers.content_handler import fetch_content, edit_content
from fastapi.responses import StreamingResponse

api_router = APIRouter()

api_router.post('/content/{req_id}/get-content' )(fetch_content)
api_router.post('/content/{req_id}/edit-content' )(edit_content)