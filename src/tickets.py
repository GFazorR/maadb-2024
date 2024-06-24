import logging
from typing import List

from fastapi import APIRouter, Response, status

from models import Ticket, DayCapacityModel
from ticket_service import TicketService
from pydantic import TypeAdapter, BaseModel

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ticket_service = TicketService()


class Tickets(BaseModel):
    tickets: List[Ticket]

list_adapter = TypeAdapter(Tickets)


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


@router.get('/ticket/buy')
async def read_ticket(ticket_id: str):
    pass


if __name__ == '__main__':
    pass
