"""
This module implements user session crud operations endpoints
"""
from http.client import HTTPException

from fastapi import APIRouter, status, HTTPException, Response

import redis_utils
from models import EventModel

router = APIRouter()


@router.get("/session/events/{user_id}")
async def get_session(user_id: str):
    """
    Retrieves the session associated with a given user ID.
    :param user_id: str
    :return: EventModel | HTTPException
    """
    event = await redis_utils.get_event_session(user_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.put('/session/events/{user_id}')
@router.post("/session/events/{user_id}")
async def create_session(user_id: str, event: EventModel):
    """
    Performs an upsert for an EventModel session associated with a given user ID.
    :param user_id: str
    :param event: EventModel    :return:  EventModel | HTTPException
    """
    try:
        await redis_utils.upsert_event_session(user_id=user_id, event=event)
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    return event


@router.delete("/session/events/{user_id}")
async def delete_session(user_id: str):
    """
    Deletes the session associated with a given user ID.
    :param user_id: str
    :return: Response | HTTPException
    """
    event_id = await redis_utils.delete_event_session(user_id)
    if not event_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == '__main__':
    pass
