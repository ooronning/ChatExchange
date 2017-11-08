import datetime

import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime, UniqueConstraint

from . import _base, server


class User(*_base.bases):
    __tablename__ = 'User'
    server_id = Column(Integer, ForeignKey('Server.meta_id'))
    _id_is_unique_per_server = UniqueConstraint('server_id', 'id')
    id = Column(Integer, nullable=False)

    name = Column(String)
    about = Column(String)
    is_moderator = Column(Boolean)
    message_count = Column(Integer)
    room_count = Column(Integer)
    reputation = Column(Integer)
    last_seen = Column(DateTime)
    last_message = Column(DateTime)

