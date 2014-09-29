import os
import urlparse

import mechanize
from bs4 import BeautifulSoup

from truffula.basecollector import BaseCollector
from truffula.cachecollector import BaseCacheCollector

url_prefix = 'http://www.na.fs.fed.us/spfo/pubs/silvics_manual/volume_2/'

toc_url = os.path.join(url_prefix, 'vol2_Table_of_contents.htm')

class SilvicsToCCollector(BaseCollector):
    def __init__(self, cachedir='data'):
        super(SilvicsToCCollector, self).__init__()
        self.cache = BaseCacheCollector(cachedir=cachedir)
        self.set_url(toc_url)
        self.soup = None
        self.trees = dict()
        self.pagecollector = BaseCollector()
        

    def add_tree(self, href, genus, species, cname):
        if genus not in self.trees:
            self.trees[genus] = dict()
        url = os.path.join(url_prefix, href)
        self.trees[genus][species] = cname
        
        
    def get_page(self):
        data = self.cache.get(self.url)
        if data is None:
            self.retrieve_page()
            self.cache.save(self.url, self)
            data = self.cache.get(self.url)
        self.soup = BeautifulSoup(data['content'])
        data['soup'] = BeautifulSoup(data['content'])
        return data
        
    def get_link_info(self):
        if self.soup is None:
            self.get_page()
        anchors = self.soup.select('a')
        tree_and_env, general_notes = anchors[:2]
        
        treelist = anchors[2:-8]
        other_links = anchors[-8:]
        data = dict(tree_and_env=tree_and_env, general_notes=general_notes,
                    treelist=treelist, other_links=other_links)
        tree_info = list()
        anchor_count = 0
        for anchor in treelist:
            anchor_count += 1
            if not anchor_count % 2:
                href = anchor.get('href').strip()
                #print anchor, anchor_count
                genus, specfile = os.path.split(href)
                cname = anchor.text
                if not specfile.endswith('.htm'):
                    raise RuntimeError, "Bad link %s" % href
                species = specfile[:-4]
                if species.endswith('%20'):
                    #print 'stripping %20 from species %s' % species
                    species = species[:-3]
                self.add_tree(href, genus, species, cname)
                print "Added %s (%s %s)" % (cname, genus, species)
                tree_url = os.path.join(url_prefix, href)
                tree_data = self.cache.get(tree_url)
                if tree_data is None:
                    self.pagecollector.retrieve_page(tree_url)
                    self.cache.save(tree_url, self.pagecollector)
                    print tree_url

                
              
        
