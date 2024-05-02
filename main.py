from typing import List
from bson.objectid import ObjectId
import riak
from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel, Field
import pymongo


app = FastAPI()


class DayCapacity(BaseModel):
    day: date
    max_capacity: int


class Event(BaseModel):
    id: ObjectId = Field(description="Id of the event", alias="_id")
    name: str
    capacity_by_date: List[DayCapacity]
    start_date: date
    end_date: date



@app.get("/")
async def root():
    return {"message": "Hello World"}
