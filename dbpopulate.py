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
from truffula.database import VTLooksLike



here = os.getcwd()
settings = {'sqlalchemy.url' : 'sqlite:///%s/truffula.sqlite' % here}
engine = engine_from_config(settings)
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)

s = Session()

vc = VTDendroCollector()
vc.add_trees()

# populate with VTDendroCollector
genus_list = vc.trees.keys()
genus_list.sort()
for genus in genus_list:
    q = s.query(Genus).filter_by(name=genus).all()
    if not len(q):
        g = Genus()
        g.name = genus
        s.add(g)
        #s.commit()
        
for genus in genus_list:
    for species in vc.trees[genus]:
        if species in ['spp.']:
            continue
        q = s.query(SpecName).filter_by(name=species).all()
        if not len(q):
            sp = SpecName()
            sp.name = species
            s.add(sp)
            #s.commit()
        else:
            print "Species %s already present." % species
            

for genus in vc.trees:
    for species in vc.trees[genus]:
        if species in ['spp.']:
            continue
        data = vc.trees[genus][species]
        sp = s.query(VTSpecies).get(data['id'])
        if sp is None:
            print data['treeinfo']
            sp = VTSpecies()
            spec_id = data['id']
            sp.id = spec_id
            g = s.query(Genus).filter_by(name=genus).one()
            sn = s.query(SpecName).filter_by(name=species).one()
            sp.genus_id = g.id
            sp.spec_id = sn.id
            if 'soup' in data:
                del data['soup']
            sp.cname = data['cname']
            treeinfo = data['treeinfo']
            for key, value in treeinfo.items():
                setattr(sp, key, value)
            for like_id in treeinfo['lookslike']:
                ll = s.query(VTLooksLike).get((spec_id, like_id))
                if ll is None:
                    ll = VTLooksLike()
                    ll.spec_id = spec_id
                    ll.like_id = like_id
                    s.add(ll)
            sp.data = data
            s.add(sp)
            #s.commit()
            
s.commit()
