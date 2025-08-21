# encoding: utf-8
from doctest import ELLIPSIS
from unittest import TestCase

from doctestcase import doctestcase


case = doctestcase(options=ELLIPSIS)


@case
class UsageFirst(TestCase):
    """
    First use case

    >>> from lazycloud import __version__
    """
