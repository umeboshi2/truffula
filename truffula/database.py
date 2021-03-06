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

SimpleDescriptionType = Enum('flower', 'leaf', 'form', 'fruit',
                             'bark', 'twig',
                             name='simple_description_type_enum')

VTPictureType = Enum('flower', 'leaf', 'form', 'fruit',
                             'bark', 'twig', 'map',
                             name='vt_picture_type_enum')

####################################

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


class Genus(Base, SerialBase):
    __tablename__ = 'genus_list'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)

class GenusWiki(Base, SerialBase):
    __tablename__ = 'genus_wikipages'
    id = Column(Integer, ForeignKey('genus_list.id'), primary_key=True)
    content = Column(Unicode)

class SpecName(Base, SerialBase):
    __tablename__ = 'species_list'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    

class Species(Base, SerialBase):
    __tablename__ = 'species_table'
    genus_id = Column(Integer, ForeignKey('genus_list.id'), primary_key=True)
    spec_id = Column(Integer, ForeignKey('species_list.id'), primary_key=True)
    cname = Column(Unicode)

class SimpleDescription(Base, SerialBase):
    __tablename__ = 'simple_descriptions'
    id = Column(Integer, primary_key=True)
    type = Column(SimpleDescriptionType)
    text = Column(Unicode)
    

class VTSpecies(Base, SerialBase):
    __tablename__ = 'vt_species_table'
    id = Column(Integer, primary_key=True)
    genus_id = Column(Integer, ForeignKey('genus_list.id'))
    spec_id = Column(Integer, ForeignKey('species_list.id'))
    cname = Column(Unicode)
    symbol = Column(Unicode)
    flower = Column(Unicode)
    leaf = Column(Unicode)
    form = Column(Unicode)
    fruit = Column(Unicode)
    bark = Column(Unicode)
    twig = Column(Unicode)
    data = Column(PickleType)
    wikipage = Column(Unicode)
    
class VTLooksLike(Base, SerialBase):
    __tablename__ = 'vt_looks_likes'
    spec_id = Column(Integer, ForeignKey('vt_species_table.id'), primary_key=True)
    like_id = Column(Integer, ForeignKey('vt_species_table.id'), primary_key=True)

class VTPicture(Base, SerialBase):
    __tablename__ = 'vt_pictures'
    id = Column(Integer, ForeignKey('vt_species_table.id'), primary_key=True)
    type = Column(VTPictureType, primary_key=True)
    #text = Column(Unicode)
    url = Column(Unicode)
    
class WikiPage(Base, SerialBase):
    __tablename__ = 'wiki_pages'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    title = Column(Unicode)
    content = Column(Unicode)
    
#VTSpecies.like = relationship('vt_looks_likes.spec_id')
from sqlalchemy.orm.collections import attribute_mapped_collection

Genus.wiki = relationship(GenusWiki, uselist=False)

VTSpecies.pictures = relationship(
    VTPicture,
    collection_class=attribute_mapped_collection('type'))

VTSpecies.genus = relationship(Genus)
VTSpecies.species = relationship(SpecName)
VTSpecies.looklikes = relationship(VTSpecies,
                                   secondary='vt_looks_likes',
                                   primaryjoin=VTSpecies.id==VTLooksLike.spec_id,
                                   secondaryjoin=VTSpecies.id==VTLooksLike.like_id)

    
