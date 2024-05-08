from riak import RiakClient
import uuid
from riak import RiakObject

# Initialize Riak KV client
client = RiakClient(host='http://localhost', port=8098)

# Define valid users for simplicity
valid_users = {
    "user1": "password1",
    "user2": "password2"
}

# Function to authenticate user
def authenticate_user(username, password):
    if username in valid_users and valid_users[username] == password:
        return True
    else:
        return False

# Function to create a session
def create_session(user_id):
    session_id = str(uuid.uuid4())
    session_data = {'user_id': user_id, 'last_login': '2024-05-08'}
    session = RiakObject(key=session_id, value=session_data)
    client.store(session)
    return session_id

# Function to get session data
def get_session(session_id):
    session = client.get(session_id)
    if session:
        return session.value
    else:
        return None

# Function to delete session data
def delete_session(session_id):
    client.delete(session_id)

# Simulate user input for demonstration
username = "user1"
password = "password1"

if authenticate_user(username, password):
    session_id = create_session(username)
    print(f"Session created for user {username} with ID {session_id}")
else:
    print("Authentication failed")

# To retrieve session data later
session_data = get_session(session_id)
print(f"Session data: {session_data}")

# When the user logs out
delete_session(session_id)
print("Session deleted")
