"""
This module contains the data models used in the application.
"""
import datetime
import uuid
from typing import List

from odmantic import Model, EmbeddedModel, Field
from pydantic import BaseModel, ConfigDict, Extra


class UserModel(Model, extra=Extra.allow):
    """
    This class represents the user model.
    :param username: str    :param role: str
    """
    id: uuid.UUID = Field(primary_field=True, default=uuid.uuid4())
    username: str
    role: str

    model_config = {
        'collection': 'users'
    }


class DayCapacityModel(EmbeddedModel):
    """
    This class represents the day capacity model.
    :param day: datetime
    :param max_capacity: int
    """
    day: str
    max_capacity: int = 100
    price: float = 10.0


class EventModel(Model, extra=Extra.allow):
    """
    This class represents the event model.
    :param owner: List[UUID]
    :param name: str
    :param published: bool
    :param capacity_by_day: List[DayCapacityModel]
    :param start_datetime: datetime    :param end_datetime: datetime
    """
    id: uuid.UUID = Field(primary_field=True)
    owner: List[uuid.UUID]
    name: str
    published: bool
    start_datetime: str
    end_datetime: str
    capacity_by_day: List[DayCapacityModel] = []
    model_config = {
        'collection': 'events_collection'
    }


class Ticket(BaseModel, extra='allow'):
    """
    This class represents the ticket model.
    :param user_id: str    :param id: str
    :param price: float    :param discount: float
    """
    event_id: str
    user_id: str
    ticket_price: float = 20
    discount: float = 0.0
    paid_price: float = 20
    event_day: str
    purchased_date: datetime.datetime


class UserSession(BaseModel):
    """
    This class represents the user session model.
    :param id: str    :param user_id: str
    :param user_profile: UserModel
    :param event: EventModel
    :param ticket_sale: TicketModel
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: str
    user_id: str
    user_profile: UserModel
    event: EventModel
    ticket_sale: Ticket


class EventDayStats(BaseModel):
    event_id: uuid.UUID
    event_day: str
    purchased_tickets: int


class EventStats(BaseModel):
    days: List[EventDayStats]


class Tickets(BaseModel):
    tickets: List[Ticket]


if __name__ == '__main__':
    pass
