import datetime

import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime

from . import _base


class Server(_base.Base):
    __tablename__ = 'Server'
    meta_id = Column(Integer, primary_key=True)

    name = Column(String)
    url = Column(String)
    slug = Column(String)
