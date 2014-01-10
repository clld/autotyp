from sqlalchemy.orm import joinedload_all

from clld.web import datatables
from clld.web.datatables.base import Col, IdCol, LinkCol, LinkToMapCol
from clld.db.meta import DBSession

from autotyp.models import Languoid, Area, Continent


class Languages(datatables.Languages):
    def base_query(self, query):
        return query.join(Area).join(Continent).options(
            joinedload_all(Languoid.area, Area.continent)).distinct()

    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'name'),
            LinkToMapCol(self, 'l'),
            Col(self, 'latitude'),
            Col(self, 'longitude'),
            Col(self, 'area',
                model_col=Area.name,
                get_object=lambda i: i.area,
                choices=[a.name for a in DBSession.query(Area)]),
            Col(self, 'continent',
                model_col=Continent.name,
                get_object=lambda i: i.area.continent,
                choices=[a.name for a in DBSession.query(Continent)]),
        ]


def includeme(config):
    config.register_datatable('languages', Languages)
