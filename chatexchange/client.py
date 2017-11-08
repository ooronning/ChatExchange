from contextlib import contextmanager

import requests
import sqlalchemy.orm

from . import models, _parser, _seed


class Room(models.Room):
    _client_server = None

    @property
    def owner(self):
        return self._client_server.get_user(self.owner_id)


class User(models.User):
    _client_server = None


class Message(models.Message):
    _client_server = None

    @property
    def server(self):
        return self._client_server

    @property
    def owner(self):
        return self._client_server.get_user(self.owner_id)

    @property
    def room(self):
        return self._client_server.get_room(self.room_id)


class Server(models.Server):
    _client = None

    def get_room(self, room_id: int) -> Room:
        response = self._client._web_session.get('%s/transcript/%s' % (self.url, room_id))
        transcript = _parser.TranscriptPage(response)
        transcript.room_id

    def get_user(self, room_id: int) -> User:
        pass

    def get_message(self, room_id: int) -> Message:
        pass


class Client(object):
    user_agent = None

    def __init__(self):
        self._web_session = requests.Session()
        self._web_session.headers.update({
            'User-Agent': self.user_agent
        })

        self.sql_engine = sqlalchemy.create_engine('sqlite:///:memory:')
        self._sql_sessionmaker = sqlalchemy.orm.sessionmaker(
            bind=self.sql_engine,
            expire_on_commit=False)

        models._base._Base.metadata.create_all(self.sql_engine)

        with self.sql_session() as sql:
            for row in _seed.data():
                sql.add(row)

    @contextmanager
    def sql_session(self):
        session = self._sql_sessionmaker()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_server(self, slug: str) -> Server:
        with self.sql_session() as sql:
            server = sql.query(Server).filter(models.Server.slug == slug).one()
        server.set(_client=self)
        return server

        raise Exception('sanity failure')

    def se(self):
        return self.get_server('se')
    
    def so(self):
        return self.get_server('so')
    
    def mse(self):
        return self.get_server('mse')
