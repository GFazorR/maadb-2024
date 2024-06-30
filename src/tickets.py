import logging
import uuid

from fastapi import APIRouter, Response, status, Depends

from src.models import Ticket, DayCapacityModel, Tickets
from src.utils import get_ticket_service

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/ticket")
async def buy_ticket(
        ticket: Ticket,
        capacity: DayCapacityModel,
        n_tickets: int = 1,
        ticket_service=Depends(get_ticket_service)
):
    try:
        result = ticket_service.lock_tickets(
            ticket,
            capacity.max_capacity,
            n_tickets
        )
    except ValueError as e:
        return Response(status_code=status.HTTP_226_IM_USED, content=str(e))
    if result:
        return Response(status_code=status.HTTP_201_CREATED)
    return Response(status_code=status.HTTP_412_PRECONDITION_FAILED)


@router.post("/ticket/confirm")
async def confirm_ticket(
        tickets: Ticket,
        ticket_service=Depends(get_ticket_service)
):
    result = ticket_service.book_tickets(tickets)
    if result:
        tickets = Tickets(tickets=result)
        return Response(status_code=status.HTTP_201_CREATED,
                        content=tickets.json())
    return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/ticket/confirm")
async def confirm_ticket(
        ticket: Ticket,
        ticket_service=Depends(get_ticket_service)
):
    result = ticket_service.cancel_ticket(ticket)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete('/ticket')
async def delete_ticket(
        ticket: Ticket,
        ticket_service=Depends(get_ticket_service)
):
    result = ticket_service.decrement_tickets(ticket)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.get('/ticket/{user_id}')
async def get_user_tickets(
        user_id: uuid.UUID,
        ticket_status: str = None,
        ticket_service=Depends(get_ticket_service)
):
    tickets = ticket_service.get_tickets_by_user(user_id, ticket_status)
    return Response(status_code=status.HTTP_200_OK, content=tickets.json())


# TODO Move to analytics
# TODO cache
# TODO implement discount calculation
@router.get('/discount/{user_id}')
async def calculate_discount(
        user_id: uuid.UUID,
        ticket_service=Depends(get_ticket_service)
):
    n_tickets = ticket_service.get_attended_events(user_id)
    return n_tickets


if __name__ == '__main__':
    pass
