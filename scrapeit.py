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
from truffula.vtdendro import VTDendroCollector

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


WIKIPEDIA_MISSING_SPECIES = dict(
    abelia=['xgrandiflora'],
    anisacanthus=['quadrifidus'],
    baccharis=['pteronioides'],
    bursera=['hindsiana'],
    carya=['pallida'],
    cercis=['orbiculata'],
    corylopsis=['glabrescens', 'sinensis'],
    cylindropuntia=['arbuscula'],
    deutzia=['scabra'],
    ebenopsis=['confinis'],
    ericameria=['palmeri'],
    erythrina=['corallodendron'],
    eucalyptus=['torelliana'],
    euonymus=['kiautschovicus'],
    gelsemium=['rankinii'],
    hamamelis=['xintermedia'],
    ilex=['xattenuata', 'myrtifolia'],
    jatropha=['cuneata'],
    laburnum=['xwatereri'],
    larix=['xmarschlinsii'],
    lonicera=['xbella'],
    lyonia=['ferruginea'],
    lysiloma=['candidum', 'watsonii'],
    magnolia=['xsoulangiana'],
    nolina=['texana'],
    opuntia=['rufida'],
    paulownia=['fortunei'],
    penstemon=['ellipticus'],
    philadelphus=['pubescens', 'inodorus'],
    photinia=['xfraseri'],
    prunus=['xyedoensis'],
    quercus=['margarettae', 'sinuata'],
    rhododendron=['albiflorum', 'canescens'],
    rhus=['lentii'],
    ribes=['acerifolium', 'rotundifolium'],
    smilax=['tamnoides'],
    styrax=['japonicus'],
    taxus=['xmedia'],
    tilia=['petiolaris'],
    viburnum=['dilatatum', 'xburkwoodii'],
    )



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

vc.get_tree_pages()
vc.add_trees()

trees = vc.trees.keys()
for genus in trees:
    if genus not in ['diplacus', 'pyrularia', 'buckleya',
                     'pinckneya', 'xcupressocyparis']:
        wc.get_genus_page(genus)
    for species in vc.trees[genus]:
        if genus in ['weigela', 'hypericum', 'gaylussacia', 'diplacus',
                     'lippia', 'styphnolobium', 'musa', 'ephedra', 'gambelia',
                     'citrus', 'cistus', 'ditrysinia', 'forsythia',
                     'bougainvillea', 'callistemon', 'cotoneaster',
                     'crataegus', 'malus', 'stewartia', 'xcupressocyparis']:
            continue
        skip_species = False
        for key in WIKIPEDIA_MISSING_SPECIES:
            if genus == key and species in WIKIPEDIA_MISSING_SPECIES[key]:
                print "Skipping %s %s" % (genus, species)
                skip_species = True
                continue
        if skip_species:
            continue
        if genus == 'morella':
            genus = 'myrica'
        if genus == 'pyrularia':
            species = genus
            genus = 'clermontia'
        if genus == 'abies' and species == 'nordmannia':
            species = 'nordmanniana'
        if genus == 'heptacodium' and species == 'miconoides':
            species = 'miconioides'
            
        wc.get_page(genus, species)
        
url = make_tree_url(url_prefix, 'carpinus', 'caroliniana')

