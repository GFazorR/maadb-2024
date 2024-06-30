from cassandra.cluster import ConsistencyLevel
from cassandra.query import SimpleStatement


insert_ticket = SimpleStatement("""
        INSERT INTO tickets 
        (event_id, event_day, purchase_date, user_id,
        ticket_id, ticket_price, discount, paid_price, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)

insert_by_user = SimpleStatement("""
INSERT INTO tickets_by_user ("user_id", "purchase_date", "event_day", "event_id", "ticket_id", "paid_price", "status") 
VALUES (%s, %s, %s, %s, %s, %s, %s)
""")

insert_by_user_and_date = SimpleStatement("""
INSERT INTO tickets_by_user_and_date ("user_id", "event_day", "event_id", "ticket_id", "purchase_date", "paid_price", "status")
VALUES (%s, %s, %s, %s, %s, %s, %s)
""")

update_by_user = SimpleStatement("""
UPDATE tickets_by_user
SET status = %s
WHERE user_id = %s AND ticket_id = %s
""")

update_by_user_and_date = SimpleStatement("""
UPDATE tickets_by_user_and_date
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
FROM tickets_by_user
WHERE user_id = %s AND status = %s
""")

user_tickets = SimpleStatement("""
        SELECT * 
        FROM tickets_by_user
        WHERE user_id = %s
        """)

attended_events = SimpleStatement("""
SELECT event_id 
FROM tickets_by_user_and_date
WHERE user_id = %s AND event_day < %s AND status = %s
""")

delete_ticket = SimpleStatement("""
DELETE 
FROM tickets
WHERE event_id = %s AND event_day = %s AND user_id = %s AND ticket_id = %s
""")

delete_by_user = SimpleStatement("""
DELETE 
FROM tickets_by_user
WHERE user_id = %s AND ticket_id = %s
""")

delete_by_user_and_day = SimpleStatement("""
DELETE 
FROM tickets_by_user_and_date
WHERE user_id = %s AND event_day = %s AND ticket_id = %s
""")

if __name__ == '__main__':
    pass