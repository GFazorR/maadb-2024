from models import EventModel, UserModel
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    Response,
    status,
    BackgroundTasks
)
from typing import Optional, Annotated, Union, Dict, List
from utils import get_engine
from redis_utils import get_cache, get_session, set_cache, create_session
import json


router = APIRouter()


@router.post('/event')
async def save_event(background_task: BackgroundTasks, event: EventModel,
                     header: Annotated[Union[str, None], Header()] = None,
                     engine=Depends(get_engine)):
    print(type(header), header)
    user = await get_session(session_id=header)
    if not event.owner:
        event.owner.append(user.id)
    event = await engine.save(event)
    background_task.add_task(set_cache, event)
    return event


@router.put('/event')
async def update_event(event: EventModel):
    # TODO: add cache
    event = await engine.save(event)
    return event


@router.delete('/event')
async def delete_event(event: EventModel):
    # TODO: add cache
    # TODO: make it transactional ?
    try:
        _ = await engine.delete(event)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@router.get('/event')
async def get_saved_events(background_task: BackgroundTasks, event_id: str):
    events = await get_cache(event_id)
    if events:
        return Response(status_code=status.HTTP_200_OK, content=events)

    try:
        events = await engine.find(EventModel, {'_id': ObjectId(event_id)})
        event = events[0]
        print(type(event), event)
        background_task.add_task(set_cache, event)
        return Response(status_code=status.HTTP_200_OK, content=event.model_dump_json())
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@router.get('/event/published', response_model=List[EventModel])
async def get_published_events():
    try:
        events = await engine.find(EventModel, {'published': True})
        return events
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@router.get('/event/{user_id}', response_model=List[EventModel])
async def get_event(user_id: str):
    events = await engine.find(EventModel, {'owner': ObjectId(user_id)})
    return events


if __name__ == '__main__':
    pass
