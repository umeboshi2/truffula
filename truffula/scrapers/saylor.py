import os, sys
import urlparse
import multiprocessing
from multiprocessing.pool import ThreadPool

import mechanize
import requests
from bs4 import BeautifulSoup

from .basecollector import BaseCollector
from .cachecollector import BaseCacheCollector
from .util import download_pictures

url_prefix = 'http://www.saylorplants.com'
search_unit_url = os.path.join(url_prefix, 'pd_search_unit.html')
index_url = os.path.join(url_prefix, "pd_search_scientific.asp?range=%27all%27")
saylor_pid_url_marker = 'pd.asp?pid='

def get_pid_from_saylor_link(anchor):
    href = anchor.attrs['href']
    return int(href.split(saylor_pid_url_marker)[1])
    
class SaylorIndexCollector(BaseCollector):
    def __init__(self, cachedir='data', pictdir='images/saylor'):
        super(SaylorIndexCollector, self).__init__()
        self.cache = BaseCacheCollector(cachedir=cachedir)
        self.set_url(index_url)
        self.soup = None
        self.pagecollector = BaseCollector()
        self.pictdir = pictdir
        self.plants = dict()
        self.plant_anchors = dict()
        
    def make_picture_filename(self, url):
        raise RuntimeError, "Fix me"
        marker = url_prefix + 'images/'
        frag = url.split(marker)[1]
        frag = frag.replace('%20', '_')
        return os.path.join(self.pictdir, frag)

    def _make_paramlist(self):
        raise RuntimeError, "Build a list of image urls"
        paramlist = list()
        for genus in self.trees:
            for species in self.trees[genus]:
                treeinfo = self.trees[genus][species]['treeinfo']
                for ptype, url in treeinfo['pictures'].items():
                    filename = self.make_picture_filename(url)
                    paramlist.append((url, filename))
        return paramlist

    def download_pictures(self):
        paramlist = self._make_paramlist()
        for url, filename in paramlist:
            dirname = os.path.dirname(filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
        download_pictures(paramlist)
        
        
    def get_page(self):
        data = self.cache.get(self.url)
        if data is None:
            self.retrieve_page()
            self.cache.save(self.url, self)
            data = self.cache.get(self.url)
        # FIXME: find a better way than this
        sys.setrecursionlimit(9500)
        self.soup = self._make_soup(data['content'])
        data['soup'] = self._make_soup(data['content'])
        return data

    def get_plant_anchors(self):
        data = self.get_page()
        soup = data['soup']
        plist = [a for a in soup.select('a') if saylor_pid_url_marker in a.attrs['href']]
        for a in plist:
            pid = get_pid_from_saylor_link(a)
            if pid in self.plant_anchors:
                print "%s already in dictionary" % a.text
                continue
            self.plant_anchors[pid] = a

    def _get_page_by_url(self, url, data=None):
        page = self.cache.get(url)
        if page is None:
            print "Get SAYLOR PAGE", url
            self.pagecollector.retrieve_page(url)
            self.cache.save(url, self.pagecollector)
            page = self.cache.get(url)
        soup = self._make_soup(page['content'])
        page['soup'] = soup
        return page

    def get_saylor_plant_pages(self):
        pids = self.plant_anchors.keys()
        import random
        random.shuffle(pids)
        for pid in pids:
            anchor = self.plant_anchors[pid]
            url = os.path.join(url_prefix, anchor.attrs['href'])
            print "Processing page for %s" % anchor.text
            self._get_page_by_url(url)
            
            
        
