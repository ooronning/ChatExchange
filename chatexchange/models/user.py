import datetime

import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime, UniqueConstraint

from . import _base, server


class User(*_base.bases):
    __tablename__ = 'User'
    server_meta_id = Column(Integer, ForeignKey('Server.meta_id'))
    id = Column(Integer, nullable=False)

    name = Column(String)
    about = Column(String)
    is_moderator = Column(Boolean)
    message_count = Column(Integer)
    room_count = Column(Integer)
    reputation = Column(Integer)
    last_seen = Column(DateTime)
    last_message = Column(DateTime)

    __table_args__ = (
        UniqueConstraint('server_meta_id', 'id'),
    )
