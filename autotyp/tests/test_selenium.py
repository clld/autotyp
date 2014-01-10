from clld.tests.util import TestWithSelenium

import autotyp


class Tests(TestWithSelenium):
    app = autotyp.main({}, **{'sqlalchemy.url': 'postgres://robert@/autotyp'})
