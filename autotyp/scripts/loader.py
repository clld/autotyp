from __future__ import unicode_literals
import sys
import codecs
from itertools import groupby
from getpass import getuser
from collections import OrderedDict

from unicsv import UnicodeCSVDictReader
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


def param_and_contrib(data, name, id, num):
    kw = dict(id=str(num), name=name)
    return (
        data.add(common.Parameter, id, **kw),
        data.add(common.Contribution, id, **kw))


def inclusive_excusive(args, data, bib):
    """
    Incl	Inclusive/exclusive distinction. 1 = present, 0 = absent.
    Belh	Belhare-type inclusive/exclusive distinction. 1 = present, 0 = absent. NA = no information available.
    MinAug	Minimal/augmented system. 1 = present, 0 = absent. 1? = probably present
    """
    value_map = {
        '0': 'absent',
        '1': 'present',
        '1?': 'probably present',
        'NA': 'no information available'}
    name_map = OrderedDict()
    name_map['Incl'] = 'Inclusive/exclusive distinction'
    name_map['Belh'] = 'Belhare-type inclusive/exclusive distinction'
    name_map['MinAug'] = 'Minimal/augmented system'
    varspec = [(name, set()) for name in name_map.values()]
    rev_name_map = dict(zip(name_map.values(), name_map.keys()))

    p, contrib = param_and_contrib(
        data, 'inclusive/exclusive distinction', 'inclusive.exclusive', 2)

    DBSession.add(common.ContributionContributor(
        contribution=contrib, contributor=data['Contributor']['bickel']))
    DBSession.add(common.ContributionContributor(
        contribution=contrib, contributor=data['Contributor']['nichols']))

    allv = rows(
        args.data_file('InclExcl_ISO_bib_stripped.txt'), namedtuples=True, encoding='utf8', newline='\r')

    for lid, values in groupby(sorted(allv, key=lambda j: j.LID), lambda i: i.LID):
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
            bibkeys.extend(filter(None, [v.strip() for v in v.bibkey.split(',')]))

        for key in set(bibkeys):
            if key in data['Source']:
                source = data['Source'][key]
            else:
                if key in bib.keymap:
                    source = data.add(common.Source, key, _obj=bibtex2source(bib[key]))
                else:
                    print key

                    source = None
            if source:
                DBSession.add(common.ValueSetReference(valueset=vs, source=source))

        for i, value in enumerate(values):
            if i > 0:
                print 'multiuple values!'
                raise ValueError
            value_data = OrderedDict()
            for var in name_map.keys():
                val = value_map.get(getattr(value, var))
                if not val:
                    print getattr(value, var)
                    raise ValueError
                value_data[var] = val
            v = data.add(
                common.Value, vsid,
                id=vsid,
                name=' / '.join(value_data.values()),
                #jsondata=value,
                valueset=vs)
            DBSession.flush()
            for j, spec in enumerate(varspec):
                attr, domain = spec
                domain.add(value_data[rev_name_map[attr]])
                DBSession.add(common.Value_data(key=attr, value=value_data[rev_name_map[attr]], ord=j, object_pk=v.pk))

    p.jsondata = {'varspec': [(name, list(domain)) for name, domain in varspec]}


def case_alignment(args, data, bib):
    varspec = [
        ('alignment', set()),
        ('referential_type', set()),
        ('tense_aspect', set()),
        ('morphological_form.PoS', set()),
        ('A.marked', set()),
        ('P.marked', set())]
    p, contrib = param_and_contrib(
        data, 'case alignment', 'case.alignment', 1)
    alena = data.add(
        common.Contributor, 'witzlack',
        id='witzlack', name='Alena Witzlack-Makarevich')
    DBSession.add(common.ContributionContributor(contribution=contrib, contributor=alena))

    with open(args.data_file('case.alignment.Dec.2013.csv')) as fp:
        allv = list(UnicodeCSVDictReader(fp))

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
