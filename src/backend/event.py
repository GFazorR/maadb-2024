"""
This module implements endpoints for crud operations over events.
"""
import uuid
from typing import List

import bson
from bson import ObjectId
from cassandra.cluster import Session, ConsistencyLevel, RetryPolicy, NeverRetryPolicy
from cassandra.query import SimpleStatement, BatchStatement, BatchType
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
    get_cached_user_events
)
from utils import get_engine, get_session
import logging

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
    :param background_tasks: BackgroundTasks object
    :param event: EventModel
    :param engine: Depends on engine
    :return: EventModel
    """
    background_tasks.add_task(set_cache, event)
    event = await engine.save(event)
    query = SimpleStatement('INSERT INTO tickets (event_id, ticket_id, available, price) Values (?,?,?,?)')

    print(event.id, type(event.id))
    for cap in event.capacity_by_day:
        for _ in range(cap.max_capacity):
            session.execute(query, [event.id, uuid.uuid4(), True, cap.price])


    # insert_stats = SimpleStatement(
    #     """INSERT INTO stats (event_id , available_tickets, on_sale, purchased_tickets, revenues)
    #     VALUES (?,?,?,?,?)
    #     """
    # )
    # session.execute(insert_stats, [event.id, sum(cap.max_capacity for cap in event.capacity_by_day), True, 0, 0.0])
    return event


@router.put('/event')
async def update_event(
        background_tasks: BackgroundTasks,
        event: EventModel,
        engine=Depends(get_engine)
):
    """
    Performs an upsert for an EventModel on MongoDB with redis caching.
    :param background_tasks: BackgroundTasks object
    :param event: EventModel
    :param engine: Depends on engine
    :return: EventModel
    """
    background_tasks.add_task(set_cache, event)
    event = await engine.save(event)
    # TODO if event published and it wasn't published before, generate tickets on cassandra
    # TODO also add an entry with the total number of tickets available in ticket_sales
    return event


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
        event = await engine.find(EventModel, {'_id': ObjectId(event_id)})
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
        events = await engine.find(EventModel, {'owner': ObjectId(user_id)})
        background_task.add_task(set_cached_user_events, user_id, events)
        return events
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


if __name__ == '__main__':
    pass
