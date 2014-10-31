#!/usr/bin/env python
import os, sys
import cPickle as Pickle
from urllib2 import HTTPError

from bs4 import BeautifulSoup
from sqlalchemy import engine_from_config
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from truffula.scrapers.silvicstoc import SilvicsToCCollector
from truffula.scrapers.wikipedia import WikiCollector
from truffula.scrapers.vtdendro import VTDendroCollector, TREEINFO_KEYS

from truffula.scrapers.wikipedia import get_wikipedia_pages_for_vt
from truffula.scrapers.wikipedia import get_wikipedia_pages_for_silvics
from truffula.scrapers.wikipedia import WikiCollector, cleanup_wiki_page

from truffula.database import Base, URI
from truffula.database import Genus, GenusWiki, SpecName
from truffula.database import Species, VTSpecies
from truffula.database import VTLooksLike, VTPicture



here = os.getcwd()
settings = {'sqlalchemy.url' : 'sqlite:///%s/truffula.sqlite' % here}
engine = engine_from_config(settings)
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)

s = Session()

wiki_collector = WikiCollector()
vctrees_filename = 'vctrees.pickle'
if os.path.isfile(vctrees_filename):
    print "Loading from %s" % vctrees_filename
    vctrees = Pickle.load(file(vctrees_filename))
else:
    vc = VTDendroCollector()
    vc.add_trees()
    for genus in vc.trees:
        for spec in vc.trees[genus]:
            for key in ['info', 'soup']:
                if key in vc.trees[genus][spec]:
                    del vc.trees[genus][spec][key]
    with file(vctrees_filename, 'w') as outfile:
        Pickle.dump(vc.trees, outfile)
    vctrees = vc.trees

# populate with VTDendroCollector
genus_list = vctrees.keys()
genus_list.sort()

for genus in genus_list:
    q = s.query(Genus).filter_by(name=genus).all()
    if not len(q):
        g = Genus()
        g.name = genus
        s.add(g)
        g = s.merge(g)
        gw = GenusWiki()
        gw.id = g.id
        try:
            wpage = wiki_collector.get_genus_page(genus)
        except HTTPError, e:
            wpage = None
        if wpage is not None:
            soup = cleanup_wiki_page(wpage['content'])
            gw.content = unicode(soup.body)
        s.add(gw)
        
        #s.commit()
        
for genus in genus_list:
    for species in vctrees[genus]:
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
            

for genus in vctrees:
    for species in vctrees[genus]:
        if species in ['spp.']:
            continue
        data = vctrees[genus][species]
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
            for key in TREEINFO_KEYS:
                if key in treeinfo:
                    setattr(sp, key, treeinfo[key])
            for like_id in treeinfo['lookslike']:
                ll = s.query(VTLooksLike).get((spec_id, like_id))
                if ll is None:
                    ll = VTLooksLike()
                    ll.spec_id = spec_id
                    ll.like_id = like_id
                    s.add(ll)
            pix = treeinfo['pictures']
            for ptype in pix:
                px = s.query(VTPicture).get((spec_id, ptype))
                if px is None:
                    px = VTPicture()
                    px.id = spec_id
                    px.type = ptype
                    px.url = pix[ptype]
                    s.add(px)
                    print "px.type", px.type, px.url
            #import pdb ; pdb.set_trace()
            sp.data = data
            try:
                wpage = wiki_collector.get_page(genus, species)
            except HTTPError, e:
                wpage = None
            #print "WPAGE IS", wpage
            if wpage is not None:
                soup = cleanup_wiki_page(wpage['content'])
                sp.wikipage = unicode(soup.body)
            s.add(sp)
            #s.commit()
            
s.commit()
