from datetime import datetime, date
import time

from sqlalchemy import Sequence, Column, ForeignKey

# column types
from sqlalchemy import Integer, String, Unicode
from sqlalchemy import Boolean, Date, LargeBinary
from sqlalchemy import PickleType
from sqlalchemy import Enum
from sqlalchemy import DateTime

from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

####################################
## Data Types                     ##
####################################


FileType = Enum('agenda', 'minutes', 'attachment',
                name='file_type_enum')

AgendaItemType = Enum('presentation', 'policy', 'routine', 'unknown',
                      name='agenda_item_type_enum')

VoteType = Enum('Yea', 'Nay', 'Abstain', 'Absent', 'Present',
                name='vote_type_enum')

AgendaItemTypeMap = dict(V='presentation', VI='policy',
                         VII='routine')


CacheType = Enum('action', 'departments', 'item', 'meeting',
                 'people', 'rss-2011', 'rss-2012', 'rss-2013',
                 'rss-this-month',
                 name='cache_type_enum')

class SerialBase(object):
    def serialize(self):
        data = dict()
        table = self.__table__
        for column in table.columns:
            name = column.name
            try:
                pytype = column.type.python_type
            except NotImplementedError:
                print "NOTIMPLEMENTEDERROR", column.type
            value = getattr(self, name)
            if pytype is datetime or pytype is date:
                if value is not None:
                    value = value.isoformat()
            data[name] = value
        return data
    

    
####################################
## Tables                         ##
####################################

class URI(Base, SerialBase):
    __tablename__ = 'global_uri_table'
    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True)
    headers = Column(PickleType)
    created = Column(DateTime)
    updated = Column(DateTime)

