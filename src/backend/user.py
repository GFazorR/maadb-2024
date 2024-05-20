from urllib.request import Request

from fastapi import FastAPI, APIRouter, Request, Depends, Response, status
from redis import create_session, get_session
from models import UserModel, EventModel
from odmantic import AIOEngine
from typing import Annotated
from bson import ObjectId
import uuid

router = APIRouter()


def get_engine(request: Request):
    engine = request.app.engine
    return engine


@router.post(
    "/register/business",
)
async def register(username: str, engine=Depends(get_engine)):
    # TODO check user exists
    user = UserModel(username=username, role='business')
    user = await engine.save(user)
    return user


@router.get('/user/business/{user_id}')
async def get_user(user_id: str, engine=Depends(get_engine)):
    # TODO generate user_session token/id
    user = await engine.find_one(UserModel, {'_id': ObjectId(user_id)})
    session_token = await create_session({'user': user.model_dump_json()})
    return Response(status_code=status.HTTP_200_OK,
                    headers={'X-Session-Id': session_token},
                    content=user.model_dump_json())


if __name__ == '__main__':
    pass
