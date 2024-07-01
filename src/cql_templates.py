from cassandra.cluster import ConsistencyLevel
from cassandra.query import SimpleStatement


def initialize_cassandra(session):
    session.execute(SimpleStatement("""
    CREATE KEYSPACE IF NOT EXISTS ticket_service 
    WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 3}
    """))

    session.execute(SimpleStatement("""
    CREATE KEYSPACE IF NOT EXISTS inventory WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 3}
    """))

    session.execute(SimpleStatement("""
        CREATE TABLE IF NOT EXISTS ticket_service.tickets(
        event_id uuid,
        event_day date,
        purchase_date timestamp,
        user_id uuid,
        ticket_id uuid,
        ticket_price float,
        discount float,
        paid_price float,
        status text,
        PRIMARY KEY ( event_id, event_day, user_id, ticket_id),
    )"""))
    session.execute(SimpleStatement("""
        CREATE TABLE IF NOT EXISTS ticket_service.tickets_by_user(
        user_id uuid,
        event_id uuid,
        ticket_id uuid,
        event_day date,
        purchase_date timestamp,
        paid_price float,
        status text,
        PRIMARY KEY (user_id, ticket_id)
    )"""))
    session.execute(SimpleStatement("""
        CREATE TABLE IF NOT EXISTS ticket_service.tickets_by_user_and_date(
        user_id uuid,
        event_day date,
        event_id uuid,
        ticket_id uuid,
        purchase_date timestamp,
        paid_price float,
        status text,
        PRIMARY KEY ( user_id, event_day, ticket_id)
        ) WITH CLUSTERING ORDER BY (event_day ASC)
        """))
    session.execute(SimpleStatement("""
        CREATE INDEX IF NOT EXISTS index_status ON ticket_service.tickets_by_user (status)
        """))
    session.execute(SimpleStatement("""
        CREATE INDEX IF NOT EXISTS index_event_day ON ticket_service.tickets_by_user_and_date (status)
        """))
    session.execute(SimpleStatement("""
        CREATE TABLE IF NOT EXISTS inventory.events(
        event_id uuid,
        event_day date,
        purchased_tickets int,
        PRIMARY KEY ( event_id, event_day )
    )"""))
    session.execute(SimpleStatement("""
        CREATE TABLE IF NOT EXISTS inventory.user_visits(
        event_id uuid,
        page_visits counter,
        PRIMARY KEY ( event_id )
    )"""))


insert_ticket = SimpleStatement("""
        INSERT INTO ticket_service.tickets 
        (event_id, event_day, purchase_date, user_id,
        ticket_id, ticket_price, discount, paid_price, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)

insert_by_user = SimpleStatement("""
INSERT INTO ticket_service.tickets_by_user ("user_id", "purchase_date", "event_day", "event_id", "ticket_id", "paid_price", "status") 
VALUES (%s, %s, %s, %s, %s, %s, %s)
""")

insert_by_user_and_date = SimpleStatement("""
INSERT INTO ticket_service.tickets_by_user_and_date ("user_id", "event_day", "event_id", "ticket_id", "purchase_date", "paid_price", "status")
VALUES (%s, %s, %s, %s, %s, %s, %s)
""")

update_by_user = SimpleStatement("""
UPDATE ticket_service.tickets_by_user
SET status = %s
WHERE user_id = %s AND ticket_id = %s
""")

update_by_user_and_date = SimpleStatement("""
UPDATE ticket_service.tickets_by_user_and_date
SET status = %s
WHERE user_id = %s AND event_day = %s AND ticket_id = %s
""")

increment_counter = SimpleStatement("""
UPDATE inventory.events
SET purchased_tickets = %s
WHERE event_id = %s AND event_day = %s
IF purchased_tickets = %s
""", consistency_level=ConsistencyLevel.LOCAL_QUORUM)

update_ticket = SimpleStatement("""
UPDATE ticket_service.tickets
SET status = %s
WHERE event_id = %s AND event_day = %s AND user_id = %s AND ticket_id = %s
""")

n_tickets = SimpleStatement("""
SELECT purchased_tickets
FROM inventory.events
WHERE event_id = %s AND event_day = %s
""", consistency_level=ConsistencyLevel.LOCAL_QUORUM)

purch_tickets = SimpleStatement("""
SELECT purchased_tickets
FROM inventory.events
WHERE event_id = %s AND event_day = %s
IF purchased_tickets < %s
""", consistency_level=ConsistencyLevel.LOCAL_QUORUM)

user_tickets_status = SimpleStatement("""
SELECT * 
FROM ticket_service.tickets_by_user
WHERE user_id = %s AND status = %s
""")

user_tickets = SimpleStatement("""
        SELECT * 
        FROM ticket_service.tickets_by_user
        WHERE user_id = %s
        """)

attended_events = SimpleStatement("""
SELECT event_id 
FROM ticket_service.tickets_by_user_and_date
WHERE user_id = %s AND event_day < %s AND status = %s
""")

delete_ticket = SimpleStatement("""
DELETE 
FROM ticket_service.tickets
WHERE event_id = %s AND event_day = %s AND user_id = %s AND ticket_id = %s
""")

delete_by_user = SimpleStatement("""
DELETE 
FROM ticket_service.tickets_by_user
WHERE user_id = %s AND ticket_id = %s
""")

delete_by_user_and_day = SimpleStatement("""
DELETE 
FROM ticket_service.tickets_by_user_and_date
WHERE user_id = %s AND event_day = %s AND ticket_id = %s
""")

increment_visits = SimpleStatement("""
        UPDATE inventory.user_visits
        SET page_visits = page_visits + %s
        WHERE event_id = %s
        """, consistency_level=ConsistencyLevel.QUORUM)

if __name__ == '__main__':
    pass
