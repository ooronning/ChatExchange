import datetime

import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime, UniqueConstraint

from . import _base, server


class Room(*_base.bases):
    __tablename__ = 'Room'
    server_id = Column(Integer, ForeignKey('Server.meta_id'))
    _id_is_unique_per_server = UniqueConstraint('server_id', 'id')
    id = Column(Integer, nullable=False)

    name = Column(String)
