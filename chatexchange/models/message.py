import datetime

import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime, UniqueConstraint

from . import _base, server


class Message(*_base.bases):
    __tablename__ = 'Message'
    server_id = Column(Integer, ForeignKey('Server.meta_id'))
    _id_is_unique_per_server = UniqueConstraint('server_id', 'id')
    id = Column(Integer, nullable=False)

    owner_id = Column(Integer)

    content_html = Column(String)
    content_text = Column(String)
    content_markdown = Column(String)
