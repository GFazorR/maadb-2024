import random
import string
import uuid
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
import httpx

from src.models import EventModel

created_events = []


@events.test_start.add_listener
def on_test_start(environment):
    for _ in range(10):
        event = EventModel(id=uuid.uuid4(), **generate_sample_event_data())
        result = httpx.post('http://localhost:8000/event',
                            json=event.model_dump(mode='json'),
                            headers={"Content-Type": "application/json"})
        if result.status_code == 200:
            created_events.append(event)
    print(created_events)


def generate_random_name(length=10):
    """Generate a random name."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_owner():
    """Generate a random UUID for the owner."""
    return uuid.uuid4()


def generate_random_capacity(min_capacity=20, max_capacity=150):
    """Generate a random capacity within a specified range."""
    return random.randint(min_capacity, max_capacity)


def generate_sample_event_data(num_days=2):
    """Generate sample event data with randomized values."""
    owners = [generate_random_owner(), generate_random_owner()]
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


# Example usage


class EventLoadTest(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks

    user_ids = [uuid.uuid4() for _ in range(20)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_id_list = created_events

    @task
    def create_event(self):
        """Simulate creating an event with capacities."""
        event = EventModel(id=random.choice(self.user_ids), **generate_sample_event_data())
        response = self.client.post(
            "/event",
            headers={"Content-Type": "application/json"},
            data=event.json()
        )
        assert response.status_code == 200
        self.event_id_list.append(EventModel(**response.json()))

    @task
    def get_event_by_user(self):
        """Simulate getting an event."""
        response = self.client.get("/event/published")
        assert response.status_code == 200 or response.status_code == 404

    @task
    def get_published_event(self):
        """Simulate getting an event."""
        user_id = random.choice(self.user_ids)
        response = self.client.get(f"/event/{user_id}")
        assert response.status_code == 200

    @task
    def update_event(self):
        """Simulate updating an event, including capacities."""
        event = EventModel(id=random.choice(self.user_ids), **generate_sample_event_data())
        response = self.client.put(f"/event", data=event.json())
        assert response.status_code == 200

    @task
    def delete_event(self):
        """Simulate deleting an event."""
        event = random.choice(self.event_id_list)
        response = self.client.delete(f"/event", data=event.json())
        assert response.status_code == 204 or response.status_code == 404
        self.event_id_list.remove(event)
