import aioredis
from models import Ticket, EventModel, UserModel
import uuid

redis_client = aioredis.from_url('redis://localhost:6379', decode_responses=True)


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
    mapping = {'event': event.model_dump_json()}
    await redis_client.hset(str(event.id),
                            mapping=mapping)
    await redis_client.expire(str(event.id), 120)


async def get_cache(key: str):
    cached_event = await redis_client.get(key)
    if cached_event:
        event = EventModel.parse_obj(json.loads(cached_event))
        return event


if __name__ == '__main__':
    pass
