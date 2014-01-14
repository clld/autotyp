from __future__ import unicode_literals
import sys
import csv
import codecs
from itertools import groupby
from getpass import getuser

from clld.scripts.util import (
    initializedb, Data, bibtex2source, glottocodes_by_isocode, add_language_codes,
)
from clld.db.meta import DBSession
from clld.db.models import common
from clld.util import slug
from clld.lib.dsv import rows
from clld.lib.bibtex import Database

import autotyp
from autotyp import models


def coord(value):
    return float(value) if value else None


def main(args):
    glottocodes = {}
    if getuser() == 'robert':
        glottocodes = glottocodes_by_isocode('postgresql://robert@/glottolog3')

    data = Data()
    dataset = common.Dataset(
        id=autotyp.__name__,
        name="AUTOTYP",
        description="AUTOTYP",
        domain='autotyp.clld.org')
    DBSession.add(dataset)

    bib = Database.from_file(args.data_file('LenaBib.bib'), lowercase=True)

    for i, spec in enumerate([
        ('bickel', "Balthasar Bickel", "University of Zurich"),
        ('nichols', "Johanna Nichols", "University of California, Berkeley"),
    ]):
        DBSession.add(common.Editor(
            dataset=dataset,
            ord=i + 1,
            contributor=common.Contributor(id=spec[0], name=spec[1])))

    for l in rows(args.data_file('backbone_09Jan2014_directexport.tab'), newline='\r', encoding='macroman', namedtuples=True):
        #LID	language	ISO639.3.2013	stock	continent	area	latitude	longitude
        if l.stock not in data['Stock']:
            stock = data.add(
                models.Stock, l.stock,
                id=slug(l.stock), name=l.stock)
        else:
            stock = data['Stock'][l.stock]

        if l.continent not in data['Continent']:
            continent = data.add(
                models.Continent, l.continent,
                id=slug(l.continent), name=l.continent)
        else:
            continent = data['Continent'][l.continent]

        if l.area not in data['Area']:
            area = data.add(
                models.Area, l.area,
                id=slug(l.area), name=l.area, continent=continent)
        else:
            area = data['Area'][l.area]

        lang = data.add(
            models.Languoid, l.LID,
            id=l.LID,
            name=l.language,
            latitude=coord(l.latitude),
            longitude=coord(l.longitude),
            stock=stock,
            area=area)
        add_language_codes(data, lang, l.ISO639_3_2013, glottocodes=glottocodes)

    varspec = [
        ('alignment', set()),
        ('referential_type', set()),
        ('tense_aspect', set()),
        ('morphological_form.PoS', set()),
        ('A.marked', set()),
        ('P.marked', set())]
    p = data.add(
        common.Parameter, 'case.alignment',
        id='1',
        name='case alignment')
    contrib = data.add(
        common.Contribution, 'case.alignment',
        id="1", name="case alignment")
    alena = data.add(
        common.Contributor, 'witzlack',
        id='witzlack', name='Alena Witzlack-Makarevich')
    DBSession.add(common.ContributionContributor(contribution=contrib, contributor=alena))

    with codecs.open(args.data_file('case.alignment.Dec.2013.csv')) as fp:
        allv = list(csv.DictReader(fp))
    for v in allv:
        for k in v:
            v[k] = v[k].decode('utf8')

    for lid, values in groupby(sorted(allv, key=lambda j: j['LID']), lambda i: i['LID']):
        vsid = '%s-%s' % (p.id, lid)
        values = list(values)

        if vsid not in data['ValueSet']:
            vs = data.add(
                common.ValueSet, vsid,
                id=vsid,
                language=data['Languoid'][lid],
                contribution=contrib,
                parameter=p)
        else:
            vs = data['ValueSet'][vsid]

        bibkeys = []
        for v in values:
            bibkeys.extend(filter(None, [v.strip() for v in v['bibtex'].split(',')]))

        for key in set(bibkeys):
            if key in data['Source']:
                source = data['Source'][key]
            else:
                if key in bib.keymap:
                    source = data.add(common.Source, key, _obj=bibtex2source(bib[key]))
                else:
                    print key
# Marchese1978Time
# Kibriketal2000Jazyk
# check Mreta1998Analysis
# Nababan1971Grammar
# Werleetal1976Phonologie

                    source = None
            if source:
                DBSession.add(common.ValueSetReference(valueset=vs, source=source))

        for i, value in enumerate(values):
            vid = '%s-%s' % (vsid, i + 1)
            v = data.add(
                common.Value, vid,
                id=vid,
                name=' '.join('%('+spec[0]+')s' for spec in varspec) % value,
                jsondata=value,
                valueset=vs)
            DBSession.flush()
            for j, spec in enumerate(varspec):
                attr, domain = spec
                domain.add(value[attr])
                DBSession.add(common.Value_data(key=attr, value=value[attr], ord=j, object_pk=v.pk))

    p.jsondata = {'varspec': [(name, list(domain)) for name, domain in varspec]}


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
