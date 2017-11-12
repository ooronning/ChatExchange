from . import _parser, _obj_dict



class _Scraper:
    __repr__ = _obj_dict.repr



class TranscriptPage(_Scraper):
    @classmethod
    async def scrape(cls, server, room_id=None, message_id=None, date=None):
        if message_id:
            if room_id:
                raise AttributeError("room_id not supported with message_id")
            if date:
                raise AttributeError("date not supported with message_id")
        elif not room_id:
            raise AttributeError("room_id xor message_id required")

        self = cls()

        self.server = server

        self.target_room_id = room_id
        self.target_message_id = message_id
        self.target_date = date

        self.url = 'https://%s/transcript' % (server.host)

        if self.target_message_id:
            self.url += '/message/%s' % (self.target_message_id)
        else:
            self.url += '/%s' % (self.target_room_id)
            if self.target_date:
                self.url += '/%s/%s/%s' % (
                    self.target_date.year, self.target_date.month, self.target_date.day)
            self.url += '/0-24'

        async with self.server._client._web_session.get(self.url) as response:
            self.html = await response.text()

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
                message.room_id = self.data.room_id
                self.messages[m.id] = message

                if m.parent_message_id:
                    if m.parent_message_id in self.messages:
                        parent = self.messages[m.parent_message_id]
                    else:
                        parent = self.server._get_or_create_message(sql, m.parent_message_id)
                    message.parent_message_id = m.parent_message_id

                owner = self.users.get(m.owner_user_id)
                if not owner:
                    owner = self.server._get_or_create_user(sql, m.owner_user_id)
                    if not owner.user_name:
                        owner.mark_updated()
                        # XXX: this is the name as of the time of the message, so it should really
                        # be treated as an update from that time, except that we don't have message
                        # timestamps implemented yet, so we'll just use the first name we see.
                        owner.name = m.owner_user_name
                    self.users[m.owner_user_id] = owner
                message.owner_id = m.owner_user_id
        
        return self
