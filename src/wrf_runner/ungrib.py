# -*- coding: utf-8 -*-

import datetime

import dateparser
import jsonschema

from . import namelist_ungrib
from .wrf_exceptions import WrfException

configuration_schema = {
    "type": "object",
    "properties": {
        "start_date": {"type": "string"},
        "end_date": {"type": "string"},
        "interval": {"type": "number"},
        "prefix": {"type": "string"}
    },

    "required": ["start_date", "end_date", "interval", "prefix"]
}


def check_config(config):
    try:
        jsonschema.validate(config, configuration_schema)

        # Check if we understand the dates
        config['start_date'] = dateparser.parse(config['start_date'])
        config['end_date'] = dateparser.parse(config['end_date'])

        if not isinstance(config['start_date'], datetime.datetime):
            raise WrfException("Cannot parse the start date")

        if not isinstance(config['end_date'], datetime.datetime):
            raise WrfException("Cannot parse the end date")

    except jsonschema.ValidationError as e:
        raise WrfException("Configuration error", e)


class Ungrib:
    def __init__(self, config):
        """"""

        try:
            self.config = config['ungrib']
        except KeyError:
            self.config = config

        # Process the datetime
        if isinstance(self.config['start_date'], str):
            self.config['start_date'] = dateparser.parse(self.config['start_date'])
        if isinstance(self.config['end_date'], str):
            self.config['end_date'] = dateparser.parse(self.config['end_date'])

    def generate_namelist_dict(self):
        return namelist_ungrib.config_to_namelist(self.config)
