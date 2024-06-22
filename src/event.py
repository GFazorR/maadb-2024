"""
This module implements endpoints for crud operations over events.
"""
import datetime
import logging
import uuid
from typing import List

from cassandra.cluster import ConsistencyLevel, Session
from cassandra.query import SimpleStatement
from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    BackgroundTasks
)
from odmantic.exceptions import DocumentNotFoundError

from models import EventModel
from redis_utils import (
    get_cache,
    set_cache,
    delete_cache,
    get_cached_published,
    set_cache_published,
    set_cached_user_events,
    get_cached_user_events,
    set_cache_tickets,
    get_cache_tickets
)
from utils import get_engine, get_session

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post('/event')
async def save_event(
        background_tasks: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine),
        session=Depends(get_session),
):
    """
    Performs an upsert for an EventModel on MongoDB with redis caching.
    :param session:
    :param background_tasks: BackgroundTasks object
    :param event: EventModel
    :param engine: Depends on engine
    :return: EventModel
    """
    event = await engine.save(event)
    background_tasks.add_task(set_cache, event)

    insert_ticket = SimpleStatement(
        """INSERT INTO events (event_id, event_day, purchased_tickets)
         VALUES (%s, %s, %s)""", consistency_level=ConsistencyLevel.QUORUM
    )
    if event.published:
        for cap in event.capacity_by_day:
            session.execute(insert_ticket, (event.id, cap.day, 0))

    return event


@router.put('/event')
async def update_event(
        background_tasks: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine),
):
    """
    Performs an upsert for an EventModel on MongoDB with redis caching.
    :param background_tasks: BackgroundTasks object
    :param event: EventModel
    :param engine: Depends on engine
    :return: EventModel
    """
    event = await engine.save(event)
    background_tasks.add_task(set_cache, event)
    return event


# TODO manage tickets when event deleted
@router.delete('/event')
async def delete_event(
        background_task: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine)):
    """
    Deletes an EventModel from Redis cache and MongoDB databases.
    :param background_task: BackgroundTasks object
    :param event: EventModel
    :param engine: Depends on engine
    :return: Response
    """
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
    logger.info(f'events: {events}')
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
    """
    Returns all events owned by a user, from redis cache or from MongoDB databases.
    :param user_id: str
    :param background_task: BackgroundTasks object
    :param engine: Depends on engine
    :return: List[EventModel] | Response
    """
    events = await get_cached_user_events(user_id)
    logger.info(f'events: {events}')
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
