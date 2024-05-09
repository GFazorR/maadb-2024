import os
from typing import List

import redis
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi import status, Response
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from pymongo import MongoClient
from models import Login, User, Event, Ticket, ClientUser
from bson.objectid import ObjectId

# Initialize FastAPI application and templating engine
app = FastAPI()
templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Mock Redis client for development purposes (replace with actual connection)
redis_client = redis.Redis(host='localhost', port=6379, db=0)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    hashed_password = pwd_context.hash(password)
    print(f"Hashed password: {hashed_password}")  # Log hashed password for debugging (remove in production)
    return hashed_password


# Function to retrieve a MongoClient instance using the MONGO_URL environment variable
def get_mongo_client():
    client = MongoClient(os.environ.get("MONGO_URL"))
    return client.your_database_name  # Replace with your actual database name


# Endpoint for user registration
@app.post("/register")
async def register(user: User):
    hashed_password = hash_password(user.password)
    db = get_mongo_client()
    users_collection = db.users  # Replace with your actual collection name
    result = users_collection.insert_one({"username": user.username, "hashed_password": hashed_password})
    if result.inserted_id:
        return {"message": "User created successfully!"}
    else:
        raise HTTPException(status_code=400, detail="User registration failed")


# Endpoint for user login with JWT authentication
@app.post("/login")
async def login(user: Login = Depends(oauth2_scheme)):
    print("serving Login page")
    db = get_mongo_client()
    users_collection = db.users  # Replace with your actual collection name
    found_user = users_collection.find_one({"username": user.username})

    if not found_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not pwd_context.verify(user.password, found_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # JWT logic for access token generation and session management (omitted for brevity)

    # Redirect to user profile on successful login (adapt based on your needs)
    response = Response()
    response.headers["Location"] = "/user_profile"
    response.status_code = status.HTTP_302_FOUND  # Set redirect status code
    return response


# ----------------------- Event Creation --------------------------------

# User session (redis)
@app.post('/event')
async def create_event(event: Event):
    pass


@app.put('/event')
async def update_event(event: Event):
    pass


@app.delete('/event')
async def delete_event(event: Event):
    pass


@app.get('/event')
async def read_event(key: ObjectId):
    pass


# Persistence (MongoDB)
@app.post('/event/publish')
async def publish_event(event: Event):
    pass


@app.put('/event/publish')
async def update_published_event(event: Event):
    pass


@app.get('/event/publish')
async def published_events():
    pass


@app.post('/event/save')
async def save_event(event: Event):
    pass


@app.put('/event/save')
async def save_event(event: Event):
    pass


@app.delete('/event/save')
async def delete_event(event_id: ObjectId):
    pass


@app.get('/event/save')
async def get_saved_events():
    pass


# ----------------------- Ticket Sale --------------------------------
# User Session (Redis)
@app.post('/ticket')
async def buy_ticket(ticket: Ticket):
    pass


@app.get('/ticket')
async def buy_ticket(ticket: Ticket):
    pass


@app.put('/ticket')
async def update_ticket(ticket: Ticket):
    pass


@app.delete('/ticket')
async def delete_ticket(ticket: Ticket):
    pass


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
async def read_ticket(ticket_id: ObjectId):
    pass


# ----------------------- Telemetry --------------------------------
# User Session (Redis(
@app.post('/profile/attended_events')
async def attended_events(events: List[Event]):
    pass


@app.post('/profile/discount')
async def discount_earned(client: ClientUser):
    pass


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
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    print("Serving registration page")
    return templates.TemplateResponse("register.html", {"request": request})


if __name__ == '__main__':
    pass
