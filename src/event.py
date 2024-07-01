"""
This module implements endpoints for crud operations over events.
"""
import logging
import uuid
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    BackgroundTasks
)
from odmantic.exceptions import DocumentNotFoundError

from src.models import EventModel
from src.redis_utils import (
    get_cache,
    set_cache,
    delete_cache,
    get_cached_published,
    set_cache_published,
    set_cached_user_events,
    get_cached_user_events
)
from src.ticket_service import EventService
from src.utils import get_engine, get_event_service

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post('/event')
async def save_event(
        background_tasks: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine),
        event_service=Depends(get_event_service)
):
    """
    Performs an upsert for an EventModel on MongoDB with redis caching.
    :param event_service:
    :param background_tasks: BackgroundTasks object
    :param event: EventModel
    :param engine: Depends on engine
    :return: EventModel
    """
    event = await engine.save(event)
    background_tasks.add_task(set_cache, event)
    logger.info(event.id)

    if event.published:
        event_service.create_event(event)

    return event


@router.put('/event')
async def update_event(
        background_tasks: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine),
        event_service=Depends(get_event_service)
):
    """
    Performs an upsert for an EventModel on MongoDB with redis caching.
    :param event_service:
    :param background_tasks: BackgroundTasks object
    :param event: EventModel
    :param engine: Depends on engine
    :return: EventModel
    """
    event = await engine.save(event)
    background_tasks.add_task(set_cache, event)
    logger.info(event.id)
    if event.published:
        event_service.create_event(event)

    return event


# TODO manage tickets when event deleted
@router.delete('/event')
async def delete_event(
        background_task: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine),
):
    """
    Deletes an EventModel from Redis cache and MongoDB databases.
    :param background_task: BackgroundTasks object
    :param event: EventModel
    :param engine: Depends on engine
    :return: Response
    """
    logger.info((event.id, type(event.id)))
    try:
        background_task.add_task(delete_cache, event)
        await engine.delete(event)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


# TODO: refactor
@router.get('/event/event_id/{event_id}')
async def get_event_by_event_id(background_task: BackgroundTasks,
                                event_id: str,
                                engine=Depends(get_engine)):
    """
    Gets an EventModel by event_id from redis cache or MongoDB databases.
    :param background_task: BackgroundTasks object
    :param event_id: str
    :param engine: Depends on engine
    :return: Response
    """
    event = await get_cache(event_id)
    if event:
        return Response(status_code=status.HTTP_200_OK, content=event.model_dump_json())

    try:
        event = await engine.find(EventModel, {'_id': uuid.UUID(event_id)})
        background_task.add_task(set_cache, event[0])
        return Response(status_code=status.HTTP_200_OK, content=event[0].model_dump_json())
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@router.get('/event/published', response_model=List[EventModel])
async def get_published_events(background_task: BackgroundTasks,
                               engine=Depends(get_engine)):
    """
    Returns all published EventModels from Redis cache or MongoDB databases.
    :param background_task: BackgroundTasks object
    :param engine: Depends on engine
    :return: List[EventModel] | Response
    """
    events = await get_cached_published()
    logger.debug(f'events: {events}')
    if events:
        return events
    try:
        events = await engine.find(EventModel, {'published': True})
        background_task.add_task(set_cache_published, events)
        return events
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))

# TODO move in users
# TODO remove in-endpoint params
@router.get('/event/{user_id}', response_model=List[EventModel])
async def get_event_by_user_id(user_id: str,
                               background_task: BackgroundTasks,
                               engine=Depends(get_engine)):
    """
    Returns all events owned by a user, from redis cache or from MongoDB databases.
    :param user_id: str
    :param background_task: BackgroundTasks object
    :param engine: Depends on engine
    :return: List[EventModel] | Response
    """
    events = await get_cached_user_events(user_id)
    logger.debug(f'events: {events}')
    if events:
        return events
    try:
        events = await engine.find(EventModel, {'owner': uuid.UUID(user_id)})
        background_task.add_task(set_cached_user_events, user_id, events)
        return events
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


if __name__ == '__main__':
    pass
