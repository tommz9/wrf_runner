# -*- coding: utf-8 -*-

"""Main module."""

import jsonschema

from . import geogrid
from .wrf_exceptions import WrfException

configuration_schema = {
    "type": "object",
    "properties": {
        "geogrib": {"type": "object"},
        "ungrib": {"type": "object"},
        "metgrib": {"type": "object"},
        "real": {"type": "object"},
        "wrf": {"type": "object"}
    },
    "required": ["geogrib", "ungrib", "metgrib", "real", "wrf"]
}

def check_configuration(config):
    try:
        jsonschema.validate(config, configuration_schema)
        geogrid.check_config(config['geogrid'])

    except jsonschema.ValidationError as e:
        raise WrfException("Configuration error", e)
