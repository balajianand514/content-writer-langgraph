from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse
from server.agents.system_agents.content_creator.agent import ContentCreationSystemAgent
from server.agents.system_agents.content_editor.agent import ContentEditorSystemAgent
import json
import logging
from typing import AsyncGenerator

# Initialize a logger for error handling
logger = logging.getLogger(__name__)

async def fetch_content(req_id: str, request: Request) -> StreamingResponse:
    """
    Handle requests to fetch content by orchestrating the content creation process.
    """
    try:
        request_body = await request.json()
        topic = request_body.get("topic")
        sources = request_body.get("sources", [])

        # Validate required fields
        if not topic:
            logger.warning(f"Missing required field: 'topic' in request [req_id={req_id}].")
            raise HTTPException(status_code=400, detail="Missing required field: 'topic'.")
        
        # Validate sources if provided
        if sources and not isinstance(sources, list):
            logger.warning(f"Invalid sources format. Expected list, got {type(sources)} [req_id={req_id}].")
            raise HTTPException(status_code=400, detail="Sources must be a list.")
        
        # Orchestrate content creation using the ContentCreationSystemAgent
        user = request.headers.get("user", "default_user")
        content_agent = ContentCreationSystemAgent(req_id=req_id, user=user)

        async def content_stream() -> AsyncGenerator[str, None]:
            async for document_data in content_agent.run(topic, sources):
                yield document_data

        logger.info(f"Successfully initiated content creation process [req_id={req_id}, topic={topic}].")
        return StreamingResponse(content=content_stream(), media_type="application/json")

    except HTTPException as http_ex:
        logger.error(f"Validation error in fetch_content [req_id={req_id}]: {http_ex.detail}")
        return StreamingResponse(
            content=json.dumps({"error": http_ex.detail}),
            media_type="application/json",
            status_code=http_ex.status_code,
        )
    except Exception as ex:
        logger.error(f"Unhandled exception in fetch_content [req_id={req_id}]: {ex}")
        return StreamingResponse(
            content=json.dumps({"error": "An unexpected error occurred."}),
            media_type="application/json",
        )


async def edit_content(req_id: str, request: Request) -> StreamingResponse:
    """
    Handle requests to edit content based on user feedback.
    """
    try:
        request_body = await request.json()
        feedback = request_body.get("feedback")
        post_content = request_body.get("postContent")

        # Validate required fields
        if not feedback:
            logger.warning(f"Missing required field: 'feedback' in request [req_id={req_id}].")
            raise HTTPException(status_code=400, detail="Missing required field: 'feedback'.")
        if not post_content:
            logger.warning(f"Missing required field: 'postContent' in request [req_id={req_id}].")
            raise HTTPException(status_code=400, detail="Missing required field: 'postContent'.")

        # Orchestrate content refinement using the ContentRefinementSystemAgent
        user = request.headers.get("user", "default_user")
        content_agent = ContentEditorSystemAgent(req_id=req_id, user=user)

        async def content_stream() -> AsyncGenerator[str, None]:
            async for document_data in content_agent.run(post_content=post_content, user_feedback=feedback):
                yield document_data

        logger.info(f"Successfully initiated content refinement process [req_id={req_id}].")
        return StreamingResponse(content=content_stream(), media_type="application/json")

    except HTTPException as http_ex:
        logger.error(f"Validation error in edit_content [req_id={req_id}]: {http_ex.detail}")
        return StreamingResponse(
            content=json.dumps({"error": http_ex.detail}),
            media_type="application/json",
            status_code=http_ex.status_code,
        )
    except Exception as ex:
        logger.error(f"Unhandled exception in edit_content [req_id={req_id}]: {ex}")
        return StreamingResponse(
            content=json.dumps({"error": "An unexpected error occurred."}),
            media_type="application/json",
        )
