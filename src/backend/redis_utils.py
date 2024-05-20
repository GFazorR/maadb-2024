from redis import asyncio as aioredis
from models import Ticket, EventModel, UserModel
from typing import List
import uuid
import json
from pydantic.json import pydantic_encoder
import pickle

redis_client = aioredis.from_url('redis://localhost:6379', decode_responses=True)


async def delete_cache(event: EventModel):
    await redis_client.delete(str(event.id))


async def create_session(data: dict):
    # TODO check if session exists, return existing session
    # TODO define data to store in session
    token = str(uuid.uuid4())
    await redis_client.hset(token, mapping=data)
    await redis_client.expire(token, 3600)
    return token


async def get_session(session_id: str):
    user = await redis_client.hgetall(session_id)
    print(user)
    user = UserModel.parse_obj(json.loads(user['user']))
    return user


async def set_cache(event: EventModel):
    await redis_client.hset('event', key=str(event.id), value=event.model_dump_json())
    await redis_client.expire('event', 120)


async def get_cache(key: str):
    cached_event = await redis_client.hget('event', key=key)
    if cached_event:
        event = EventModel.parse_obj(json.loads(cached_event))
        return event


async def set_cache_published(events: List[EventModel]):
    async with redis_client.pipeline() as pipe:
        for event in events:
            pipe.hset('event', key=str(event.id), value=event.model_dump_json())
            pipe.expire('event', 120)
        await pipe.execute()


async def get_cached_published():
    cached_events = await redis_client.hgetall(name='event')
    if cached_events:
        result = []
        for event in cached_events.values():
            event = EventModel.parse_obj(json.loads(event))
            result.append(event)
        return result


if __name__ == '__main__':
    pass
