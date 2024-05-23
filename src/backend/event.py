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
    set_cache_published
)
from odmantic.exceptions import DocumentNotFoundError
import json
from bson import ObjectId

router = APIRouter()


# TODO cache write behind per non pubblicati
# TODO cache write through per pubblicati
@router.put('/event')
@router.post('/event')
async def save_event(event: EventModel,
                     engine=Depends(get_engine)):
    event = await engine.save(event)
    return event


# TODO cache write behind per non pubblicati
# TODO cache write through per pubblicati
@router.delete('/event')
async def delete_event(event: EventModel, engine=Depends(get_engine)):
    try:
        _ = await engine.delete(event)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


# TODO: refactor
@router.get('/event')
async def get_saved_events(event_id: str,
                           engine=Depends(get_engine)):
    try:
        event = await engine.find(EventModel, {'_id': ObjectId(event_id)})
        return Response(status_code=status.HTTP_200_OK, content=event[0].model_dump_json())
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@router.get('/event/published', response_model=List[EventModel])
async def get_published_events(engine=Depends(get_engine)):
    try:
        events = await engine.find(EventModel, {'published': True})
        return events
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@router.get('/event/{user_id}', response_model=List[EventModel])
async def get_event(user_id: str,
                    engine=Depends(get_engine)):
    events = await engine.find(EventModel, {'owner': ObjectId(user_id)})
    return events


if __name__ == '__main__':
    pass
