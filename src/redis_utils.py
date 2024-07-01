"""
This module implements async operations on redis for user session and caching events.
"""

import json
import uuid
from typing import List

from redis import asyncio as aioredis

from src.models import EventModel, UserModel

redis_client = aioredis.from_url('redis://localhost:6379', decode_responses=True)


async def upsert_event_session(user_id: str, event: EventModel):
    """
    Inserts or update an EventModel in redis events session hset.
    :param user_id: str
    :param event: EventModel
    :return: None
    """
    await redis_client.hset('events', key=user_id, value=event.model_dump_json())


async def delete_event_session(user_id: str):
    """
    Delete an EventModel from redis events session hset.
    :param user_id: str
    :return: event_id: str
    """
    return await redis_client.hdel('events', user_id)


async def get_event_session(user_id: str) -> EventModel:
    """
    Get an EventModel from redis events session hset.
    :param user_id: str
    :return: EventModel
    """
    event = await redis_client.hget('events', key=user_id)
    return EventModel.parse_obj(json.loads(event))


async def delete_cache(event: EventModel):
    """
    Delete cached EventModel from redis events session hset.
    :param event: EventModel
    :return: None
    """
    await redis_client.delete(str(event.id))


async def create_session(data: dict):
    """
    Creates a user session token and stores data in redis.
    :param data: dict
    :return: token: str
    """
    token = str(uuid.uuid4())
    await redis_client.hset(token, mapping=data)
    await redis_client.expire(token, 120)
    return token


async def get_session(session_id: str):
    """
    Get cached UserModel session from redis.
    :param session_id: str
    :return: UserModel | None
    """
    user = await redis_client.hgetall(session_id)
    if user:
        user = UserModel.parse_obj(json.loads(user['user']))
        return user


async def set_cache(event: EventModel):
    """
    Stores an EventModel in redis events hset cache.
    :param event: EventModel
    :return: None
    """
    await redis_client.hset('event', key=str(event.id), value=event.model_dump_json())
    await redis_client.expire('event', 120)


async def get_cache(key: str):
    """
    Retrieves a specific cached EventModel from redis.
    :param key: str
    :return: EventModel | None
    """
    cached_event = await redis_client.hget('event', key=key)
    if cached_event:
        event = EventModel.parse_obj(json.loads(cached_event))
        return event


async def set_cache_published(events: List[EventModel]):
    """
    Caches a list of EventModel that are published in redis.
    :param events: List[EventModel]
    :return: None
    """
    async with redis_client.pipeline() as pipe:
        for event in events:
            pipe.hset('event', key=str(event.id), value=event.model_dump_json())
            pipe.expire('event', 120)
        await pipe.execute()


async def get_cached_published():
    """
    Retrieves the list of cached published EventModel from redis.
    :return: List[EventModel] | None
    """
    cached_events = await redis_client.hgetall(name='event')
    if cached_events:
        result = []
        for event in cached_events.values():
            event = EventModel.parse_obj(json.loads(event))
            result.append(event)
        return result


async def set_cached_user_events(user_id: str, events: List[EventModel]):
    """
    Caches the list of EventModels that are owned by a specific user in redis.
    :param user_id: str
    :param events: List[EventModel]
    :return: None
    """
    async with redis_client.pipeline() as pipe:
        for event in events:
            pipe.hset('user_events', key=str(user_id), value=event.model_dump_json())
            pipe.expire('event', 120)
        await pipe.execute()


async def set_cached_discount(user_id, discount):
    await redis_client.set(f'{user_id}_discount', discount)
    await redis_client.expire(f'{user_id}_discount', 120)


async def get_cached_discount(user_id):
    return await redis_client.get(f'{user_id}_discount')


async def get_cached_user_events(user_id: str):
    """
    Retrieves the list of EventModels that are owned by a specific user from redis.
    :param user_id: str
    :return: List[EventModel] | None
    """
    cached_events = await redis_client.hgetall('user_events')
    if cached_events:
        result = [EventModel.parse_obj(json.loads(v))
                  for k, v in cached_events.items()
                  if v == user_id]
        return result


async def set_cache_tickets(event):
    async with redis_client.pipeline() as pipe:
        for cap in event.capacity_by_day:
            pipe.hset(event.id, key=str(cap.day), value=cap.max_capacity)
        await pipe.execute()


if __name__ == '__main__':
    pass
