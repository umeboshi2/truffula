#!/usr/bin/env python
import os, sys
import cPickle as Pickle

from sqlalchemy import engine_from_config
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from truffula.basecollector import BaseCollector
from truffula.cachecollector import BaseCacheCollector
from truffula.silvicstoc import SilvicsToCCollector
from truffula.wikipedia import WikiCollector

from truffula.database import Base, URI

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
bc = BaseCollector()
cc = BaseCacheCollector()

sc = SilvicsToCCollector()
sc.get_link_info()
wc = WikiCollector()
for genus in sc.trees:
    if genus not in ['manikara']:
        #print "Getting genus %s" % genus
        wc.get_genus_page(genus)
    for species in sc.trees[genus]:
        if species == 'nutallii':
            species = 'texana'
        # no wiki page for tabebuia heterophylla
        if genus == 'tabebuia' and species == 'heterophylla':
            continue
        if genus == 'nyssa' and species == 'silvatica':
            species = 'sylvatica'
        if genus == 'casuarina':
            print "Skipping Casuarina"
            continue
        if genus == 'populus' and species == 'populus':
            print "Skipping Populus populus"
            continue
        if genus == 'castanopsis' and species == 'chrysophylla':
            genus = 'chrysolepis'
            print "Getting genus page for %s" % genus
            wc.get_genus_page(genus)
            print 'Getting Chrysolepis chrysophylla'
            wc.get_page(genus, species)
        if genus == 'manikara':
            print "Getting sapodilla"
            wc.get_page('manilkara', 'zapota')
            continue
        if genus == 'carya':
            if species == 'myristicformis':
                species = 'myristiciformis'
            if species == 'illinoesis':
                species = 'illinoinensis'
        if genus == 'cedrela' and species == 'ordota':
            species = 'odorata'
        if genus == 'magnolia' and species == 'accuminata':
            species = 'acuminata'
        wc.get_page(genus, species)
        

url = make_tree_url(url_prefix, 'carpinus', 'caroliniana')

