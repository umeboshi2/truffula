import os, sys
import urlparse

import mechanize
from bs4 import BeautifulSoup

from .basecollector import BaseCollector
from .cachecollector import BaseCacheCollector


url_prefix = 'http://dendro.cnre.vt.edu/dendrology/'

toc_url = 'http://dendro.cnre.vt.edu/dendrology/data_results_with_common.cfm'

PICTURE_KEYS = ['flower', 'leaf', 'form', 'fruit', 'bark', 'twig', 'map']

class VTDendroCollector(BaseCollector):
    def __init__(self, cachedir='data'):
        super(VTDendroCollector, self).__init__()
        self.cache = BaseCacheCollector(cachedir=cachedir)
        self.set_url(toc_url)
        self.soup = None
        self.trees = dict()
        self.pagecollector = BaseCollector()
        

    def add_tree(self, href, genus, species, cname):
        if genus not in self.trees:
            self.trees[genus] = dict()
        url = os.path.join(url_prefix, href)
        data = self._get_tree_page_by_url(url)
        data['cname'] = cname
        
        #data = dict(common=cname, url=url)
        self.trees[genus][species] = data
        
        
    def get_page(self):
        data = self.cache.get(self.url)
        if data is None:
            self.retrieve_page()
            self.cache.save(self.url, self)
            data = self.cache.get(self.url)
        # FIXME: find a better way than this
        sys.setrecursionlimit(9500)
        self.soup = BeautifulSoup(data['content'])
        data['soup'] = BeautifulSoup(data['content'])
        return data
        
    def get_tree_anchors(self):
        if self.soup is None:
            self.get_page()
        anchors = self.soup.select('a')
        treelist = [a for a in anchors if 'syllabus/factsheet' in a.get('href')]
        return treelist

    def parse_tree_anchor(self, anchor):
        latin = anchor.select('em')[0].text.lower().split()
        common = anchor.text.strip().split(anchor.select('em')[0].text)[1].strip().split('- ')[1]
        if len(latin) == 2:
            genus, species = latin
            href = anchor.get('href')
            return dict(genus=genus, species=species, href=href, common=common)
        else:
            print "Unexpected latin", latin
        

    def get_tree_page(self, genus, species):
        url = self.trees[genus][species]['url']
        return self._get_tree_page_by_url(url)

    def _get_tree_info_from_page(self, soup):
        symbol = soup.select('span.BigText')[0].text.split('symbol:')[1].strip()
        if symbol == '--':
            symbol = None
        tinytext_selection = soup.select('.TinyText')
        tinytext_block = tinytext_selection[0]
        info = dict(symbol=symbol)
        for slabel in tinytext_block.select('strong'):
            key = slabel.text.split(':')[0].lower()
            value = unicode(slabel.next_sibling).strip()
            info[key] = value
        info['lookslike'] = list()
        try:
            looks_like_element = tinytext_block.next_sibling.next_sibling
        except AttributeError:
            return info
        if looks_like_element is None:
            return info
        if looks_like_element.text == 'Looks like:':
            for anchor in tinytext_block.parent.select('a'):
                href = anchor.get('href')
                llid = int(href.split('ID=')[1])
                info['lookslike'].append(llid)
        pictures = dict()
        image_elements = soup.select('img')
        for element in image_elements:
            src = element.get('src')
            if src.startswith('../images/'):
                key = element.get('alt')
                if key in PICTURE_KEYS:
                    pictures[key] = src
        info['pictures'] = pictures
        return info

    def _get_tree_page_by_url(self, url, data=None):
        page = self.cache.get(url)
        if page is None:
            print 'GET_TREE_PAGE', data
            self.pagecollector.retrieve_page(url)
            self.cache.save(url, self.pagecollector)
            page = self.cache.get(url)
        #page['soup'] = BeautifulSoup(page['content'])
        soup = BeautifulSoup(page['content'])
        page['soup'] = soup
        page['treeinfo'] = self._get_tree_info_from_page(soup)
        page['id'] = int(url.split('ID=')[1])
        return page
        
    def _get_tree_page(self, anchor):
        data = self.parse_tree_anchor(anchor)
        url = os.path.join(url_prefix, anchor['href'])
        return self._get_tree_page_by_url(url, data=data)
        
        
    def get_tree_pages(self):
        anchors = self.get_tree_anchors()
        import random ; random.shuffle(anchors)
        pages = [self._get_tree_page(a) for a in anchors]
        return pages

    def add_trees(self):
        for anchor in self.get_tree_anchors():
            p = self.parse_tree_anchor(anchor)
            if p is not None:
                self.add_tree(p['href'], p['genus'], p['species'], p['common'])
        
