from http import HTTPStatus

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
from redis_utils import (
    get_cache,
    get_session,
    set_cache,
    create_session,
    delete_cache,
    get_cached_published,
    set_cache_published,
    set_cached_user_events,
    get_cached_user_events
)
from odmantic.exceptions import DocumentNotFoundError
import json
from bson import ObjectId

router = APIRouter()


@router.put('/event')
@router.post('/event')
async def save_event(
        background_tasks: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine)
):
    background_tasks.add_task(set_cache, event)
    event = await engine.save(event)
    return event


@router.delete('/event')
async def delete_event(
        background_task: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine)):
    try:
        background_task.add_task(delete_cache, event)
        del_id = await engine.delete(event)
        if not del_id:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


# TODO: refactor
@router.get('/event')
async def get_saved_events(background_task: BackgroundTasks,
                           event_id: str,
                           engine=Depends(get_engine)):
    event = await get_cache(event_id)
    if event:
        return Response(status_code=status.HTTP_200_OK, content=event.model_dump_json())

    try:
        event = await engine.find(EventModel, {'_id': ObjectId(event_id)})
        background_task.add_task(set_cache, event[0])
        return Response(status_code=status.HTTP_200_OK, content=event[0].model_dump_json())
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@router.get('/event/published', response_model=List[EventModel])
async def get_published_events(background_task: BackgroundTasks,
                               engine=Depends(get_engine)):
    events = await get_cached_published()
    print(events)
    if events:
        return events
    try:
        events = await engine.find(EventModel, {'published': True})
        background_task.add_task(set_cache_published, events)
        return events
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@router.get('/event/{user_id}', response_model=List[EventModel])
async def get_event(user_id: str,
                    background_task: BackgroundTasks,
                    engine=Depends(get_engine)):
    events = await get_cached_user_events(user_id)
    print(events)
    if events:
        return events
    try:
        events = await engine.find(EventModel, {'owner': ObjectId(user_id)})
        background_task.add_task(set_cached_user_events, user_id, events)
        return events
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


if __name__ == '__main__':
    pass
