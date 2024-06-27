import random
import uuid

from locust import HttpUser, task, between
import json


class LoadTestUser(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks
    id_list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task
    def register_business_user(self):
        """Simulate registering a new business user."""
        username = "testBusinessUser" + str(uuid.uuid4())
        result = self.client.post("/register/business", params=f"username={username}")
        self.id_list.append(result.json()["id"])

    @task
    def get_business_user(self):
        """Simulate getting a business user by ID."""
        print(self.id_list)
        user_id = random.choice(self.id_list)
        response = self.client.get(f"/user/business/{user_id}")
        print(response.headers)  # Optionally print the response for debugging purposes