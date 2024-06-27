import random
import uuid

from locust import HttpUser, task, between
import json


class FastApiLoadTestUser(HttpUser):
    host = 'http://localhost:8000'  # Add this line
    wait_time = between(1, 2.5)  # Wait time between tasks
    id_list = []

    def __init__(self, id_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unique_id = str(uuid.uuid4())  # Assign a unique ID to each user instance
        id_list.append(self.unique_id)
    @task
    def register_business_user(self):
        """Simulate registering a new business user."""
        username = "testBusinessUser" + str(self.unique_id)
        self.client.post("/register/business", params = "username" + username)

    @task
    def get_business_user(self, id_list):
        """Simulate getting a business user by ID."""
        user_id = random.choice(id_list)
        response = self.client.get(f'/user/business/{user_id}')
        print(response.json())  # Optionally print the response for debugging purposes

    @task
    def get_session(self):
        """Simulate getting a session by user ID."""
        response = self.client.get(f"/session/events/{self.user_id}")
        print(response.json())  # Optionally print the response for debugging purposes

    @task
    def create_session(self):
        """Simulate creating/updating a session for a user."""
        event_data = {
            "title": "Sample Session",
            "description": "A sample session description.",
            "start_time": "2024-07-01T10:00:00Z",
            "end_time": "2024-07-01T12:00:00Z"
        }
        self.client.put(f"/session/events/{self.user_id}", json=event_data)

    @task
    def delete_session(self):
        """Simulate deleting a session for a user."""
        self.client.delete(f"/session/events/{self.user_id}")

    @task
    def post_event(self):
        """Simulate posting an event."""
        event_data = {
            "title": "Sample Event",
            "description": "A sample event description.",
            "start_time": "2024-07-01T10:00:00Z",
            "end_time": "2024-07-01T12:00:00Z"
        }
        self.client.post("/event", json=event_data)

    @task
    def put_event(self):
        """Simulate updating an existing event."""
        event_id = "some-event-id"  # Replace with actual event ID
        event_data = {
            "title": "Updated Event Title",
            "description": "An updated event description."
        }
        self.client.put(f"/event/{event_id}", json=event_data)

    @task
    def delete_event(self):
        """Simulate deleting an event."""
        event_id = "some-event-id"  # Replace with actual event ID
        self.client.delete(f"/event/{event_id}")

    @task
    def get_all_events(self):
        """Simulate getting all saved events."""
        self.client.get("/event")

    @task
    def get_published_events(self):
        """Simulate getting all published events."""
        self.client.get("/event/published")

    @task
    def get_user_events(self):
        """Simulate getting events for a specific user."""
        user_id = "some-user-id"  # Replace with actual user ID
        self.client.get(f"/event/{user_id}")
