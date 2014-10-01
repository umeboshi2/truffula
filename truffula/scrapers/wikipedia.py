import os
import urlparse

import mechanize
from bs4 import BeautifulSoup

from .basecollector import BaseCollector
from .cachecollector import BaseCacheCollector

url_prefix = 'http://en.wikipedia.org/wiki/'


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
        
