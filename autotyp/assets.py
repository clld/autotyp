from clld.web.assets import environment
from path import path

import autotyp


environment.append_path(
    path(autotyp.__file__).dirname().joinpath('static'), url='/autotyp:static/')
environment.load_path = list(reversed(environment.load_path))
