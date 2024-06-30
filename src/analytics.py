import uuid

from fastapi import APIRouter, Response, status, Depends

from src.ticket_service import AnalyticsService
from src.utils import get_analytics_service

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


if __name__ == '__main__':
    pass
