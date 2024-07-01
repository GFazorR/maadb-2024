import random

from locust import HttpUser, task, between

from setup_teardown import id_list_business, id_list_client
from src.models import EventModel
from test.utils import generate_sample_event_data

local_random = random.Random(123)


class LoadTestUserSession(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks
    weight = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task(3)
    async def get_user_session(self):
        """Simulate getting a session."""
        user_id = local_random.choice(id_list_business + id_list_client)
        response = self.client.get(f"/session/events/{user_id}", name="/session/events/{user_id}")
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    @task(1)
    async def create_user_session(self):
        """Simulate creating/updating a session."""
        data = generate_sample_event_data(local_random.choices(id_list_business, k=local_random.randint(1, 3)))
        user_id = local_random.choice(data['owners'])
        event_model = EventModel(**data)  # Assuming EventModel has fields matching event_data keys
        response = self.client.put(
            f"/session/events/",
            params=user_id,
            data=event_model,
            headers={"Content-Type": "application/json"},
            name="/session/events/{user_id}"
        )
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"


if __name__ == '__main__':
    pass
