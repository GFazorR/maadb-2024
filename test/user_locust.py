import random
import uuid

from locust import HttpUser, task, between, events
import json

from src.models import UserModel
from pydantic.tools import parse_obj_as
import httpx

id_list_business = []
id_list_client = []


@events.test_start.add_listener
def on_test_start(environment):
    for _ in range(50):
        username = "testBusinessUser" + str(uuid.uuid4())
        response = httpx.post("http://localhost:8000/register/business",
                              params={'username': username})
        if response.status_code == 200:
            response_user = json.loads(response.text)
            user = parse_obj_as(UserModel, response_user)
            id_list_business.append(str(user.id))
            print(user)
        response = httpx.post("http://localhost:8000/register/client",
                              params={'username': username})
        if response.status_code == 200:
            response_user = json.loads(response.text)
            user = parse_obj_as(UserModel, response_user)
            id_list_client.append(str(user.id))
            print(user)


class LoadTestUser(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task
    def register_business_user(self):
        """Simulate registering a new business user."""
        username = "testBusinessUser" + str(uuid.uuid4())
        response = self.client.post("/register/business", params=f"username={username}")
        assert response.status_code == 200
        id_list_business.append(response.json()["id"])

    @task
    def get_business_user(self):
        """Simulate getting a business user by ID."""
        user_id = random.choice(id_list_business)
        response = self.client.get(f"/user/business/{user_id}")
        assert (response.headers.get('X-Session-Id', False)
                and response.status_code == 200)

    @task
    def register_client_user(self):
        """Simulate registering a new client user."""
        username = "testClientUser" + str(uuid.uuid4())
        response = self.client.post("/register/client", params=f"username={username}")
        assert response.status_code == 200
        id_list_client.append(response.json()["id"])

    @task
    def get_client_users(self):
        """Simulate getting all client users."""
        user_id = random.choice(id_list_client)
        response = self.client.get(f"/user/client/{user_id}")
        assert (response.headers.get('X-Session-Id', False)
                and response.status_code == 200)


if __name__ == '__main__':
    pass
