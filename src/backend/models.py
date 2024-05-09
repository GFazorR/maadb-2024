from pydantic import BaseModel, Field
from typing import List
from bson.objectid import ObjectId
from datetime import date


class Telemetry(BaseModel):
    pass


class DayCapacity(BaseModel):
    day: date
    max_capacity: int


class Event(BaseModel):
    id: ObjectId = Field(description="Id of the event", alias="_id")
    user_id: ObjectId = Field(description="Id of the user", alias="_id")
    name: str
    capacity_by_date: List[DayCapacity]
    start_date: date
    end_date: date


# Data model for user login information
class Login(BaseModel):
    username: str
    password: str


# Data model for user information stored in MongoDB
class User(BaseModel):
    username: str
    hashed_password: str


class ClientUser(User):
    attended_events: List[ObjectId]
    owned_tickets: List[ObjectId]


class BusinessUser(User):
    owned_events: List[ObjectId]


class Ticket(BaseModel):
    event_id: ObjectId = Field(description="Id of the event", alias="_id")
    user_id: ObjectId = Field(description="Id of the user", alias="_id")
    price: float
    discount: float


class UserSession(BaseModel):
    user_id: str
    user_profile: User
    event: Event
    ticket_sale: Ticket
    event_telemetry: Telemetry


if __name__ == '__main__':
    pass
