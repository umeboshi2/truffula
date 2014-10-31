from sqlalchemy.orm.exc import NoResultFound
import transaction


from truffula.database import Genus, SpecName
from truffula.database import VTSpecies
from truffula.database import WikiPage


class BaseManager(object):
    def __init__(self, session):
        self.session = session

    def query(self):
        return self.session.query(self.dbmodel)

    def get(self, id):
        return self.query().get(id)

class GetByNameManager(BaseManager):
    def get_by_name_query(self, name):
        return self.query().filter_by(name=name)

    def get_by_name(self, name):
        q = self.get_by_name_query(name)
        try:
            return q.one()
        except NoResultFound:
            return None

    
class GenusManager(GetByNameManager):
    dbmodel = Genus

class SpecNameManager(BaseManager):
    dbmodel = SpecName

class VTSpeciesManager(BaseManager):
    dbmodel = VTSpecies

class WikiPageManager(GetByNameManager):
    dbmodel = WikiPage
    
