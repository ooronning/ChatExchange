import logging
import datetime

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime

from .. import _utils

from . import _base


logger = logging.getLogger(__name__)


class User(_base.Base):
    __tablename__ = 'User'

    _client = None

    id = Column(Integer, primary_key=True)
    name = Column(String)
    about = Column(String)
    is_moderator = Column(Boolean)
    message_count = Column(Integer)
    room_count = Column(Integer)
    reputation = Column(Integer)
    last_seen = Column(DateTime)
    last_message = Column(DateTime)

    meta_last_updated = Column(DateTime, onupdate=datetime.datetime.now),

    def scrape_profile(self):
        data = self._client._br.get_profile(self.id)

        self.name = data['name']
        self.is_moderator = data['is_moderator']
        self.message_count = data['message_count']
        self.room_count = data['room_count']
        self.reputation = data['reputation']
        self.last_seen = data['last_seen']
        self.last_message = data['last_message']

    def __repr__(self):
        return "<%s.%s with id %r on %s>" % (
            type(self).__module__, type(self).__name__, self.id, self._client.host)
