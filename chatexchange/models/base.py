import datetime
import hashlib
import hmac

import hashids
import sqlalchemy
from sqlalchemy import Column, String, Integer, Index, ForeignKey, Boolean, DateTime
import sqlalchemy.ext.declarative

from .. import _obj_dict



_key = 'adbbf3aa342bc82736d0ee71b2a0650e05b2edd21082e1291ae161777550ba0c71002b9ce3ad7aa19c8a4641223f8f4e82bab7ebbf5335d01046cdc5a462bdfe'


class Base(object):
    __tablename__ = None

    meta_id = Column(Integer, primary_key=True)
    meta_created = Column(DateTime, default=datetime.datetime.now)
    meta_updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    meta_deleted = Column(DateTime, default=None)

    __init__ = _obj_dict.update
    set = _obj_dict.updated
    
    __repr__ = _obj_dict.repr

    @property
    def deleted(self):
        return self.meta_deleted is not None

    @property
    def meta_slug(self):
        """
        Produces a short obfuscated (NOT SECURE!) slug encoding .meta_id.

        I like to use these so that we have an identifier for these instances
        that is clearly not their official room/message IDs.
        """
        salt = ''.join(chr(n) for n in hmac.new(_key, self.__tablename__, hashlib.sha512).digest())
        min_length = 4
        slugger = hashids.Hashids(salt=salt, min_length=min_length)
        meta_slug ,= slugger.encode(self.meta_id)
        return meta_slug

    @classmethod
    def meta_id_from_meta_slug(cls, meta_slug):
        salt = ''.join(chr(n) for n in hmac.new(_key, cls.__tablename__, hashlib.sha512).digest())
        min_length = 4
        slugger = hashids.Hashids(salt=salt, min_length=min_length)
        meta_id, = slugger.decode(meta_slug)
        return meta_id


Base = sqlalchemy.ext.declarative.declarative_base(cls=Base)
