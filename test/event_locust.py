import random
import uuid

from locust import HttpUser, task, between

from setup_teardown import created_events, id_list_business
from src.models import EventModel
from test.utils import generate_sample_event_data
local_random = random.Random(1234)


class EventLoadTest(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task
    def create_event(self):
        """Simulate creating an event with capacities."""
        event = EventModel(id=str(uuid.uuid4()), **generate_sample_event_data(local_random.choices(id_list_business,
                                                                                             k=local_random.randint(1, 3))))
        response = self.client.post(
            "/event",
            headers={"Content-Type": "application/json"},
            data=event.json()
        )
        assert response.status_code == 200
        # print(response.json()['id'], event.id)
        # created_events.append(EventModel(**response.json()))

    @task
    def get_event_by_user(self):
        """Simulate getting an event."""
        response = self.client.get("/event/published")
        assert response.status_code == 200 or response.status_code == 404

    @task
    def get_published_event(self):
        """Simulate getting an event."""
        user_id = local_random.choice(id_list_business)
        response = self.client.get(f"/event/{user_id}")
        assert response.status_code == 200

    @task
    def update_event(self):
        """Simulate updating an event, including capacities."""
        event_to_modify = local_random.choice(created_events)
        random_event = generate_sample_event_data(local_random.choices(id_list_business, k=local_random.randint(1, 3)))
        event_to_modify.start_datetime = random_event['start_datetime']
        event_to_modify.end_datetime = random_event['end_datetime']
        event_to_modify.published = True
        event_to_modify.name = random_event['name']
        response = self.client.put(f"/event", data=event_to_modify.json())
        assert response.status_code == 200

    @task
    def delete_event(self):
        """Simulate deleting an event."""
        event = local_random.choice(created_events)
        response = self.client.delete(f"/event", data=event.json())
        assert response.status_code == 204 or response.status_code == 404
        # created_events.remove(event)


if __name__ == '__main__':
    pass
