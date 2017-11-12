import abc
import logging

from . import _parser, _obj_dict



logger = logging.getLogger(__name__)


class _Scraper:
    __repr__ = _obj_dict.repr
    @classmethod
    async def scrape(cls, server, **kwargs):
        self = cls(server, **kwargs)
        logger.info("Fetching %s...", self.url)
        self.html = await self._fetch()
        logger.debug("Importing data fetched from %s...", self.url)
        self._load()
        logger.info("...finished scraping %s.", self.url)
        return self

    def __init__(self, server, **kwargs):
        self.server = server
        self.url = 'https://%s/%s' % (server.host, self._make_path(**kwargs))

    @abc.abstractmethod
    def _make_path(self, **kwargs):
        pass

    async def _fetch(self):
        async with self.server._client._web_session.get(self.url) as response:
            logger.debug("...%s response from %s...", response.status, self.url)
            html = await response.text()
            logger.debug("...fully loaded")
            return html

    @abc.abstractmethod
    def _load(self):
        pass



class TranscriptPage(_Scraper):
    def _make_path(self, room_id=None, message_id=None, date=None):
        target_room_id = room_id
        target_message_id = message_id
        target_date = date

        if message_id:
            if room_id:
                raise AttributeError("room_id not supported with message_id")
            if date:
                raise AttributeError("date not supported with message_id")
        elif not room_id:
            raise AttributeError("room_id xor message_id required")

        path = 'transcript'

        if target_message_id:
            path += '/message/%s' % (target_message_id)
        else:
            path += '/%s' % (target_room_id)
            if target_date:
                path += '/%s/%s/%s' % (
                    target_date.year, target_date.month, target_date.day)
            path += '/0-24'
        
        return path

    def _load(self):
        self.data = _parser.TranscriptPage(self.html)

        with self.server._client.sql_session() as sql:
            self.room = self.server._get_or_create_room(sql, self.data.room_id)
            self.room.mark_updated()
            self.room.name = self.data.room_name

            self.messages = {}
            self.users = {}

            for m in self.data.messages:
                message = self.server._get_or_create_message(sql, m.id)
                message.mark_updated()
                message.content_html = m.content_html
                message.content_text = m.content_text
                message.room_meta_id = self.room.meta_id

                self.messages[m.id] = message

                if m.parent_message_id:
                    if m.parent_message_id in self.messages:
                        parent = self.messages[m.parent_message_id]
                    else:
                        parent = self.server._get_or_create_message(sql, m.parent_message_id)
                    message.parent_message_id = m.parent_message_id

                owner = self.users.get(m.owner_user_id)
                if not owner:
                    if m.owner_user_id:
                        owner = self.server._get_or_create_user(sql, m.owner_user_id)
                        if not owner.name:
                            owner.mark_updated()
                            # XXX: this is the name as of the time of the message, so it should really
                            # be treated as an update from that time, except that we don't have message
                            # timestamps implemented yet, so we'll just use the first name we see.
                            owner.name = m.owner_user_name
                    else:
                        # deleted owner, default to Community.
                        owner = self.server._get_or_create_user(sql, -1)
                    self.users[m.owner_user_id] = owner
                message.owner_meta_id = owner.meta_id
        
        return self
