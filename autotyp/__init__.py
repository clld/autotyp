from clld.web.app import get_configurator

# we must make sure custom models are known at database initialization!
from autotyp import models


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = get_configurator('autotyp', settings=settings)
    config.include('autotyp.datatables')
    config.include('autotyp.adapters')
    return config.make_wsgi_app()
