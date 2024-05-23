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
import event
import tickets
import telemetry
import user_session
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = AsyncIOMotorClient('mongodb://root:example@localhost:27017/')
engine = AIOEngine(client=client, database='maadb_tickets')

app = FastAPI()
app.include_router(user_session.router)
app.include_router(user.router)
app.include_router(event.router)
app.include_router(tickets.router)
app.include_router(telemetry.router)

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


# ----------------------- Ticket Sale --------------------------------

# Persistence (Cassandra)


# Endpoint to render the registration page as the default view
@app.get("/")
async def read_root():
    return {'message': 'Hello World'}
