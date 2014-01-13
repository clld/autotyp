from sqlalchemy import and_
from sqlalchemy.orm import joinedload_all, joinedload, aliased

from clld.web import datatables
from clld.db.meta import DBSession
from clld.db.models.common import (
    Value, ValueSet, Parameter, DomainElement, Language, Contribution, ValueSetReference,
    Value_data,
)
from clld.db.util import icontains
from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol, IdCol,
)
from clld.web.util.helpers import linked_references, map_marker_img
from clld.web.util.htmllib import HTML, literal

from autotyp.models import Languoid, Area, Continent


class ValueNameCol(LinkCol):
    def get_obj(self, item):
        return item.valueset

    def get_attrs(self, item):
        label = item.__unicode__()
        title = label
        return {'label': label, 'title': title}

    def order(self):
        return Value.name

    def search(self, qs):
        return icontains(Value.name, qs)


class ValueDataCol(LinkCol):
    def get_obj(self, item):
        return item.valueset

    def get_attrs(self, item):
        label = ''
        for d in item.data:
            if d.ord == self.index:
                label = d.value
                break
        return {'label': label}

    def __init__(self, dt, name, index, spec, **kw):
        kw['sTitle'] = spec[0]
        Col.__init__(self, dt, name, **kw)
        self.index = index
        self.choices = spec[1]

    def search(self, qs):
        return icontains(self.dt.vars[self.index].value, qs)


class ValueSetCol(LinkCol):
    def get_obj(self, item):
        return item.valueset

    def get_attrs(self, item):
        return {'label': item.valueset.name}


class Values(DataTable):
    __constraints__ = [Parameter, Contribution, Language]

    def __init__(self, req, model, eid=None, **kw):
        DataTable.__init__(self, req, model, eid=eid, **kw)
        self.vars = []
        if self.parameter:
            self.vars = [aliased(Value_data, name='var%s' % i) for i in range(len(self.parameter.jsondata['varspec']))]

    def base_query(self, query):
        query = query.join(ValueSet).options(
            joinedload_all(Value.valueset, ValueSet.references, ValueSetReference.source)
        )

        if self.language:
            query = query.join(ValueSet.parameter)
            return query.filter(ValueSet.language_pk == self.language.pk)
        if self.parameter:
            for i, var in enumerate(self.vars):
                query = query.join(var, and_(var.ord == i, var.object_pk == Value.pk))

            query = query.join(ValueSet.language)
            query = query.outerjoin(DomainElement).options(
                joinedload(Value.domainelement))
            return query.filter(ValueSet.parameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(ValueSet.parameter)
            return query.filter(ValueSet.contribution_pk == self.contribution.pk)

        return query

    def col_defs(self):
        if self.parameter:
            res = [
                LinkCol(self, 'language',
                        model_col=Language.name, get_object=lambda i: i.valueset.language),
                LinkToMapCol(self, 'm', get_object=lambda i: i.valueset.language),
            ]
            for i, spec in enumerate(self.parameter.jsondata['varspec']):
                res.append(ValueDataCol(self, 'var%s' % i, i, spec))
            return res

        if self.language:
            return [
                ValueNameCol(self, 'value'),
                LinkCol(self, 'parameter', sTitle=self.req.translate('Parameter'),
                        model_col=Parameter.name, get_object=lambda i: i.valueset.parameter),
            ]

        return [
            ValueNameCol(self, 'value'),
            ValueSetCol(self, 'valueset', bSearchable=False, bSortable=False),
        ]


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
    config.register_datatable('values', Values)
    config.register_datatable('languages', Languages)
