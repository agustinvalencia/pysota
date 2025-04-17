# Import all the classes from the core module
# to expose them in the package level.
# make ruff lint ignore this file

# The order of imports is important here.
# The Provider class depends on the IQuery and Publication classes.
# The ResultPage class depends on the IQuery and Publication classes.
# That is why the dependencies are imported first.

# ruff: noqa
from .query import IQuery
from .publication import Publication
from .result_page import ResultPage
from .provider import Provider

__all__ = ['Provider', 'ResultPage', 'Publication', 'IQuery']
