import datetime
import logging
import uuid

from cassandra.cluster import Cluster, ConsistencyLevel
from cassandra.query import SimpleStatement, BatchStatement, BatchType

from src import cql_templates
from src.models import EventModel, Ticket, DayCapacityModel, Tickets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cluster = Cluster(port=9042)
session = cluster.connect('ticket_service')


class EventService:
    def __init__(self):
        self.session = session
        self.insert_event = SimpleStatement("""
        INSERT INTO inventory.events ("event_id", "event_day", "purchased_tickets")
        VALUES (%s, %s, 0)
        """)

    def create_event(self, event: EventModel):
        for cap in event.capacity_by_day:
            self.session.execute(
                self.insert_event,
                (
                    event.id,
                    datetime.datetime.strptime(cap.day, "%Y-%m-%d").date(),
                ))


class TelemetryService:
    def __init__(self):
        self.session = session
        self.query_update_counter = SimpleStatement("""
        UPDATE inventory.user_visits
        SET page_visits = page_visits + 1
        WHERE event_id = %s
        """)

        self.query_counter = SimpleStatement("""
        SELECT page_visits
        FROM inventory.user_visits
        WHERE event_id = %s
        """)

    def update_counter(self, event_id):
        self.session.execute(
            self.query_update_counter,
            (event_id,)
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

    def lock_tickets(
            self,
            ticket: Ticket,
            max_capacity: int,
            n_tickets=1
    ):
        initial_purchased = self.session.execute(
            cql_templates.n_tickets,
            (
                uuid.UUID(ticket.event_id),
                datetime.datetime.strptime(ticket.event_day,
                                           '%Y-%m-%d').date(),
            )
        )
        initial_purchased = initial_purchased.one().purchased_tickets

        if not (initial_purchased + n_tickets < max_capacity):
            raise ValueError("Capacity exceeds max capacity")

        result = self.session.execute(
            cql_templates.increment_counter,
            parameters=(
                initial_purchased + n_tickets,
                uuid.UUID(ticket.event_id),
                datetime.datetime.strptime(ticket.event_day,
                                           '%Y-%m-%d').date(),
                initial_purchased,
            )
        )
        if result.was_applied:
            return True
        return False

    def book_tickets(
            self,
            ticket: Ticket,
            n_tickets=1
    ):
        created_tickets = []
        batch = BatchStatement(batch_type=BatchType.LOGGED,
                               consistency_level=ConsistencyLevel.LOCAL_QUORUM)
        for i in range(n_tickets):
            ticket.id = uuid.uuid4()
            batch.add(
                cql_templates.insert_ticket,
                parameters=(
                    uuid.UUID(ticket.event_id),
                    datetime.datetime.strptime(ticket.event_day, "%Y-%m-%d").date(),
                    ticket.purchased_date,
                    uuid.UUID(ticket.user_id),
                    ticket.id,
                    ticket.ticket_price,
                    ticket.discount,
                    ticket.paid_price,
                    'purchased'
                )
            )
            batch.add(
                cql_templates.insert_by_user,
                parameters=(
                    uuid.UUID(ticket.user_id),
                    ticket.purchased_date,
                    datetime.datetime.strptime(ticket.event_day, "%Y-%m-%d").date(),
                    uuid.UUID(ticket.event_id),
                    ticket.id,
                    ticket.paid_price,
                    'purchased'
                )
            )
            batch.add(
                cql_templates.insert_by_user_and_date,
                parameters=(
                    uuid.UUID(ticket.user_id),
                    datetime.datetime.strptime(ticket.event_day, "%Y-%m-%d").date(),
                    uuid.UUID(ticket.event_id),
                    ticket.id,
                    ticket.purchased_date,
                    ticket.paid_price,
                    'purchased'
                )
            )
            created_tickets.append(ticket)
        self.session.execute(batch)

        return created_tickets

    def decrement_tickets(
            self,
            ticket: Ticket,
    ):
        initial_purchased = self.session.execute(
            cql_templates.n_tickets,
            (
                uuid.UUID(ticket.event_id),
                datetime.datetime.strptime(ticket.event_day,
                                           '%Y-%m-%d').date(),
            )
        )
        initial_purchased = initial_purchased.one().purchased_tickets

        result = self.session.execute(
            cql_templates.increment_counter,
            parameters=(
                initial_purchased - 1,
                uuid.UUID(ticket.event_id),
                datetime.datetime.strptime(ticket.event_day,
                                           '%Y-%m-%d').date(),
                initial_purchased,
            )
        )

        if result.was_applied:
            return True
        return False

    def cancel_ticket(self, ticket: Ticket):

        ticket.id = uuid.UUID(ticket.id)

        batch = BatchStatement(batch_type=BatchType.LOGGED,
                               consistency_level=ConsistencyLevel.ONE)

        batch.add(
            cql_templates.update_ticket,
            parameters=(
                'canceled',
                uuid.UUID(ticket.event_id),
                datetime.datetime.strptime(ticket.event_day, "%Y-%m-%d").date(),
                uuid.UUID(ticket.user_id),
                ticket.id,
            )
        )
        batch.add(
            cql_templates.update_by_user,
            parameters=(
                'canceled',
                uuid.UUID(ticket.user_id),
                ticket.id,
            )
        )
        batch.add(
            cql_templates.update_by_user_and_date,
            parameters=(
                'canceled',
                uuid.UUID(ticket.user_id),
                datetime.datetime.strptime(ticket.event_day, "%Y-%m-%d").date(),
                ticket.id,
            )
        )
        self.session.execute(batch)
        return True

    def get_tickets_by_user(self, user_id, status=None):
        if status is not None:
            result = self.session.execute(
                cql_templates.user_tickets_status,
                (
                    user_id,
                    status
                )
            )
        else:
            result = self.session.execute(
                cql_templates.user_tickets,
                (user_id,)
            )
        tickets = []
        for row in result.all():
            ticket = Ticket(
                id=str(row.ticket_id),
                user_id=str(row.user_id),
                event_id=str(row.event_id),
                event_day=row.event_day.date().strftime("%Y-%m-%d"),
                purchased_date=row.purchase_date,
                paid_price=float(row.paid_price),
                status=row.status,
            )
            tickets.append(ticket)

        return Tickets(tickets=tickets)

    def get_attended_events(self, user_id):
        result = self.session.execute(
            cql_templates.attended_events,
            (
                user_id,
                datetime.datetime.now().date(),
                'purchased',
            ))
        n_rows = set(result)
        return len(n_rows)


if __name__ == '__main__':
    pass
