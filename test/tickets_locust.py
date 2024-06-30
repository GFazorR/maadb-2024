import json
import random
import uuid
from datetime import datetime, timedelta

import httpx
from faker import Faker
from locust import HttpUser, task, between, events
from pydantic import BaseModel, Extra
from pydantic.tools import parse_obj_as

from src.models import EventModel, Ticket, Tickets
from test.event_locust import generate_sample_event_data

fake = Faker()

created_events = []


@events.test_start.add_listener
def on_test_start(environment):
    for _ in range(100):
        event = EventModel(id=str(uuid.uuid4()), **generate_sample_event_data())
        event.published = True
        result = httpx.post('http://localhost:8000/event',
                            json=event.model_dump(mode='json'),
                            headers={"Content-Type": "application/json"})
        if result.status_code == 200:
            print(event.id, result.json()['id'])
            created_events.append(event)


def create_random_ticket(event):
    # Generate a random user ID

    # Generate a random ticket price
    ticket_price = 20

    # Generate a random discount
    discount = fake.pyfloat(min_value=0, max_value=1)

    # Calculate the paid price based on discount
    paid_price = ticket_price - (ticket_price * discount)

    # Generate a random event day within the next month
    day = random.choice(event.capacity_by_day)
    # event_day = datetime.strptime(day.day, '%Y-%m-%d').date()

    # Generate a random purchased date close to the current date
    purchased_date = datetime.now() + timedelta(hours=fake.random_int(min=0, max=24))

    # Return a dictionary representing the ticket
    return {
        "ticket_price": ticket_price,
        "discount": discount,
        "paid_price": paid_price,
        "event_day": day.day,
        "purchased_date": purchased_date
    }


class TicketBody(BaseModel, extra=Extra.allow):
    ticket: Ticket
    n_tickets: int = 1


class TicketLoadTest(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks
    tickets = []
    events = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = created_events
        self.id = str(uuid.uuid4())

    def _buy_ticket(self, body: TicketBody, ticket_data: Ticket):

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

    @task
    def buy_ticket(self):
        """Simulate buying a ticket."""
        event = random.choice(self.events)
        ticket_data = Ticket(event_id=str(event.id),
                             user_id=self.id,
                             **create_random_ticket(event))
        body = TicketBody(ticket=ticket_data,
                          capacity=random.choice(event.capacity_by_day),
                          n_tickets=random.randint(1, 5))

        self._buy_ticket(body, ticket_data)

    @task
    def delete_ticket_task(self):
        # Generate a random UUID to simulate a ticket ID
        event = random.choice(self.events)
        ticket_data = Ticket(event_id=str(event.id),
                             user_id=self.id,
                             **create_random_ticket(event))
        body = TicketBody(ticket=ticket_data,
                          capacity=random.choice(event.capacity_by_day),
                          n_tickets=random.randint(1, 5))
        response = self._buy_ticket(body, ticket_data)

        if response is not None:
            response_tickets = json.loads(response.text)
            response_tickets = parse_obj_as(Tickets, response_tickets)

            ticket = random.choice(response_tickets.tickets)
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

    @task
    def get_tickets_by_user(self):
        response = self.client.get(
            f"/ticket/{self.id}",
            params={
                "ticket_status":
                    random.choice(['purchased', 'canceled', None])},
        )
        assert (response is not None and response.status_code == 200)

    @task
    def get_discount(self):
        response = self.client.get(
            f"/discount/{self.id}",
        )
        assert (response is not None and response.status_code == 200)


if __name__ == '__main__':
    pass
