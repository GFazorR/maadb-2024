import uuid

from fastapi import APIRouter, Response, status, Depends, BackgroundTasks
from math import log

from src.redis_utils import get_cached_discount, set_cached_discount
from src.utils import get_analytics_service, get_ticket_service

router = APIRouter()


@router.get('/visits/event')
async def get_visits(event_id: uuid.UUID,
                     analytics_service=Depends(get_analytics_service)):
    return analytics_service.get_counter(event_id)


@router.put('/visits/event')
async def update_visits(event_id: uuid.UUID,
                        analytics_service=Depends(get_analytics_service)):
    analytics_service.update_counter(event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/statistics/event')
async def get_statistics(
        event_id: uuid.UUID,
        analytics_service=Depends(get_analytics_service)
):
    result = analytics_service.get_event_counter(event_id)
    if result:
        return result
    return Response(status_code=status.HTTP_404_NOT_FOUND)

if __name__ == '__main__':
    pass
