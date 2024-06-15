import logging
import uuid
from http import HTTPStatus

from cassandra.cluster import ConsistencyLevel
from cassandra.query import SimpleStatement, BatchStatement
from fastapi import APIRouter, Depends, Response

from models import Ticket
from utils import get_session, get_engine

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@router.post('/ticket/buy')
async def buy_ticket(
        ticket: Ticket,
        session=Depends(get_session)
):
    query = SimpleStatement(
        """SELECT available_tickets, purchased_tickets FROM events WHERE event_id = %s AND event_day = %s""",
        consistency_level=ConsistencyLevel.QUORUM)
    result = session.execute(query, (uuid.UUID(ticket.event_id), ticket.event_day))
    available_tickets = result[0].available_tickets
    purchased_tickets = result[0].purchased_tickets
    if available_tickets > 0:

        query = SimpleStatement("""
        UPDATE events 
        SET available_tickets = %s , purchased_tickets = %s
        WHERE event_id = %s AND event_day = %s
        IF available_tickets = %s AND purchased_tickets = %s
        """, consistency_level=ConsistencyLevel.QUORUM)
        applied = session.execute(query, (
        available_tickets - 1, purchased_tickets + 1, uuid.UUID(ticket.event_id), ticket.event_day, available_tickets,
        purchased_tickets))

        if applied[0].applied:
            query = SimpleStatement(
                """INSERT INTO tickets (ticket_id, event_id, user_id, purchase_date, ticket_price, discount, paid_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS""",
                consistency_level=ConsistencyLevel.QUORUM
            )
            ticket.id = uuid.uuid4()
            result = session.execute(query, (
                ticket.id,
                uuid.UUID(ticket.event_id),
                uuid.UUID(ticket.user_id),
                ticket.purchased_date,
                ticket.ticket_price,
                ticket.discount,
                ticket.paid_price
            ))

            logger.info(result[0].applied)
            # TODO: handle insert of an existing ticket
            return ticket

    return Response(status_code=HTTPStatus.NOT_FOUND)


@router.delete('/ticket/buy')
async def delete_ticket(
        ticket: Ticket,
        session=Depends(get_session)
):
    # TODO: determine consistency level

    # delete ticket from ticket db
    # update count

    query = SimpleStatement("""
        DELETE FROM tickets
        WHERE event_id = %s AND event_day = %s
        IF EXISTS
        """, consistency_level=ConsistencyLevel.QUORUM)
    result = session.execute(query, (uuid.UUID(ticket.event_id), ticket.event_day))
    applied = result[0].applied
    if applied[0].applied:
        pass


@router.get('/ticket/buy')
async def read_ticket(ticket_id: str):
    pass


if __name__ == '__main__':
    pass
