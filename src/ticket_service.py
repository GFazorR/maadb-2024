import logging
import uuid

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

from models import EventModel, Ticket, DayCapacityModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cluster = Cluster(port=9042)
session = cluster.connect('ticket_service')


class EventService:
    def __init__(self):
        self.session = session
        self.insert_event = session.prepare("""
        UPDATE ticket_service.events
        SET purchased_tickets = purchased_tickets + 0
        WHERE event_id = ? AND event_day = ?
        """)

    def create_event(self, event: EventModel):
        for cap in event.capacity_by_day:
            self.session.execute(
                self.insert_event,
                (
                    event.id,
                    cap.day
                ))


class TicketService:
    def __init__(self):
        self.session = session
        self.insert_ticket = SimpleStatement("""
        INSERT INTO tickets 
        (event_id, event_day, purchase_date, user_id,
        ticket_id, ticket_price, discount, paid_price, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        IF NOT EXISTS
        """)

        self.increment_counter = SimpleStatement("""
        UPDATE ticket_service.events
        SET purchased_tickets = purchased_tickets + %s
        WHERE event_id = %s AND event_day = %s
        """)

        self.update_ticket = SimpleStatement("""
        UPDATE ticket_service.tickets
        SET status = %s
        WHERE event_id = %s AND event_day = %s AND user_id = %s AND ticket_id = %s
        IF EXISTS
        """)

        self.n_tickets = SimpleStatement("""
        SELECT purchased_tickets
        FROM ticket_service.events
        WHERE event_id = %s AND event_day = %s
        """)

    def book_ticket(self,
                    ticket: Ticket,
                    capacity: DayCapacityModel,
                    n_tickets=1):

        purchased = self.session.execute(self.n_tickets, (
            uuid.UUID(ticket.event_id),
            ticket.event_day,
        ))
        purchased = purchased[0].purchased_tickets
        if purchased + n_tickets <= capacity.max_capacity:
            created_tickets = []
            # TODO rollback
            for i in range(n_tickets):
                ticket = self._create_ticket(ticket)
                logger.info(ticket)
                created_tickets.append(ticket)
            return created_tickets

    def cancel_ticket(self, ticket: Ticket):
        result = self.session.execute(self.update_ticket, (
            'canceled',
            uuid.UUID(ticket.event_id),
            ticket.event_day,
            uuid.UUID(ticket.user_id),
            uuid.UUID(ticket.id),
        ))
        if result.was_applied:
            self.session.execute(self.increment_counter, (
                -1,
                uuid.UUID(ticket.event_id),
                ticket.event_day,
            ))
            return result

    def _create_ticket(self, ticket):
        ticket.id = uuid.uuid4()
        result = self.session.execute(self.insert_ticket, (
            uuid.UUID(ticket.event_id),
            ticket.event_day,
            ticket.purchased_date,
            uuid.UUID(ticket.user_id),
            ticket.id,
            ticket.ticket_price,
            ticket.discount,
            ticket.paid_price,
            'purchased'
        ))

        if result.was_applied:
            self.session.execute(self.increment_counter, (
                1,
                uuid.UUID(ticket.event_id),
                ticket.event_day,
            ))
            return ticket
        else:
            raise NotImplementedError('Transaction failed')

    def _rollback(self, ticket: Ticket):
        pass


if __name__ == '__main__':
    pass
