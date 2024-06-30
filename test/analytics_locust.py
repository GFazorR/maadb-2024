import json
import random

from locust import HttpUser, task, between, events
import uuid
import httpx

event_ids = []


@events.test_start.add_listener
def on_test_start(environment):
    for _ in range(100):
        event_id = uuid.uuid4()
        result = httpx.put(f'http://localhost:8000/visits/event?event_id={event_id}')
        if result.status_code == 204:
            event_ids.append(event_id)


class TelemetryUser(HttpUser):
    host = 'http://localhost:8000'
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task
    def get_visits(self):
        event_id = random.choice(event_ids)
        self.client.get(f"/visits/event", params={'event_id': event_id})

    @task
    def update_visits(self):
        event_id = random.choice(event_ids)
        self.client.put(f"/visits/event", params={"event_id": event_id})


if __name__ == "__main__":
    pass
