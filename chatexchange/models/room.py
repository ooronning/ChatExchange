import datetime

import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime, UniqueConstraint

from . import base, server


class Room(base.Base):
    __tablename__ = 'Room'
    server_meta_id = Column(Integer, ForeignKey('Server.meta_id'))
    id = Column(Integer, nullable=False)

    name = Column(String)

    __table_args__ = (
        UniqueConstraint('server_meta_id', 'id'),
    )
