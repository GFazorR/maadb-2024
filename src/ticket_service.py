import datetime
import logging
import uuid

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

from models import EventModel, Ticket, DayCapacityModel, Tickets

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


class TelemetryService:
    def __init__(self):
        self.session = session
        self.query_update_counter = SimpleStatement("""
        UPDATE ticket_service.user_visits
        SET page_visits = page_visits + 1
        WHERE event_id = %s
        """)

        self.query_counter = SimpleStatement("""
        SELECT page_visits
        FROM ticket_service.user_visits
        WHERE event_id = %s
        """)

    def update_counter(self, event_id):
        self.session.execute(
            self.query_update_counter,
            (event_id, )
        )

    def get_counter(self, event_id):
        result = self.session.execute(
            self.query_counter,
            (event_id,)
        )
        return result.one().page_visits



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

        self.insert_by_user = SimpleStatement("""
        INSERT INTO tickets_by_user ("user_id", "purchase_date", "event_day", "event_id", "ticket_id", "paid_price", "status") 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        IF NOT EXISTS
        """)

        self.insert_by_user_and_date = SimpleStatement("""
        INSERT INTO tickets_by_user_and_date ("user_id", "event_day", "event_id", "ticket_id", "purchase_date", "paid_price", "status")
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        IF NOT EXISTS
        """)

        self.update_by_user = SimpleStatement("""
        UPDATE tickets_by_user
        SET status = %s
        WHERE user_id = %s AND ticket_id = %s
        IF EXISTS
        """)

        self.update_by_user_and_date = SimpleStatement("""
        UPDATE tickets_by_user_and_date
        SET status = %s
        WHERE user_id = %s AND event_day = %s AND ticket_id = %s
        IF EXISTS
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

        self.user_tickets_status = SimpleStatement("""
        SELECT * 
        FROM tickets_by_user
        WHERE user_id = %s AND status = %s
        """)

        self.user_tickets = SimpleStatement("""
                SELECT * 
                FROM tickets_by_user
                WHERE user_id = %s
                """)

        self.attended_events = SimpleStatement("""
        SELECT event_id 
        FROM tickets_by_user_and_date
        WHERE user_id = %s AND event_day < %s AND status = %s
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
        result_ticket = self.session.execute(self.update_ticket, (
            'canceled',
            uuid.UUID(ticket.event_id),
            ticket.event_day,
            uuid.UUID(ticket.user_id),
            uuid.UUID(ticket.id),
        ))
        result_users = self.session.execute(self.update_by_user, (
            'canceled',
            uuid.UUID(ticket.user_id),
            uuid.UUID(ticket.id),
        ))
        result_users_and_date = self.session.execute(
            self.update_by_user_and_date,
            (
                'canceled',
                uuid.UUID(ticket.user_id),
                ticket.event_day,
                uuid.UUID(ticket.id),
            )
        )

        if result_ticket.was_applied and result_users.was_applied and result_users_and_date.was_applied:
            self.session.execute(self.increment_counter, (
                -1,
                uuid.UUID(ticket.event_id),
                ticket.event_day,
            ))
            return result_ticket

    def _create_ticket(self, ticket):
        ticket.id = uuid.uuid4()
        result_ticket = self.session.execute(self.insert_ticket,
                                             parameters=(
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
        result_user = self.session.execute(
            self.insert_by_user,
            parameters=(
                uuid.UUID(ticket.user_id),
                ticket.purchased_date,
                ticket.event_day,
                uuid.UUID(ticket.event_id),
                ticket.id,
                ticket.paid_price,
                'purchased'
            ))

        result_user_and_date = self.session.execute(
            self.insert_by_user_and_date,
            parameters=(
                uuid.UUID(ticket.user_id),
                ticket.event_day,
                uuid.UUID(ticket.event_id),
                ticket.id,
                ticket.purchased_date,
                ticket.paid_price,
                'purchased'
            )
        )

        if (result_ticket.was_applied
                and result_user.was_applied
                and result_user_and_date.was_applied):
            self.session.execute(self.increment_counter, (
                1,
                uuid.UUID(ticket.event_id),
                ticket.event_day,
            ))
            return ticket
        else:
            raise NotImplementedError('Transaction failed')

    def get_tickets_by_user(self, user_id, status=None):
        if status is not None:
            result = self.session.execute(
                self.user_tickets_status, (
                    user_id,
                    status
                )
            )
        else:
            result = self.session.execute(
                self.user_tickets, (
                    user_id,
                )
            )
        tickets = []
        for row in result.all():
            ticket = Ticket(
                id=str(row.ticket_id),
                user_id=str(row.user_id),
                event_id=str(row.event_id),
                event_day=row.event_day,
                purchased_date=row.purchase_date,
                paid_price=float(row.paid_price),
                status=row.status,
            )
            tickets.append(ticket)
            logger.info(f"ticket: {ticket}")

        return Tickets(tickets=tickets)

    def get_attended_events(self, user_id):
        result = self.session.execute(self.attended_events, (
            user_id,
            datetime.datetime.now(),
            'purchased',
        ))
        n_rows = set(result)
        logger.info(n_rows)
        return len(n_rows)

    def _rollback(self, ticket: Ticket):
        pass


if __name__ == '__main__':
    pass
