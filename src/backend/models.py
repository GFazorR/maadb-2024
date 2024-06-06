"""
This module contains the data models used in the application.
"""
import datetime
from typing import List

from bson import ObjectId
from odmantic import Model, EmbeddedModel
from pydantic import BaseModel, Field, ConfigDict, Extra

from src.backend import event


class UserModel(Model):
    """
    This class represents the user model.
    :param username: str    :param role: str
    """
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
    day: datetime.datetime
    max_capacity: int


class EventModel(Model, extra=Extra.allow):
    """
    This class represents the event model.
    :param owner: List[ObjectId]
    :param name: str
    :param published: bool
    :param capacity_by_day: List[DayCapacityModel]
    :param start_datetime: datetime    :param end_datetime: datetime
    """
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
    """
    This class represents the telemetry model.
    :param participants: int
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    participants: int = Field(default_factory=int)


class Ticket(BaseModel):
    """
    This class represents the ticket model.
    :param user_id: str    :param event_id: str
    :param price: float    :param discount: float
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    user_id: str
    event_id: str
    price: float
    discount: float


class UserSession(BaseModel):
    """
    This class represents the user session model.
    :param id: str    :param user_id: str
    :param user_profile: UserModel
    :param event: EventModel
    :param ticket_sale: TicketModel
    :param event_telemetry: TelemetryModel
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: str = Field(alias="_id")
    user_id: str
    user_profile: UserModel
    event: EventModel
    ticket_sale: Ticket
    event_telemetry: Telemetry


if __name__ == '__main__':
    pass
