import os
from ConfigParser import ConfigParser
from datetime import datetime
from urllib2 import HTTPError

from cornice.resource import resource, view
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from bs4 import BeautifulSoup
import transaction

from trumpet.views.rest.base import BaseResource

from trumpet.models.usergroup import User

from truffula.database import WikiPage
from truffula.managers.basic import WikiPageManager
from truffula.scrapers.wikipedia import WikiCollector, cleanup_wiki_page


from truffula.scrapers.vtdendro import url_prefix

APIROOT = '/rest/v0'

rscroot = os.path.join(APIROOT, 'main')

wiki_path = os.path.join(rscroot, 'wikipage')

@resource(collection_path=wiki_path,
          path=os.path.join(wiki_path, '{name}'))
class WikiPageView(BaseResource):
    def __init__(self, request):
        super(WikiPageView, self).__init__(request)
        self.mgr = WikiPageManager(self.db)
        self.wikicollector = WikiCollector()
        self.limit = 25

    def collection_query(self):
        return self.mgr.query()

    def get(self):
        name = self.request.matchdict['name']
        p = self.mgr.get_by_name(name)
        if p is None:
            try:
                data = self.wikicollector.get_wiki_page(name)
            except HTTPError, e:
                data = None
            if data is not None:
                with transaction.manager:
                    p = WikiPage()
                    p.name = name
                    soup = cleanup_wiki_page(data['content'])
                    p.content = unicode(soup.body)
                    self.db.add(p)
                p = self.db.merge(p)
        return self.serialize_object(p)

