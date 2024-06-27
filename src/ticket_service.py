import datetime
import logging
import uuid

from cassandra.cluster import Cluster, ConsistencyLevel
from cassandra.query import SimpleStatement, BatchStatement, BatchType

import cql_templates
from models import EventModel, Ticket, DayCapacityModel, Tickets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cluster = Cluster(port=9042)
session = cluster.connect('ticket_service')


class EventService:
    def __init__(self):
        self.session = session
        self.insert_event = SimpleStatement("""
        UPDATE ticket_service.events
        SET purchased_tickets = purchased_tickets + 0
        WHERE event_id = %s AND event_day = %s
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

    def book_ticket(self,
                    ticket: Ticket,
                    capacity: DayCapacityModel,
                    n_tickets=1):

        initial_purchased = self.session.execute(
            cql_templates.n_tickets,
            (
                uuid.UUID(ticket.event_id),
                capacity.event_day,
            )
        )
        initial_purchased = initial_purchased.one().purchased_tickets

        if initial_purchased + n_tickets <= capacity.max_capacity:
            created_tickets = []
            try:
                for i in range(n_tickets):
                    ticket = self._create_ticket(ticket)
                    logger.info(f'Created ticket {ticket}')
                    created_tickets.append(ticket)

                result = self.session.execute(
                    cql_templates.increment_counter,
                    parameters=(
                        initial_purchased + n_tickets,
                        uuid.UUID(ticket.event_id),
                        ticket.event_day,
                        initial_purchased,
                    )
                )

                if result.was_applied:
                    return created_tickets

            except Exception as e:
                logger.error(e)

            for ticket in created_tickets:
                self._delete_ticket(ticket)
            return False

    def _delete_ticket(self, ticket):
        # TODO
        pass

    def cancel_ticket(self, ticket: Ticket):
        initial_purchased = self.session.execute(
            cql_templates.n_tickets,
            (
                uuid.UUID(ticket.event_id),
                ticket.event_day,
            )
        )
        initial_purchased = initial_purchased.one().purchased_tickets

        batch = BatchStatement(batch_type=BatchType.LOGGED,
                               consistency_level=ConsistencyLevel.ONE)
        batch.add(
            cql_templates.update_ticket,
            parameters=(
                'canceled',
                uuid.UUID(ticket.event_id),
                ticket.event_day,
                uuid.UUID(ticket.user_id),
                uuid.UUID(ticket.id),
            )
        )
        batch.add(
            cql_templates.update_by_user,
            parameters=(
                'canceled',
                uuid.UUID(ticket.user_id),
                uuid.UUID(ticket.id),
            )
        )
        batch.add(
            cql_templates.update_by_user_and_date,
            parameters=(
                'canceled',
                uuid.UUID(ticket.user_id),
                ticket.event_day,
                uuid.UUID(ticket.id),
            )
        )
        try:
            self.session.execute(batch)
            result = self.session.execute(
                cql_templates.increment_counter,
                parameters=(
                    initial_purchased - 1,
                    uuid.UUID(ticket.event_id),
                    ticket.event_day,
                    initial_purchased
                ),
            )
            if result.was_applied:
                return True
        except Exception as e:
            logger.error(e)
        return False

    def _create_ticket(self, ticket):
        ticket.id = uuid.uuid4()
        batch = BatchStatement(batch_type=BatchType.LOGGED,
                               consistency_level=ConsistencyLevel.ONE)
        batch.add(
            cql_templates.insert_ticket,
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
            )
        )
        batch.add(
            cql_templates.insert_by_user,
            parameters=(
                uuid.UUID(ticket.user_id),
                ticket.purchased_date,
                ticket.event_day,
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
                ticket.event_day,
                uuid.UUID(ticket.event_id),
                ticket.id,
                ticket.purchased_date,
                ticket.paid_price,
                'purchased'
            )
        )
        result = self.session.execute(batch)
        logger.info(list(result))
        return ticket

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
                event_day=row.event_day,
                purchased_date=row.purchase_date,
                paid_price=float(row.paid_price),
                status=row.status,
            )
            tickets.append(ticket)
            logger.info(f"ticket: {ticket}")

        return Tickets(tickets=tickets)

    def get_attended_events(self, user_id):
        result = self.session.execute(
            cql_templates.attended_events,
            (
                user_id,
                datetime.datetime.now(),
                'purchased',
            ))
        n_rows = set(result)
        logger.info(n_rows)
        return len(n_rows)


if __name__ == '__main__':
    pass
