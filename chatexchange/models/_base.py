import datetime

import hashids
import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime
import sqlalchemy.ext.declarative


class Base(sqlalchemy.ext.declarative.declarative_base()):
    __tablename__ = None
    meta_id = Column(Integer, primary_key=True)
    meta_created = Column(DateTime, default=datetime.datetime.now)
    meta_updated = Column(DateTime, onupdate=datetime.datetime.now)

    @property
    def meta_slug(self):
        meta_slug ,= hashids.Hashids(salt=self.__tablename__).encode(self.meta_id)
        return meta_slug

    @classmethod
    def meta_id_from_meta_slug(cls, meta_slug):
        meta_id, = hashids.Hashids(salt=cls.__tablename__).decode(meta_slug)
        return meta_id


STACK_EPOCH = datetime.datetime.fromtimestamp(1217514151)
