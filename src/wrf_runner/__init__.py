# -*- coding: utf-8 -*-

"""Top-level package for WRF Runner."""

__author__ = """Tomas Barton"""
__email__ = 'tomas@tomasbarton.net'
__version__ = '0.1.0'

import logging

logging.getLogger(__name__).setLevel('INFO')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - (%(name)s)[%(levelname)s]: %(message)s', '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)

logging.getLogger(__name__).addHandler(ch)

from .wrf_exceptions import WrfException
