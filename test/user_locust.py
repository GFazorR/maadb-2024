import random
import uuid

from locust import HttpUser, task, between

from setup_teardown import id_list_business, id_list_client

local_random = random.Random(123)


class LoadTestUser(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks
    weight = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task
    def register_business_user(self):
        """Simulate registering a new business user."""
        username = "testBusinessUser" + str(uuid.uuid4())
        response = self.client.post("/register/business", params=f"username={username}")
        assert response.status_code == 200
        # id_list_business.append(response.json()["id"])

    @task
    def get_business_user(self):
        """Simulate getting a business user by ID."""
        user_id = local_random.choice(id_list_business)
        response = self.client.get(f"/user/business", params={'user_id': user_id})
        assert (response.headers.get('X-Session-Id', False)
                and response.status_code == 200)

    @task
    def register_client_user(self):
        """Simulate registering a new client user."""
        username = "testClientUser" + str(uuid.uuid4())
        response = self.client.post("/register/client", params=f"username={username}")
        assert response.status_code == 200
        # id_list_client.append(response.json()["id"])

    @task
    def get_client_users(self):
        """Simulate getting all client users."""
        user_id = local_random.choice(id_list_client)
        response = self.client.get(f"/user/client", params={'user_id': user_id})
        assert (response.headers.get('X-Session-Id', False)
                and response.status_code == 200)

    @task
    def get_tickets_by_user(self):
        response = self.client.get(
            f"/user/tickets",
            params={
                "user_id": local_random.choice(id_list_business + id_list_client),
                "ticket_status":
                    local_random.choice(['purchased', 'canceled', None])},
        )
        assert (response is not None and response.status_code == 200)

    @task
    def get_discount(self):
        user_id = local_random.choice(id_list_business + id_list_client)
        response = self.client.get(
            f"/user/discount",
            params={'user_id': user_id}
        )
        assert (response is not None and response.status_code == 200)


if __name__ == '__main__':
    pass
