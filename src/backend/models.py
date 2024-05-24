import datetime
from typing import List, Union, Optional

from odmantic import Model, EmbeddedModel, Reference
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class UserModel(Model):
    username: str
    role: str

    model_config = {
        'collection': 'users'
    }


class DayCapacityModel(EmbeddedModel):
    day: datetime.datetime
    max_capacity: int


# TODO make model flexible
class EventModel(Model):
    owner: List[ObjectId]
    name: str
    published: bool
    capacity_by_day: List[DayCapacityModel] = []
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    model_config = {
        'collection': 'events_collection'
    }


class Telemetry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    participants: int = Field(default_factory=int)


# # Data model for user login information
# class Login(BaseModel):
#     username: str
#     password: str
#


class Ticket(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    user_id: str
    price: float
    discount: float


class UserSession(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: str = Field(alias="_id")
    user_id: str
    user_profile: UserModel
    event: EventModel
    ticket_sale: Ticket
    event_telemetry: Telemetry


if __name__ == '__main__':
    pass
