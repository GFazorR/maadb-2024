"""
This module is the main entry point for the application backend.
"""

import logging

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

import event
import telemetry
import tickets
import user
import user_session

"""
Initialize logging, mongodb and FastApi routing.
"""
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = AsyncIOMotorClient('mongodb://root:example@localhost:27017/',
                            uuidRepresentation='standard')
engine = AIOEngine(client=client, database='maadb_tickets')




app = FastAPI()
app.include_router(user_session.router)
app.include_router(user.router)
app.include_router(event.router)
app.include_router(tickets.router)
app.include_router(telemetry.router)

app.engine = engine


# TODO: query mongo and put cached data to redis

@app.on_event('startup')
async def startup():
    """
    This function is called when the app is first started.
    Queries mongodb and caches the result in redis.
    :return: None
    """
    # query monogo
    # cache on redis
    pass


@app.on_event('shutdown')
async def shutdown():
    """
    This function is called when the app shutdown.
    Persists redis dataa in mongodb database.
    :return: None
    """
    # persist on mongo
    pass


@app.get("/")
async def read_root():
    """
    Default endpoint.
    :return: Response
    """
    return {'message': 'Hello World'}
