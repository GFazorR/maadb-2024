import json
import random

from locust import HttpUser, task, between
from pydantic.tools import parse_obj_as

from setup_teardown import created_events, id_list_client
from src.models import Ticket, Tickets
from test.utils import create_random_ticket, TicketBody

local_random = random.Random(1234)


class TicketLoadTest(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks
    weight = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _buy_ticket(self):
        event = local_random.choice(created_events)
        ticket_data = Ticket(event_id=str(event.id),
                             user_id=local_random.choice(id_list_client),
                             **create_random_ticket(event))
        body = TicketBody(ticket=ticket_data,
                          capacity=local_random.choice(event.capacity_by_day),
                          n_tickets=local_random.randint(1, 5))
        response = self.client.post("/ticket",
                                    data=body.json(),
                                    headers={"Content-Type": "application/json"})

        assert (response is not None
                and response.status_code == 201
                or response.status_code == 226)

        if response.status_code == 201:
            response = self.client.post(
                '/ticket/confirm',
                data=ticket_data.json(),
                params=str(body.n_tickets),
                headers={"Content-Type": "application/json"})
            assert (response is not None
                    and response.status_code == 201)
            return response

    @task(5)
    def buy_ticket(self):
        """Simulate buying a ticket."""
        self._buy_ticket()

    @task(1)
    def delete_ticket_task(self):

        response = self._buy_ticket()

        if response is not None:
            response_tickets = json.loads(response.text)
            response_tickets = parse_obj_as(Tickets, response_tickets)

            ticket = local_random.choice(response_tickets.tickets)
            response = self.client.delete(
                "/ticket",
                data=ticket.json(),
                headers={"Content-Type": "application/json"}
            )
            assert (response is not None
                    and response.status_code == 204)
            response = self.client.delete(
                "/ticket/confirm",
                data=ticket.json(),
                headers={"Content-Type": "application/json"}
            )
            assert (response is not None
                    and response.status_code == 204)


if __name__ == '__main__':
    pass
