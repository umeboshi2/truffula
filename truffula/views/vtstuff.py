import os
from ConfigParser import ConfigParser
from datetime import datetime

from cornice.resource import resource, view

from trumpet.views.rest.base import BaseResource

from trumpet.models.usergroup import User

from truffula.managers.basic import GenusManager
from truffula.managers.basic import SpecNameManager
from truffula.managers.basic import VTSpeciesManager

from truffula.scrapers.vtdendro import url_prefix

APIROOT = '/rest/v0'

rscroot = os.path.join(APIROOT, 'main')

current_user = os.path.join(rscroot, 'current/user')

specname_path = os.path.join(rscroot, 'specname')
genus_path = os.path.join(rscroot, 'genus')
vtspecies_path = os.path.join(rscroot, 'vtspecies')

@resource(collection_path=genus_path,
          path=os.path.join(genus_path, '{name}'))
class GenusView(BaseResource):
    def __init__(self, request):
        super(GenusView, self).__init__(request)
        self.mgr = GenusManager(self.db)
        #self.limit = 25
        
    def collection_query(self):
        return self.mgr.query()
        

@resource(collection_path=specname_path,
          path=os.path.join(specname_path, '{name}'))
class SpecNameView(BaseResource):
    def __init__(self, request):
        super(SpecNameView, self).__init__(request)
        self.mgr = SpecNameManager(self.db)
        self.limit = 25
        
    def collection_query(self):
        return self.mgr.query()

        
@resource(collection_path=vtspecies_path,
          path=os.path.join(vtspecies_path, '{id}'))
class VTSpeciesView(BaseResource):
    def __init__(self, request):
        super(VTSpeciesView, self).__init__(request)
        self.mgr = VTSpeciesManager(self.db)
        self.limit = 25

    def serialize_object(self, dbobj):
        data = dict()
        for field in ['id', 'genus_id', 'spec_id', 'cname', 'symbol',
                      'flower', 'leaf', 'form', 'fruit', 'bark', 'twig']:
            data[field] = getattr(dbobj, field)
        data['genus'] = dbobj.genus.name
        data['species'] = dbobj.species.name
        data['pictures'] = dict()
        for key, pobj in dbobj.pictures.items():
            value = pobj.serialize()
            ipath = value['url'].split(url_prefix)[1].replace('%20', '_')
            base = self.request.route_url('home')
            value['localurl'] = '%svt%s' % (base, ipath)
            #import pdb ; pdb.set_trace()
            data['pictures'][key] = value
        return data
        
    def collection_query(self):
        query = self.mgr.query()
        GET = self.request.GET
        if 'genus_id' in GET:
            query = query.filter_by(genus_id=int(GET['genus_id']))
        return query

    def get(self):
        id = int(self.request.matchdict['id'])
        c = self.mgr.get(id)
        return self.serialize_object(c)
        
    
