from sqlalchemy.orm import joinedload

from clld.interfaces import IParameter
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet
from clld.web.adapters.geojson import GeoJsonParameter


class GeoJsonFeature(GeoJsonParameter):
    def feature_iterator(self, ctx, req):
        return DBSession.query(ValueSet).filter(ValueSet.parameter_pk == ctx.pk)\
            .options(joinedload(ValueSet.language))

    def feature_properties(self, ctx, req, valueset):
        return {}


def includeme(config):
    config.register_adapter(GeoJsonFeature, IParameter)
