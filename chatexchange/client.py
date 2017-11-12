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


class _SQLSession(sqlalchemy.orm.session.Session):
    def get_or_create_server(self, server_slug):
        assert server_slug
        server = self.query(Server).filter(models.Server.slug == server_slug).one_or_none()
        if not server:
            server = Server(server_slug=server_slug)
            self.add(server)
            self.flush()
            assert server.meta_id
        return server

    def get_or_create_user(self, server_meta_id, user_id):
        assert server_meta_id
        assert user_id
        user = self.query(User).filter(
            (models.User.server_meta_id == server_meta_id) &
            (models.User.user_id == user_id)
        ).one_or_none()
        if not user:
            user = User(server_meta_id=server_meta_id, user_id=user_id)
            self.add(user)
            self.flush()
            assert user.meta_id
        return user

    def get_or_create_room(self, server_meta_id, room_id):
        assert server_meta_id
        assert room_id
        room = self.query(Room).filter(
            (models.Room.server_meta_id == server_meta_id) &
            (models.Room.room_id == room_id)
        ).one_or_none()
        if not room:
            room = Room(server_meta_id=server_meta_id, room_id=room_id)
            self.add(room)
            self.flush()
            assert room.meta_id
        return room

    def get_or_create_message(self, server_meta_id, message_id):
        assert server_meta_id
        assert message_id
        message = self.query(Message).filter(
            (models.Message.server_meta_id == server_meta_id) &
            (models.Message.message_id == message_id)
        ).one_or_none()
        if not message:
            message = Message(server_meta_id=server_meta_id, message_id=message_id)
            self.add(message)
            self.flush()
            assert message.meta_id
        return message


class AsyncClient(object):
    # Defaults used to control caching:
    max_age_now     = -INFINITY
    max_age_current = 60                # one minute until a datum is no longer "current"
    max_age_fresh   = 60 * 60 * 4       # four hours until a datum is no longer "fresh"
    max_age_alive   = 60 * 60 * 24 * 64 # two months until a datum is no longer "alive"
    max_age_dead    = +INFINITY

    # These should be function options but we'll just set them here for now:
    desired_max_age = max_age_fresh
    required_max_age = max_age_dead
    offline = False

    def __init__(self, db_path='sqlite:///:memory:', auth=None):
        self._web_session = _HttpClientSession()

        self.sql_engine = sqlalchemy.create_engine(db_path)
        self._sql_sessionmaker = sqlalchemy.orm.sessionmaker(
            bind=self.sql_engine,
            expire_on_commit=False,
            class_=_SQLSession)

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
        if self._closed:
            raise Exception('already closed')

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

    async def _load_transcript_page(self, room_id=None, message_id=None, date=None):
        if message_id:
            if room_id:
                raise AttributeError("room_id not supported with message_id")
            if date:
                raise AttributeError("date not supported with message_id")
        elif not room_id:
            raise AttributeError("room_id xor message_id required")

        url = 'https://%s/transcript' % (self.host)

        if message_id:
            url += '/message/%s' % (message_id)
        else:
            url += '/%s' % (room_id)
            if date:
                url += '/%s/%s/%s' % (date.year, date.month, date.day)
            url += '/0-24'

        async with self._client._web_session.get(url) as response:
            html = await response.text()

        transcript = _parser.TranscriptPage(html)

        with self._client.sql_session() as sql:
            room = sql.get_or_create_room(self.meta_id, transcript.room_id)
            room.name = transcript.room_name
            room.mark_updated()

            for m in transcript.messages:
                message = sql.get_or_create_message(self.meta_id, m.id)
                message.content_html = m.content_html
                message.content_text = m.content_text
                message.room_id = transcript.room_id

                if m.parent_message_id:
                    parent = sql.get_or_create_message(self.meta_id, m.parent_message_id)
                    message.parent_message_id = m.parent_message_id

                owner = sql.get_or_create_user(self.meta_id, m.owner_user_id)
                if not m.owner_user_name:
                    # XXX: this is the name as of the time of the message, so it should really
                    # be treated as an update from that time, except that we don't have message
                    # timestamps implemented yet, so we'll just use the first name we see.
                    owner.name = m.owner_user_name
                    owner.mark_updated()
                message.owner_id = m.owner_user_id

        return transcript

    async def room(self, room_id):
        with self._client.sql_session() as sql:
            room = sql.get_or_create_room(self.meta_id, room_id)

        if room.meta_update_age < self._client.desired_max_age:
            return room

        if not self._client.offline:
            await self._load_transcript_page(room_id=room_id)

            with self._client.sql_session() as sql:
                room = sql.get_or_create_room(self.meta_id, room_id)

        if room.meta_update_age <= self._client.required_max_age:
            return room
        
        logger.warning("%s failed to load room %s, %s > %s", self, room_id, room.meta_update_age, self._client.required_max_age)
        return None

    async def message(self, message_id):
        with self._client.sql_session() as sql:
            message = sql.get_or_create_message(self.meta_id, message_id)

        if message.meta_update_age < self._client.desired_max_age:
            return message

        if not self._client.offline:
            await self._load_transcript_page(message_id=message_id)

            with self._client.sql_session() as sql:
                message = sql.get_or_create_message(self.meta_id, message_id)

        if message.meta_update_age <= self._client.required_max_age:
            return message
        
        logger.warning("%s failed to load message %s, %s > %s", self, message_id, message.meta_update_age, self._client.required_max_age)
        return None
    
    def rooms(self):
        # TODO: check database first
        response = self._client._web_session.get('https://%s/rooms?tab=all&sort=active&nohide=true' % (self.host))
        raise NotImplementedError()
        
    def user(self, user_id):
        # TODO: check database first
        response = self._client._web_session.get('https://%s/users/%s' % (self.host, user_id))
        raise NotImplementedError()


class User(models.User):
    _client_server = None



class Room(models.Room):
    _client_server = None

    def _message(self, message_id):
        with self._client.sql_session() as sql:
            for message in sql.query(Message).filter(
                    (Message.room_meta_id == self.meta_id) &
                    (Message.message_id == message_id)):
                return message
            return Message(room_meta_id=self.meta_id, message_id=message_id)

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

