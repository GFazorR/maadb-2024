import json
import random
import uuid
from time import sleep

import httpx
from faker import Faker
from locust import events
from pydantic.tools import parse_obj_as

from src.models import UserModel, EventModel
from test.utils import generate_sample_event_data

fake = Faker()
local_random = random.Random(1234)

n_events = 50
n_users = 50

id_list_business = []
id_list_client = []
created_events = []
tickets = []


@events.test_start.add_listener
def populate_business_users(environment):
    for _ in range(n_users):
        response = httpx.post("http://localhost:8000/register/business",
                              params={'username': fake.user_name()})
        if response.status_code == 200:
            response_user = json.loads(response.text)
            user = parse_obj_as(UserModel, response_user)
            id_list_business.append(str(user.id))
            # print(user)


@events.test_start.add_listener
def populate_client_users(environment):
    for _ in range(n_users):
        response = httpx.post("http://localhost:8000/register/client",
                              params={'username': fake.user_name()})
        if response.status_code == 200:
            response_user = json.loads(response.text)
            user = parse_obj_as(UserModel, response_user)
            id_list_client.append(str(user.id))
            # print(user)


@events.test_start.add_listener
def populate_events(environment):
    for _ in range(n_events):
        event = EventModel(id=str(uuid.uuid4()),
                           **generate_sample_event_data(local_random.choices(
                               id_list_business,
                               k=local_random.randint(
                                   1, 3))))
        event.published = True
        result = httpx.post('http://localhost:8000/event',
                            json=event.model_dump(mode='json'),
                            headers={"Content-Type": "application/json"})
        # print(result)
        if result.status_code == 200:
            # print(event.id, result.json()['id'])
            created_events.append(EventModel(**result.json()))
    sleep(1)
