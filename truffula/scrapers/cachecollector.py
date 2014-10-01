import os
import cPickle as Pickle
from datetime import datetime
import uuid

from .basecollector import BaseCollector

def make_uuid_from_url(url):
    return uuid.uuid5(uuid.NAMESPACE_URL, bytes(url))
    

class BaseCacheCollector(object):
    def __init__(self, cachedir='data'):
        self.cachedir = cachedir
        if not os.path.isdir(cachedir):
            os.makedirs(cachedir)
            

    def filename(self, url):
        return os.path.join(self.cachedir, '%s.pickle' % make_uuid_from_url(url))

    def get(self, url):
        filename = self.filename(url)
        if os.path.isfile(filename):
            return Pickle.load(file(filename))
        else:
            return None

    def save(self, url, collector):
        filename = self.filename(url)
        with file(filename, 'w') as outfile:
            c = collector
            data = dict(info=c.info, content=c.content, url=c.url)
            Pickle.dump(data, outfile)
            
            
