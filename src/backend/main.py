import logging

from bson.objectid import ObjectId
from fastapi import FastAPI
from pymongo import MongoClient

from models import Event, Ticket

# Initialize FastAPI application and templating engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
# templates = Jinja2Templates(directory="templates")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
#
# # Mock Redis client for development purposes (replace with actual connection)
# redis_client = redis.Redis(host='localhost', port=6379, db=0)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient('localhost', 27017)
    app.maadb_database = app.mongodb_client.maadb_tickets
    logger.info("Connected to MongoDB")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
    logger.info("Disconnected from MongoDB")


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
async def save_event(event: Event, publish: bool = False):
    """
    Save an event in user table, if publish is set to true it saves it also in events collection
    :param event:
    :param publish:
    :return:
    """
    # TODO: add cache
    # TODO: make it transactional ?
    app.maadb_database.user_collections.update_one({"_id": event.user_id},
                                                   {"$push": {"owned_events": event}})
    if publish:
        app.maadb_database.events_collection.insert_one(event.dict())
    # TODO raise exceptions


@app.put('/event')
async def save_event(event: Event, publish: bool = False):
    # TODO: add cache
    # TODO: make it transactional ?
    user = app.maadb_database.user_collections.find_one({"_id": event.user_id},
                                                        {"$set": {
                                                            "owned_events.$[x]": event.dict(),
                                                        }},
                                                        upsert=True,
                                                        array_filters=[{'x._id': event.id}])
    if publish:
        app.maadb_database.events_collection.update_one({"_id": event.id},
                                                        {"$set": event.dict()})
    # TODO raise exceptions


@app.delete('/event')
async def delete_event(event_id: str, user_id: str, publish: bool = False):
    # TODO: add cache
    # TODO: make it transactional ?
    event = app.maadb_database.user_collections.update_one({"_id": user_id},
                                       {"$pull": {"owned_events.$[x]": event_id}},
                                       array_filters=[{'x._id': event_id}])
    if publish:
        app.maadb_database.events_collection.delete_one({"_id": event_id})
    return event
    # TODO raise exceptions


@app.get('/event')
async def get_saved_events(user_id: str):
    user = app.maadb_database.user_collections.find_one({'$match': {'_id': user_id}})
    return user.owned_events


@app.get('/event/published')
async def get_published_events(skip: int = 0):
    events = app.maadb_database.events_collection.find_many().limit(10).skip(skip)
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


