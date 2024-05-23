import uuid
from http.client import HTTPException

from fastapi import APIRouter, status, HTTPException, Response
from models import EventModel
import redis_utils

router = APIRouter()


@router.get("/session/events/{user_id}")
async def get_session(user_id: str):
    event = redis_utils.get_event_session(user_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.put('/session/events/{user_id}')
@router.post("/session/events/{user_id}")
async def create_session(user_id: str, event: EventModel):
    try:
        await redis_utils.upsert_event_session(user_id=user_id, event=event)
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    return event


@router.delete("/session/events/{user_id}")
async def delete_session(user_id: str):
    event_id = redis_utils.delete_event_session(user_id)
    if not event_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == '__main__':
    pass
