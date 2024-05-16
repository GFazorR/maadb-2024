import logging
import uuid
from typing import List

from bson.objectid import ObjectId
from fastapi import FastAPI, status, Response
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from odmantic.exceptions import DocumentNotFoundError
import aioredis

from models import Ticket, EventModel, UserModel

# Initialize FastAPI application and templating engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
client = AsyncIOMotorClient('mongodb://root:example@localhost:27017/')
engine = AIOEngine(client=client, database='maadb_tickets')
redis_client = aioredis.from_url('redis://localhost:6379')


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

async def create_session(data: dict):
    # TODO check if session exists, return existing session
    # TODO define data to store in session
    token = str(uuid.uuid4())
    await redis_client.hset(token, mapping=data)
    await redis_client.expire(token, 3600)
    return token


@app.post(
    "/register/business",
)
async def register(username: str):
    # TODO check user exists
    user = UserModel(username=username, role='business')
    user = await engine.save(user)
    return user


@app.get('/user/business/{user_id}')
async def get_user(user_id: str):
    # TODO generate user_session token/id
    user = await engine.find_one(UserModel, {'_id': ObjectId(user_id)})
    session_token = await create_session({'user': user.model_dump_json()})
    return JSONResponse(status_code=status.HTTP_200_OK,
                        headers={'X-Session-Id': session_token},
                        content=user.model_dump_json())


@app.post('/event')
async def save_event(event: EventModel):
    # TODO: add cache
    event = await engine.save(event)
    return event


@app.put('/event')
async def update_event(event: EventModel):
    # TODO: add cache
    # TODO raise exceptions
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
async def get_saved_events(event_id: str):
    try:
        events = await engine.find(EventModel, {'_id': ObjectId(event_id)})
        return Response(status_code=status.HTTP_200_OK, content=events)
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
