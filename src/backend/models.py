from pydantic import BaseModel, Field, ValidationError, ConfigDict
from typing import List, Any
from bson.objectid import ObjectId
from datetime import date


class Telemetry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(default_factory=ObjectId, alias="_id")
    participants: int = Field(default_factory=int)


class DayCapacity(BaseModel):
    day: date = Field(..., alias="day")
    max_capacity: int = Field(..., alias="max_capacity")


class Event(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(default_factory=ObjectId, alias="_id")
    user_id: str = Field(default_factory=ObjectId)
    name: str = Field(default_factory=str)
    capacity_by_date: List[DayCapacity] = Field(default_factory=list)
    start_date: date = Field(default_factory=date)
    end_date: date = Field(default_factory=date)


# # Data model for user login information
# class Login(BaseModel):
#     username: str
#     password: str
#

# Data model for user information stored in MongoDB
class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(default_factory=ObjectId, alias="_id")
    username: str = Field(default_factory=str)
    hashed_password: str = Field(default_factory=str)


class ClientUser(User):
    attended_events: List[ObjectId] = Field(default_factory=list)
    owned_tickets: List[ObjectId] = Field(default_factory=list)


class BusinessUser(User):
    owned_events: List[ObjectId] = Field(default_factory=list)


class Ticket(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(default_factory=ObjectId, alias="_id")
    user_id: str = Field(default_factory=ObjectId)
    price: float = Field(default_factory=float)
    discount: float = Field(default_factory=float)


class UserSession(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(default_factory=ObjectId, alias="_id")
    user_id: str = Field(default_factory=ObjectId)
    user_profile: User = Field(default_factory=User)
    event: Event = Field(default_factory=Event)
    ticket_sale: Ticket = Field(default_factory=Ticket)
    event_telemetry: Telemetry = Field(default_factory=Telemetry)


if __name__ == '__main__':
    pass
