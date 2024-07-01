import random

from locust import HttpUser, task, between

from setup_teardown import created_events

local_random = random.Random(123)


class AnalyticsUser(HttpUser):
    host = 'http://localhost:8000'
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    weight = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task
    def get_visits(self):
        event = local_random.choice(created_events)
        self.client.get(f"/visits/event", params={'event_id': event.id})

    @task
    def update_visits(self):
        event = local_random.choice(created_events)
        self.client.put(f"/visits/event", params={"event_id": event.id})


if __name__ == "__main__":
    pass
