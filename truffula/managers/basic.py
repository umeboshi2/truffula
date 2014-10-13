from sqlalchemy.orm.exc import NoResultFound
import transaction


from truffula.database import Genus, SpecName
from truffula.database import VTSpecies


class BaseManager(object):
    def __init__(self, session):
        self.session = session

    def query(self):
        return self.session.query(self.dbmodel)

    def get(self, id):
        return self.query().get(id)

class GenusManager(BaseManager):
    dbmodel = Genus

class SpecNameManager(BaseManager):
    dbmodel = SpecName

class VTSpeciesManager(BaseManager):
    dbmodel = VTSpecies
