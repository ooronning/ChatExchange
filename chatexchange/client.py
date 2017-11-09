from contextlib import contextmanager
import logging
import random

import requests
import sqlalchemy.orm

from . import models, _parser, _seed



logger = logging.getLogger(__name__)


class Room(models.Room):
    _client_server = None

    @property
    def owner(self):
        return self._client_server.user(self.owner_id)


class User(models.User):
    _client_server = None


class Message(models.Message):
    _client_server = None

    @property
    def server(self):
        return self._client_server

    @property
    def owner(self):
        return self._client_server.user(self.owner_id)

    @property
    def room(self):
        return self._client_server.room(self.room_id)


class Server(models.Server):
    _client = None

    def room(self, room_id: int) -> Room:
        with self._client.sql_session() as sql:
            for existing in sql.query(Room).filter(
                    (Room.server_meta_id == self.meta_id) &
                    (Room.room_id == room_id)):

                logger.debug("Found %s with age %s." % (existing, existing.meta_update_age))

                room = existing
                break
            else:
                room = None
            
            if room:
                if room.meta_update_age <= self._client.max_age_fresh:
                    logger.debug("It's fresh, returning!")
                    return room
                else:
                    logger.debug("But it's not fresh... updating!")
                    room._mark_updated()

            try:
                response = self._client._web_session.get('%s/transcript/%s/0-24' % (self.url, room_id))
                transcript = _parser.TranscriptPage(response)
            except Exception as ex:
                if room and room.meta_update_age < self._client.max_age_dead:
                    logger.error(ex)
                    logger.warn("Using stale data due to error fetching new data.")
                    sql.rollback()
                    sql.refresh(room)
                    return room
                else:
                    raise

            if not room:
                room = Room(server_meta_id=self.meta_id)

            room.room_id = transcript.room_id
            room.name = transcript.room_name

            room = sql.merge(room)

        return room
    
    def rooms(self):
        # TODO: check database first
        response = self._client._web_session.get('%s/rooms?tab=all&sort=active&nohide=true' % (self.url))
        
    def user(self, user_id: int) -> User:
        # TODO: check database first
        response = self._client._web_session.get('%s/users/%s' % (self.url, user_id))

    def message(self, message_id: int) -> Message:
        # TODO: check database first
        response = self._client._web_session.get('%s/transcript/message/%s/0-24' % (self.url, message_id))


class Client(object):
    user_agent = None

    # Defaults used to control caching:
    max_age_now     = float('-inf')
    max_age_current = 60                # one minute until a datum is no longer "current"
    max_age_fresh   = 60 * 60 * 4       # four hours until a datum is no longer "fresh"
    max_age_alive   = 60 * 60 * 24 * 64 # two months until a datum is no longer "alive"
    max_age_dead    = float('inf')

    _max_age_jitter_ratio = 1/8
    def _max_age_jitter(self, x):
        # might not be able to actually use this
        return x + (random.random() - 0.5) * (x * self._max_age_jitter_ratio)

    def __init__(self, db_path='sqlite:///:memory:'):
        self._web_session = requests.Session()
        self._web_session.headers.update({
            'User-Agent': self.user_agent
        })

        self.sql_engine = sqlalchemy.create_engine(db_path)
        self._sql_sessionmaker = sqlalchemy.orm.sessionmaker(
            bind=self.sql_engine,
            expire_on_commit=False)

        models.Base.metadata.create_all(self.sql_engine)

        with self.sql_session() as sql:
            for row in _seed.data():
                try:
                    sql.add(row)
                    sql.commit()
                except sqlalchemy.exc.IntegrityError:
                    sql.rollback()
                    continue

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

    def server(self, slug: str) -> Server:
        with self.sql_session() as sql:
            server = sql.query(Server).filter(models.Server.slug == slug).one()
        server.set(_client=self)
        return server

        raise Exception('sanity failure')

    def se(self):
        return self.server('se')

    def so(self):
        return self.server('so')
    
    def mse(self):
        return self.server('mse')
