import os
import urlparse

import mechanize
from bs4 import BeautifulSoup

from .basecollector import BaseCollector
from .cachecollector import BaseCacheCollector

url_prefix = 'http://en.wikipedia.org/wiki/'


WIKIPEDIA_GENUS_ONLY = ['weigela', 'hypericum', 'gaylussacia', 'diplacus',
                        'lippia', 'styphnolobium', 'musa', 'ephedra', 'gambelia',
                        'citrus', 'cistus', 'ditrysinia', 'forsythia',
                        'bougainvillea', 'callistemon', 'cotoneaster',
                        'crataegus', 'malus', 'stewartia', 'xcupressocyparis',
                        'casuarina']

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
    populus=['populus'],
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

WIKIPEDIA_NO_GENUS = ['diplacus', 'pyrularia', 'buckleya',
                      'pinckneya', 'xcupressocyparis']

class WikiCollector(BaseCollector):
    def __init__(self, cachedir='data'):
        super(WikiCollector, self).__init__()
        self.cache = BaseCacheCollector(cachedir=cachedir)
        self.pagecollector = BaseCollector()

    def _tree_url(self, genus, species):
        page = '%s_%s' % (genus.capitalize(), species)
        return os.path.join(url_prefix, page)
        
    def _get_url(self, url):
        data = self.cache.get(url)
        if data is None:
            print "Retrieving %s" % url
            self.pagecollector.retrieve_page(url)
            self.cache.save(url, self.pagecollector)
            data = self.cache.get(url)
        return data

    def get_page(self, genus, species):
        url = self._tree_url(genus, species)
        return self._get_url(url)
        
    def get_genus_page(self, genus):
        url = os.path.join(url_prefix, genus.capitalize())
        return self._get_url(url)
        


def get_wikipedia_pages_for_vt(treedata):
    wc = WikiCollector()
    genus_list = treedata.keys()
    genus_list.sort()
    for genus in genus_list:
        if genus not in WIKIPEDIA_NO_GENUS:
            wc.get_genus_page(genus)
        for species in treedata[genus]:
            if genus in WIKIPEDIA_GENUS_ONLY:
                break
            missing = WIKIPEDIA_MISSING_SPECIES
            if genus in missing and species in missing[genus]:
                print "Skipping %s %s" % (genus, species)
                continue
            if genus == 'morella':
                print "Genus myrica substituted for genus morella"
                genus = 'myrica'
            if genus == 'pyrularia':
                species = genus
                genus = 'clermontia'
                msg = "%s is %s %s on wikipedia."
                print msg % (species.capitalize(), genus, species)
            if genus == 'abies' and species == 'nordmannia':
                species = 'nordmanniana'
                print "%s %s on wikipedia." % (genus.capitalize(), species)
            if genus == 'heptacodium' and species == 'miconoides':
                species = 'miconioides'
                print "%s %s on wikipedia." % (genus.capitalize(), species)
            wc.get_page(genus, species)
            
            
            
def get_wikipedia_pages_for_silvics(treedata):
    wc = WikiCollector()
    genus_list = treedata.keys()
    genus_list.sort()
    for genus in genus_list:
        if genus != 'manikara':
            wc.get_genus_page(genus)
        for species in treedata[genus]:
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
            
