from sqlalchemy.orm import joinedload

from clld.interfaces import IParameter, IValue, IIndex
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet
from clld.web.adapters.base import Index
from clld.web.adapters.geojson import GeoJsonParameter
from clld.web.maps import SelectedLanguagesMap


class GeoJsonFeature(GeoJsonParameter):
    def feature_iterator(self, ctx, req):
        return DBSession.query(ValueSet).filter(ValueSet.parameter_pk == ctx.pk)\
            .options(joinedload(ValueSet.language))

    def feature_properties(self, ctx, req, valueset):
        return {}


class MapView(Index):
    extension = str('map.html')
    mimetype = str('text/vnd.clld.map+html')
    send_mimetype = str('text/html')
    template = 'language/map_html.mako'

    def template_context(self, ctx, req):
        languages = list(v.valueset.language for v in ctx.get_query(limit=8000))
        return {
            'map': SelectedLanguagesMap(ctx, req, languages),
            'languages': languages}


def includeme(config):
    config.register_adapter(GeoJsonFeature, IParameter)
    config.register_adapter(MapView, IValue, IIndex)
