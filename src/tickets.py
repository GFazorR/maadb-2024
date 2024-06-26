import datetime
import logging
import uuid

from fastapi import APIRouter, Response, status

from models import Ticket, DayCapacityModel
from models import Tickets
from ticket_service import TicketService

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ticket_service = TicketService()


@router.post("/ticket")
async def buy_ticket(
        ticket: Ticket,
        capacity: DayCapacityModel,
):
    result = ticket_service.book_ticket(ticket, capacity)
    if result:
        tickets = Tickets(tickets=result)
        logger.info(tickets)
        return Response(status_code=status.HTTP_201_CREATED, content=tickets.json())
    return Response(status_code=status.HTTP_412_PRECONDITION_FAILED)


@router.delete('/ticket')
async def delete_ticket(
        ticket: Ticket,
):
    result = ticket_service.cancel_ticket(ticket)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.get('/ticket/{user_id}')
async def get_user_tickets(user_id: uuid.UUID, ticket_status: str = None):
    tickets = ticket_service.get_tickets_by_user(user_id, ticket_status)
    return Response(status_code=status.HTTP_200_OK, content=tickets.json())


@router.get('/discount/{user_id}')
async def calculate_discount(user_id: uuid.UUID):
    n_tickets = ticket_service.get_attended_events(user_id)
    logger.info(n_tickets)
    return n_tickets

if __name__ == '__main__':
    pass
