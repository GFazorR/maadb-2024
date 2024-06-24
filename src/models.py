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
    day: datetime.datetime
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
    id: uuid.UUID = Field(primary_field=True, default=uuid.uuid4())
    owner: List[uuid.UUID]
    name: str
    published: bool
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    capacity_by_day: List[DayCapacityModel] = []
    model_config = {
        'collection': 'events_collection'
    }

    # def populate_capacity_by_day(self):
    #     self.capacity_by_day = []
    #     for x in range((self.end_datetime - self.start_datetime).days):
    #         self.capacity_by_day.append(DayCapacityModel(
    #             day=self.start_datetime + datetime.timedelta(days=x),
    #             max_capacity=self.__pydantic_extra__.get('max_capacity', 100),
    #             price=self.__pydantic_extra__.get('price', 10.0)
    #         ))


class Telemetry(BaseModel):
    """
    This class represents the telemetry model.
    :param participants: int
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    participants: int = Field(default_factory=int)


class Ticket(BaseModel, extra='allow'):
    """
    This class represents the ticket model.
    :param user_id: str    :param id: str
    :param price: float    :param discount: float
    """
    event_id: str
    user_id: str
    ticket_price: float
    discount: float
    paid_price: float
    event_day: datetime.datetime
    purchased_date: datetime.datetime


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
    id: str
    user_id: str
    user_profile: UserModel
    event: EventModel
    ticket_sale: Ticket
    event_telemetry: Telemetry


if __name__ == '__main__':
    pass
