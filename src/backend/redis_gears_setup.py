from rgsync import RGJSONWriteBehind, RGJSONWriteThrough
from rgsync.Connectors import MongoConnector, MongoConnection

mongoUrl = 'mongodb://root:example@localhost:27017/'
db = 'maadb_tickets'

connection = MongoConnection('', '', '', '', mongoUrl)

movieConnector = MongoConnector(connection, db, 'events_collection', 'id')

# TODO: change movie to events
RGJSONWriteBehind(GB, keysPrefix='MovieEntity',
                  connector=movieConnector, name='MoviesWriteBehind',
                  version='99.99.99')
