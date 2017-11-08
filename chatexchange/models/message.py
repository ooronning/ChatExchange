import datetime

import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime, UniqueConstraint

from . import base, server


class Message(base.Base):
    __tablename__ = 'Message'
    server_meta_id = Column(Integer, ForeignKey('Server.meta_id'))
    room_meta_id = Column(Integer, ForeignKey('Room.meta_id'))
    owner_meta_id = Column(Integer, ForeignKey('User.meta_id'))

    id = Column(Integer, nullable=False)

    content_html = Column(String)
    content_text = Column(String)
    content_markdown = Column(String)

    __table_args__ = (
        UniqueConstraint('server_meta_id', 'id'),
    )
