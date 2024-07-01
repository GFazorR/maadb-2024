"""
This module is the main entry point for the application backend.
"""
import logging

from cassandra.cluster import Cluster
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from src import event, analytics, tickets, user, user_session
from src.cql_templates import initialize_cassandra
from src.ticket_service import EventService, AnalyticsService, TicketService

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
app.include_router(analytics.router)

app.engine = engine


# TODO: query mongo and put cached data to redis

@app.on_event('startup')
async def startup():
    """
    This function is called when the app is first started.
    Queries mongodb and caches the result in redis.
    :return: None
    """
    cluster = Cluster(port=9042)
    session = cluster.connect()
    initialize_cassandra(session)
    app.event_service = EventService(session)
    app.analytics_service = AnalyticsService(session)
    app.ticket_service = TicketService(session)


@app.get("/")
async def read_root():
    """
    Default endpoint.
    :return: Response
    """
    return {'message': 'Hello World'}
