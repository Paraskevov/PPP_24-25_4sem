import logging
from fastapi import APIRouter, WebSocket, HTTPException
from pydantic import BaseModel
from app.celery.tasks import start_site_parsing
import redis.asyncio as redis
import json

router = APIRouter()
logger = logging.getLogger(__name__)

class ParsingRequest(BaseModel):
    url: str
    max_depth: int
    user_id: int

class UserCreateRequest(BaseModel):
    name: str
    age: int

@router.websocket("/ws/{user_id}")
async def websocket_updates(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    
    redis_conn = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(f"parsing_updates:{user_id}")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_json(json.loads(message["data"]))
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await pubsub.unsubscribe(f"parsing_updates:{user_id}")
        await pubsub.close()
        await redis_conn.close()

@router.post("/parse/")
async def initiate_parsing(request: ParsingRequest):
    """Start a new site parsing task."""
    try:
        task = start_site_parsing(
            url=request.url,
            max_depth=request.max_depth,
            user_id=request.user_id
        )
        return {"task_id": task.id, "status": "started"}
    except Exception as e:
        logger.error(f"Parsing initiation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))