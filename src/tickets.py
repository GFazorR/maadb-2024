import datetime
import logging
import uuid
from http import HTTPStatus

from cassandra.cluster import ConsistencyLevel
from cassandra.query import SimpleStatement, BatchStatement, BatchType
from fastapi import APIRouter, Depends, Response

from models import Ticket, EventModel, DayCapacityModel
from utils import get_session

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post('/ticket/buy')
async def buy_ticket(
        ticket: Ticket,
        capacity: DayCapacityModel,
        session=Depends(get_session)
):
    query = SimpleStatement(
        """SELECT purchased_tickets FROM events WHERE event_id = %s AND event_day = %s""")

    get_purchased_tickets = session.execute(query, (
        uuid.UUID(ticket.event_id),
        ticket.event_day))

    purchased_tickets = get_purchased_tickets[0].purchased_tickets


    if purchased_tickets < capacity.max_capacity:
        logger.info(f'Purchased tickets: {purchased_tickets}')
        query = SimpleStatement("""
        UPDATE events 
        SET purchased_tickets = %s
        WHERE event_id = %s AND event_day = %s
        IF purchased_tickets = %s""")

        update_count_result = session.execute(query, (
            purchased_tickets + 1,
            uuid.UUID(ticket.event_id),
            ticket.event_day,
            purchased_tickets,
        ))

        logger.info(f'applied purchased tickets: {update_count_result[0].applied}')
        if update_count_result[0].applied:
            query = SimpleStatement(
                """INSERT INTO tickets (ticket_id, event_id, user_id, event_day,
                 purchase_date, ticket_price, discount, paid_price, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS""")

            ticket.id = uuid.uuid4()
            insert_ticket_result = session.execute(query, (
                ticket.id,
                uuid.UUID(ticket.event_id),
                uuid.UUID(ticket.user_id),
                ticket.event_day,
                datetime.datetime.now(),
                ticket.ticket_price,
                ticket.discount,
                ticket.paid_price,
                'sold'
            ))

            logger.info(insert_ticket_result[0].applied)
            # TODO: handle insert of an existing ticket
            return ticket

    return Response(status_code=HTTPStatus.NOT_FOUND)


@router.delete('/ticket/buy')
async def delete_ticket(
        ticket: Ticket,
        session=Depends(get_session)
):
    # TODO: determine consistency level
    query = SimpleStatement(
        """SELECT purchased_tickets FROM events WHERE event_id = %s AND event_day = %s""")

    get_purchased_tickets = session.execute(query, (
        uuid.UUID(ticket.event_id),
        ticket.event_day))

    purchased_tickets = get_purchased_tickets[0].purchased_tickets

    query = SimpleStatement("""
    SELECT * From tickets WHERE event_id = %s AND event_day = %s AND ticket_id = %s""")

    logger.info(f'ticket_id {ticket.id}')

    ticket_exists = session.execute(query, (
        uuid.UUID(ticket.event_id),
        ticket.event_day,
        uuid.UUID(ticket.id)
    ))

    if purchased_tickets > 0 and ticket_exists:
        logger.info(f'Purchased tickets: {purchased_tickets}')
        query = SimpleStatement("""
        UPDATE events 
        SET purchased_tickets = %s
        WHERE event_id = %s AND event_day = %s
        IF purchased_tickets = %s""")

        update_count_result = session.execute(query, (
            purchased_tickets - 1,
            uuid.UUID(ticket.event_id),
            ticket.event_day,
            purchased_tickets,
        ))

        logger.info(f'applied purchased tickets: {update_count_result[0].applied}')

        if update_count_result[0].applied:
            query = SimpleStatement("""
                UPDATE tickets
                SET status = %s
                WHERE event_id = %s AND event_day = %s AND ticket_id = %s AND user_id = %s AND purchase_date = %s
                IF EXISTS
                """, consistency_level=ConsistencyLevel.ONE)
            result = session.execute(query, (
                'deleted',
                uuid.UUID(ticket.event_id),
                ticket.event_day,
                uuid.UUID(ticket.id),
                uuid.UUID(ticket.user_id),
                ticket.purchased_date,
            ))

            if result[0].applied:
                return Response(status_code=HTTPStatus.OK)
    return Response(status_code=HTTPStatus.NOT_FOUND)


@router.get('/ticket/buy')
async def read_ticket(ticket_id: str):
    pass


if __name__ == '__main__':
    pass
