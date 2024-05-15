from uuid import uuid4
from pydantic import BaseModel

from fastapi import FastAPI
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title='User API',
    description='User API with FastAPI and MongoDB',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    name: str
    password: str

    money: int = 0
    admin: bool = False


client = MongoClient('mongodb://host.docker.internal:27017')
db = client['current']['user']


# user crud

@app.post(
    '/user',
    description='Creates a new user with the provided name, password, money, and admin status.',
    response_description='Returns a success message upon creation.',
)
async def create_user(user: User):
    user_id = str(uuid4())

    db.insert_one({
        '_id': user_id,

        'name': user.name,
        'password': user.password,

        'money': user.money,
        'admin': user.admin
    })

    return {'message': f'created: {user_id}'}, 200

@app.get(
    '/user/{user_id}',
    description='Retrieves a user\'s with the specified ID.',
    response_description='Returns the user information if found, or a message indicating that the user was not found.',
)
async def read_user(user_id: str):
    document = db.find_one({'_id': user_id})

    if not document:
        return {'message': 'user not found'}, 404

    return document, 200


@app.put(
    '/user/{user_id}',
    description='Updates the information of an existing user with the specified ID.',
    response_description='Returns a success message upon updating, or a message indicating that the user was not found.'
)
async def update_user(user_id: str, user: User):
    document = db.find_one({'_id': user_id})

    if not document:
        return {'message': 'user not found'}, 404

    db.update_one({'_id': user_id}, {
        '$set': {
            'name': user.name,
            'password': user.password,

            'money': user.money,
            'admin': user.admin
        }
    })

    return {'message': f"updated: {document['_id']}"}, 200


@app.delete(
    '/user/{user_id}',
    description='Deletes a user with the specified ID.',
    response_description='Returns a success message upon deletion, or a message indicating that the user was not found.'
)
async def delete_user(user_id):
    document = db.find_one({'_id': user_id})

    if not document:
        return {'message': 'user not found'}, 404

    db.delete_one({'_id': user_id})

    return {'message': f'deleted: {document["_id"]}'}, 200


# users search


@app.get(
    '/users',
    description='Retrieves a list of all users.',
    response_description='Returns the list of users if not empty, or a message indicating that the list is empty.'
)
async def read_users():
    users = list(db.find())

    if not users:
        return {'message': 'empty'}, 404

    return users


# login

@app.post(
    '/login',
    description='Validates user credentials \'name and password\' against the database.',
    response_description='Returns the user ID and name if the login is successful, or a message indicating an invalid login.'
)
async def login(name: str, password: str):
    document = db.find_one({'name': name, 'password': password})

    if not document:
        return {'message': 'invalid login'}, 404

    return {'id': document['_id'], 'name': document['name']}, 200

@app.post(
    '/register',
    description='Register a new user with the provided name and password.',
    response_description='Returns a success message upon creation.',
)
async def create_user(user: User):
    user_id = str(uuid4())

    existing_user = db.find_one({'name': user.name})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    db.insert_one({
        '_id': user_id,
        'name': user.name,
        'password': user.password,

        'money': 0,
        'admin': False
    })

    return {'message': f'created: {user_id}'}, 200