#!/usr/bin/env python
import os, sys
import cPickle as Pickle

from sqlalchemy import engine_from_config
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from truffula.scrapers.silvicstoc import SilvicsToCCollector
from truffula.scrapers.wikipedia import WikiCollector
from truffula.scrapers.vtdendro import VTDendroCollector

from truffula.scrapers.wikipedia import get_wikipedia_pages_for_vt
from truffula.scrapers.wikipedia import get_wikipedia_pages_for_silvics
from truffula.database import Base, URI
from truffula.database import Genus, SpecName
from truffula.database import Species, VTSpecies



url_prefix = 'http://www.na.fs.fed.us/spfo/pubs/silvics_manual/volume_2/'

toc = os.path.join(url_prefix, 'vol2_Table_of_contents.htm')

def make_tree_url(prefix, genus, species):
    return os.path.join(prefix, genus, '%s.htm' % species)
    
here = os.getcwd()
settings = {'sqlalchemy.url' : 'sqlite:///%s/truffula.sqlite' % here}
engine = engine_from_config(settings)
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)

s = Session()

vc = VTDendroCollector()

GENUS_MISSPELLS = dict(manilkara='manikara')
SPECIES_MISSPELLS = dict(
    nyssa=dict(
        sylvatica='silvatica'),
    carya=dict(
        myristiciformis='myristicformis',
        illinoinensis='illinoesis'),
    cedrela=dict(
        odorata='ordota'),
    magnolia=dict(
        acuminata='accuminata'))

vc.get_tree_pages()
vc.add_trees()
get_wikipedia_pages_for_vt(vc.trees)

print "Getting silvics info..."
sc = SilvicsToCCollector()
wc = WikiCollector()

sc.get_link_info()

get_wikipedia_pages_for_silvics(sc.trees)
