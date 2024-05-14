import datetime

from pydantic import BaseModel, Field, ValidationError, ConfigDict
from typing import List, Any, Optional, Annotated, Union
from bson.objectid import ObjectId
from pydantic.functional_validators import AfterValidator

PyObjectId = Annotated[
    ObjectId,
    AfterValidator(ObjectId.is_valid),
    AfterValidator(str)
]

class Telemetry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: str = Field(alias="_id")
    participants: int = Field(default_factory=int)


class DayCapacity(BaseModel):
    day: datetime.datetime = Field(..., alias="day")
    max_capacity: int = Field(..., alias="max_capacity")


class Event(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: Union[PyObjectId, str] = Field(default=None, alias="_id")
    name: str
    published: bool = Field(default=False, alias="published")
    capacity_by_date: List[DayCapacity] = Field(default_factory=list)
    start_date: datetime.datetime = Field(default=None, alias="start_date")
    end_date: datetime.datetime = Field(default=None, alias="end_date")


# # Data model for user login information
# class Login(BaseModel):
#     username: str
#     password: str
#

# Data model for user information stored in MongoDB
class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: Union[PyObjectId, str] = Field(default=None, alias="_id")
    username: str


class ClientUser(User):
    attended_events: List[str] = Field(default_factory=list)
    owned_tickets: List[str] = Field(default_factory=list)


class BusinessUser(User):
    owned_events: List[ObjectId] = Field(default_factory=list)


class Ticket(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: str = Field(alias="_id")
    user_id: str
    price: float
    discount: float


class UserSession(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: str = Field(alias="_id")
    user_id: str
    user_profile: User
    event: Event
    ticket_sale: Ticket
    event_telemetry: Telemetry


if __name__ == '__main__':
    pass
