import random
import string
import uuid
from datetime import datetime, timedelta

from faker import Faker
from pydantic import BaseModel, Extra

from src.models import Ticket

if __name__ == '__main__':
    pass


def generate_random_name(length=10):
    """Generate a random name."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def generate_random_owner():
    """Generate a random UUID for the owner."""
    return uuid.uuid4()


def generate_random_capacity(min_capacity=20, max_capacity=150):
    """Generate a random capacity within a specified range."""
    return random.randint(min_capacity, max_capacity)


def generate_sample_event_data(owners, num_days=2):
    """Generate sample event data with randomized values."""
    name = generate_random_name()
    start_datetime = datetime.now().date()
    end_datetime = start_datetime + timedelta(days=num_days)

    capacity_by_day = [{"day": (start_datetime + timedelta(days=i)).strftime("%Y-%m-%d"),
                        "max_capacity": generate_random_capacity()} for i in range(num_days)]

    return {
        "owner": owners,
        "name": name,
        "published": random.choice([True, False]),
        "start_datetime": start_datetime.strftime("%Y-%m-%d"),
        "end_datetime": end_datetime.strftime("%Y-%m-%d"),
        "capacity_by_day": capacity_by_day
    }


fake = Faker()


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
