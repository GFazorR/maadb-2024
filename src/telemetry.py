import uuid

from fastapi import APIRouter, Response, status

from ticket_service import TelemetryService

router = APIRouter()
telemetry_service = TelemetryService()


@router.get('/visits/event')
async def get_visits(event_id: uuid.UUID):
    return telemetry_service.get_counter(event_id)


@router.put('/visits/event')
async def update_visits(event_id: uuid.UUID):
    telemetry_service.update_counter(event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == '__main__':
    pass
