import random

from locust import HttpUser, task, between

from src.models import EventModel
from test.event_locust import generate_sample_event_data
from user_locust import LoadTestUser


class LoadTestUserSession(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task
    async def get_session(self):
        """Simulate getting a session."""
        user_id = random.choice(LoadTestUser.id_list)
        response = self.client.get(f"/session/events/{user_id}", name="/session/events/{user_id}")
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    @task
    async def create_session(self):
        """Simulate creating/updating a session."""
        data = generate_sample_event_data()
        user_id = data['owners'][0]
        event_model = EventModel(**data)  # Assuming EventModel has fields matching event_data keys
        response = self.client.put(
            f"/session/events/",
            params=user_id,
            data=event_model,
            headers={"Content-Type": "application/json"},
            name="/session/events/{user_id}"
        )
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
