from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from trumpet.models.usergroup import User, Password


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    settings['db.sessionmaker'] = DBSession
    settings['db.usermodel'] = User
    settings['db.password_model'] = Password
    settings['db.usernamefield'] = 'username'
    


    DBSession.configure(bind=engine)
    Base.metadata.bind = engine


    root_factory = 'trumpet.resources.RootGroupFactory'
    request_factory = 'trumpet.request.AlchemyRequest'
    
    config = Configurator(settings=settings)
    includes = ['cornice', 'pyramid_beaker']
    for i in includes:
        config.include(i)
    client_view = 'truffula.views.client.ClientView'
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()
