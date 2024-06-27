"""
This module implements endpoints for crud operations over users.
"""
import uuid

from fastapi import APIRouter, Depends, Response, status

from models import UserModel
from redis_utils import create_session
from utils import get_engine

router = APIRouter()


@router.post("/register/business")
async def register(username: str, engine=Depends(get_engine)):
    """
    Create a new business user.
    :param username: str
    :param engine: Depends on get_engine
    :return: UserModel
    """
    # TODO check user exists
    user = UserModel(id=uuid.uuid4(), username=username, role='business')
    user = await engine.save(user)
    return user


@router.get('/user/business/{user_id}')
async def get_user(user_id: str, engine=Depends(get_engine)):
    """
    Get the business user by id.
    :param user_id: str
    :param engine: Depends on get_engine
    :return: Response
    """
    # TODO generate user_session token/id
    user = await engine.find_one(UserModel, {'_id': uuid.UUID(user_id)})
    session_token = await create_session({'user': user.model_dump_json()})
    return Response(status_code=status.HTTP_200_OK,
                    headers={'X-Session-Id': session_token},
                    content=user.model_dump_json())


if __name__ == '__main__':
    pass
