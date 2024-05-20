import json
import logging
import uuid
from typing import List, Annotated, Union

from bson.objectid import ObjectId
from fastapi import FastAPI, status, Response, Header, Depends, Cookie, BackgroundTasks
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from odmantic.exceptions import DocumentNotFoundError

from models import Ticket, EventModel, UserModel
import user

# Initialize FastAPI application and templating engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = AsyncIOMotorClient('mongodb://root:example@localhost:27017/')
engine = AIOEngine(client=client, database='maadb_tickets')

app = FastAPI()
app.include_router(user.router)
app.engine = engine



# templates = Jinja2Templates(directory="templates")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
#
# # Mock Redis client for development purposes (replace with actual connection)
# redis_client = redis.Redis(host='localhost', port=6379, db=0)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def hash_password(password: str) -> str:
#     hashed_password = pwd_context.hash(password)
#     print(f"Hashed password: {hashed_password}")  # Log hashed password for debugging (remove in production)
#     return hashed_password


# # Endpoint for user registration
# @app.post("/register")
# async def register(user: User):
#     hashed_password = hash_password(user.password)
#     users_collection = app.maadb_database['maadb_users']  # Replace with your actual collection name
#     result = users_collection.insert_one({"username": user.username, "hashed_password": hashed_password})
#     if result.inserted_id:
#         return {"message": "User created successfully!"}
#     else:
#         raise HTTPException(status_code=400, detail="User registration failed")
#
#
# # Endpoint for user login with JWT authentication
# @app.post("/login")
# async def login(user: Login = Depends(oauth2_scheme)):
#     print("serving Login page")
#     users_collection = app.maadb_database['maadb_users']  # Replace with your actual collection name
#     found_user = users_collection.find_one({"username": user.username})
#
#     if not found_user:
#         raise HTTPException(status_code=400, detail="Invalid username or password")
#
#     if not pwd_context.verify(user.password, found_user["hashed_password"]):
#         raise HTTPException(status_code=400, detail="Invalid username or password")
#
#     # JWT logic for access token generation and session management (omitted for brevity)
#
#     # Redirect to user profile on successful login (adapt based on your needs)
#     response = Response()
#     response.headers["Location"] = "/user_profile"
#     response.status_code = status.HTTP_302_FOUND  # Set redirect status code
#     return response


# ----------------------- Event Creation --------------------------------

# Persistence (MongoDB)


@app.post('/event')
async def save_event(background_task: BackgroundTasks, event: EventModel,
                     header: Annotated[Union[str, None], Header()] = None):
    print(type(header), header)
    user = await get_session(session_id=header)
    if not event.owner:
        event.owner.append(user.id)
    event = await engine.save(event)
    background_task.add_task(set_cache, event)
    return event


@app.put('/event')
async def update_event(event: EventModel):
    # TODO: add cache
    event = await engine.save(event)
    return event


@app.delete('/event')
async def delete_event(event: EventModel):
    # TODO: add cache
    # TODO: make it transactional ?
    try:
        _ = await engine.delete(event)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@app.get('/event')
async def get_saved_events(background_task: BackgroundTasks, event_id: str):
    events = await get_cache(event_id)
    if events:
        return Response(status_code=status.HTTP_200_OK, content=events)

    try:
        events = await engine.find(EventModel, {'_id': ObjectId(event_id)})
        event = events[0]
        print(type(event), event)
        background_task.add_task(set_cache, event)
        return Response(status_code=status.HTTP_200_OK, content=event.model_dump_json())
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@app.get('/event/published', response_model=List[EventModel])
async def get_published_events():
    try:
        events = await engine.find(EventModel, {'published': True})
        return events
    except DocumentNotFoundError as e:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


@app.get('/event/{user_id}', response_model=List[EventModel])
async def get_event(user_id: str):
    events = await engine.find(EventModel, {'owner': ObjectId(user_id)})
    return events


# ----------------------- Ticket Sale --------------------------------

# Persistence (Cassandra)
@app.post('/ticket/buy')
async def buy_ticket(ticket: Ticket):
    pass


@app.put('/ticket/buy')
async def update_ticket(ticket: Ticket):
    pass


@app.delete('/ticket/buy')
async def delete_ticket(ticket: Ticket):
    pass


@app.get('/ticket/buy')
async def read_ticket(ticket_id: str):
    pass


# ----------------------- Telemetry --------------------------------
# Persistence (Cassandra)
@app.get('/event/telemetry')
async def read_telemetry():
    pass


@app.get('/profile/attended_events')
async def read_attended_events():
    pass


@app.get('/profile/discount')
async def read_discount():
    pass


# Endpoint to render the registration page as the default view
@app.get("/")
async def read_root():
    return {'message': 'Hello World'}
