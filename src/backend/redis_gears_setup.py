from rgsync import RGJSONWriteBehind, RGJSONWriteThrough
from rgsync.Connectors import MongoConnector, MongoConnection

mongoUrl = 'mongodb://root:example@localhost:27017/'
db = 'maadb_tickets'

connection = MongoConnection('', '', '', '', mongoUrl)

event_connector = MongoConnector(connection, db, 'events_collection', 'id')

RGJSONWriteBehind(GB, keysPrefix='EventEntity',
                  connector=event_connector, name='EventsWriteBehind',
                  version='99.99.99')
