from models import Ticket, EventModel
from fastapi import APIRouter, Depends, HTTPException
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

router = APIRouter()
cluster = Cluster(port=9042)
session = cluster.connect('tickets')

# TODO Figure out schema and other stuff

@router.post('/ticket/buy')
async def buy_ticket(ticket: Ticket):
    # TODO create query and return result
    query = SimpleStatement(f'INSERT INTO {ticket.event_name} (id, user_id, price, discount) VALUES (%s, %s, %s, %s)')
    parameters = (ticket.id, ticket.user_id, ticket.price, ticket.discount)
    result = session.execute(query, parameters)
    return result


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
