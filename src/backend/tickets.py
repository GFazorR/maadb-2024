from models import Ticket
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.post('/ticket/buy')
async def buy_ticket(ticket: Ticket):
    pass


@router.put('/ticket/buy')
async def update_ticket(ticket: Ticket):
    pass


@router.delete('/ticket/buy')
async def delete_ticket(ticket: Ticket):
    pass


@router.get('/ticket/buy')
async def read_ticket(ticket_id: str):
    pass


if __name__ == '__main__':
    pass
