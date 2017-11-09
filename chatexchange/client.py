import asyncio
from contextlib import contextmanager
import logging
import random

import aiohttp
import sqlalchemy.orm

from . import models, _parser, _seed
from ._constants import *



logger = logging.getLogger(__name__)


class _HttpClientSession(aiohttp.ClientSession):
    def __init__(self, *a, **kw):
        if 'connector' not in kw:
            kw['connector'] = aiohttp.TCPConnector(limit_per_host=2)
        super().__init__(*a, **kw)

    def _request(self, method, url, **kwargs):
        # see https://stackoverflow.com/a/45590516/1114
        logger.debug('%s %r', method, url)
        return super()._request(method, url, **kwargs)


class AsyncClient(object):
    # Defaults used to control caching:
    max_age_now     = -INFINITY
    max_age_current = 60                # one minute until a datum is no longer "current"
    max_age_fresh   = 60 * 60 * 4       # four hours until a datum is no longer "fresh"
    max_age_alive   = 60 * 60 * 24 * 64 # two months until a datum is no longer "alive"
    max_age_dead    = -INFINITY

    def __init__(self, db_path='sqlite:///:memory:', auth=None):
        self._web_session = _HttpClientSession()

        self.sql_engine = sqlalchemy.create_engine(db_path)
        self._sql_sessionmaker = sqlalchemy.orm.sessionmaker(
            bind=self.sql_engine,
            expire_on_commit=False)

        self._event_loop = asyncio.get_event_loop()

        models.Base.metadata.create_all(self.sql_engine)

        with self.sql_session() as sql:
            for row in _seed.data():
                try:
                    sql.add(row)
                    sql.commit()
                except sqlalchemy.exc.IntegrityError:
                    sql.rollback()
                    continue
    
    _closed = False
    def close(self):
        if self._closed: raise Exception('already closed')

        self._web_session.close()

        self._closed = True
    
    def __enter__(self):
        return self

    def __exit__(self, *exc_details):
        self.close()

    @contextmanager
    def sql_session(self):
        if self._closed: raise Exception('already closed')

        session = self._sql_sessionmaker()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def server(self, slug_or_host):
        with self.sql_session() as sql:
            server = sql.query(Server).filter(
                (models.Server.slug == slug_or_host) |
                (models.Server.host == slug_or_host)).one()
        server.set(_client=self)
        return server

    @property
    def se(self):
        return self.server('se')

    @property
    def so(self):
        return self.server('so')

    @property    
    def mse(self):
        return self.server('mse')


class Server(models.Server):
    _client = None

    def me(self):
        raise NotImplementedError()

    async def room(self,
             room_id,
             offline=False,
             desired_max_age=AsyncClient.max_age_fresh,
             required_max_age=AsyncClient.max_age_dead):
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
                if room.meta_update_age <= desired_max_age:
                    logger.debug("It's fresh, returning!")
                    return room
                else:
                    logger.debug("But it's not fresh... updating!")

            try:
                if offline: raise Exception("offline=True")
                async with self._client._web_session.get('https://%s/transcript/%s/0-24' % (self.host, room_id)) as response:
                    html = await response.text()
                transcript = _parser.TranscriptPage(html)
            except Exception as ex:
                if room and room.meta_update_age <= required_max_age:
                    logger.error(ex)
                    logger.warn("Using stale data due to error fetching new data.")
                    return room
                else:
                    raise

            if not room:
                room = Room(server_meta_id=self.meta_id)

            room.room_id = transcript.room_id
            room.name = transcript.room_name
            room._mark_updated()

            room = sql.merge(room)

        return room
    
    def rooms(self):
        # TODO: check database first
        response = self._client._web_session.get('https://%s/rooms?tab=all&sort=active&nohide=true' % (self.host))
        raise NotImplementedError()
        
    def user(self, user_id):
        # TODO: check database first
        response = self._client._web_session.get('https://%s/users/%s' % (self.host, user_id))
        raise NotImplementedError()

    def message(self, message_id):
        # TODO: check database first
        response = self._client._web_session.get('https://%s/transcript/message/%s/0-24' % (self.host, message_id))
        raise NotImplementedError()


class User(models.User):
    _client_server = None



class Room(models.Room):
    _client_server = None

    @property
    def owner(self):
        return self._client_server.user(self.owner_id)

    def send(self, content_markdown):
        pass



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

