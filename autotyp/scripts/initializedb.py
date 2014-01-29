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
from autotyp.scripts import loader


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
        contributor = data.add(common.Contributor, spec[0], id=spec[0], name=spec[1])
        DBSession.add(common.Editor(
            dataset=dataset, ord=i + 1, contributor=contributor))

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

    loader.case_alignment(args, data, bib)
    loader.inclusive_excusive(args, data, bib)


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
