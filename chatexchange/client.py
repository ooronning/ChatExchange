from contextlib import contextmanager

import requests
import sqlalchemy.orm

from . import models
from . import parser
from . import _seed


class LiveRoom(models.Room):
    _live_server = None

    @property
    def owner(self):
        return self._live_server.get_user(self.owner_id)


class LiveUser(models.User):
    _live_server = None


class LiveMessage(models.Message):
    _live_server = None

    @property
    def server(self):
        return self._live_server

    @property
    def owner(self):
        return self._live_server.get_user(self.owner_id)

    @property
    def room(self):
        return self._live_server.get_room(self.room_id)


class LiveServer(models.Server):
    _client = None

    def get_room(self, room_id: int) -> LiveRoom:
        response = self._client._web_session.get('%s/transcript/%s' % (self.url, room_id))
        transcript = parser.TranscriptPage(response)
        transcript.room_id

    def get_user(self, room_id: int) -> LiveUser:
        pass

    def get_message(self, room_id: int) -> LiveMessage:
        pass


class Client(object):
    user_agent = None

    def __init__(self):
        self._web_session = requests.Session()
        self._web_session.headers.update({
            'User-Agent': self.user_agent
        })

        self._sql_engine = sqlalchemy.create_engine('sqlite:///:memory:')
        self._sql_sessionmaker = sqlalchemy.orm.sessionmaker(
            bind=self._sql_engine,
            expire_on_commit=False)

        models._base._Base.metadata.create_all(self._sql_engine)

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

    def get_server(self, slug: str) -> LiveServer:
        with self.sql_session() as sql:
            server = sql.query(LiveServer).filter(models.Server.slug == slug).one()
        server.set(_client=self)
        return server

        raise Exception('sanity failure')

    def se(self):
        return self.get_server('se')
    
    def so(self):
        return self.get_server('so')
    
    def mse(self):
        return self.get_server('mse')
