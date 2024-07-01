"""
This module implements endpoints for crud operations over users.
"""
import uuid
from math import log

from fastapi import APIRouter, Depends, Response, status, BackgroundTasks

from src.models import UserModel
from src.redis_utils import create_session, get_cached_discount, set_cached_discount
from src.utils import get_engine, get_ticket_service

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


@router.post("/register/client")
async def register_client(username: str, engine=Depends(get_engine)):
    """
    Create a new client user.
    :param username: str
    :param engine: Depends on get_engine
    :return: UserModel
    """
    # TODO check if user already exists
    user = UserModel(id=uuid.uuid4(), username=username, role='client')
    user = await engine.save(user)
    return user


@router.get('/user/client/{user_id}')
async def get_client_users(user_id: str, engine=Depends(get_engine)):
    """
    Get all client users.
    :param user_id: str
    :param engine: Depends on get_engine
    :return: UserModel
    """
    client_user = await engine.find_one(UserModel, {'_id': uuid.UUID(user_id)})
    session_token = await create_session({'user': client_user.model_dump_json()})
    return Response(status_code=status.HTTP_200_OK,
                    headers={'X-Session-Id': session_token},
                    content=client_user.model_dump_json())


@router.get('/user/tickets')
async def get_user_tickets(
        user_id: uuid.UUID,
        ticket_status: str = None,
        ticket_service=Depends(get_ticket_service)
):
    tickets = ticket_service.get_tickets_by_user(user_id, ticket_status)
    return Response(status_code=status.HTTP_200_OK, content=tickets.json())


@router.get('/user/discount')
async def calculate_discount(
        user_id: uuid.UUID,
        background_task: BackgroundTasks,
        ticket_service=Depends(get_ticket_service)
):
    discount = await get_cached_discount(user_id)
    if discount is None:
        n_tickets = ticket_service.get_attended_events(user_id)
        if not n_tickets > 0:
            discount = .0
        else:
            discount = log(n_tickets) * .1 if log(n_tickets) * .1 < 0.1 else .1
        background_task.add_task(set_cached_discount,
                                 user_id, discount)
    return discount



if __name__ == '__main__':
    pass
