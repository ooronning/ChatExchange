import datetime

import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime, UniqueConstraint

from . import base


class Server(base.Base):
    __tablename__ = 'Server'
    meta_id = Column(Integer, primary_key=True)

    name = Column(String)
    url = Column(String)
    slug = Column(String)
    _slug_is_unique = UniqueConstraint('slug')
