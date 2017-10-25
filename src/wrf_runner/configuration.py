# -*- coding: utf-8 -*-
"""Represents the configuration of WRF."""

import datetime
import json

import jsonschema
import dateparser

from .wrf_exceptions import WrfException
from . import namelist_wps
from . import namelist


TWO_NUMBERS = {"type": "array", "items": {
    "type": "number"}, "minItems": 2, "maxItems": 2}

WPS_CONFIGURATION_SCHEMA = {
    "type": "object",
    "properties": {
        "domains": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "parent_id": {"type": "number"},
                    "parent_ratio": {"type": "number"},
                    "parent_start": TWO_NUMBERS,
                    "size": TWO_NUMBERS,
                    "step_size": TWO_NUMBERS
                },
                "required": [
                    "parent_id", "parent_ratio", "parent_start", "size"]
            }},
        "projection": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "ref_location": TWO_NUMBERS,
                "truelat": TWO_NUMBERS,
                "stand_lot": {"type": "number"}
            },
            "required": ["type", "ref_location", "truelat", "stand_lot"]
        },
        "data_path": {"type": "string"},

        "start_date": {"type": "string"},
        "end_date": {"type": "string"},
        "interval": {"type": "number"},
        "prefix": {"type": "string"}
    },
    "required": ["domains", "projection", "data_path", "start_date",
                 "end_date", "interval", "prefix"]
}


def configuration_dict_from_json(path):
    with open(path, 'r') as f:
        config = json.load(f)
    return config


class WpsConfiguration:
    """Represents the WPS Configuration.

    Can validate the config and convert it into the namelist.
    """

    def __init__(self, config_dict):
        """Initialize the object from a configuration dictionary.

        The dictioraty is validated against schema in WPS_CONFIGURATION_SCHEMA and agains WPS
        configuration requirements.
        """
        self.config_dict = config_dict

        self.validate()

    def validate_geogrid_part(self):
        """Validate the geogrid section of the config."""
        # Check if it has stepsize in the first domain but not the others
        if 'step_size' not in self.config_dict['domains'][0]:
            raise WrfException(
                "Step size not specified in the first domain")

        if any(['step_size' in domain for domain in self.config_dict['domains'][1:]]):
            raise WrfException(
                "Step size can be specified only on the first domain")

        # Check first domain id
        if self.config_dict['domains'][0]['parent_id'] != 1:
            raise WrfException('First domain parent id has to be 1.')

        # Check other domains ids
        for i, domain in enumerate(self.config_dict['domains'][1:]):
            if domain['parent_id'] > i + 1:
                raise WrfException('Invalid parent_id (too large)')
            if domain['parent_id'] < 1:
                raise WrfException(
                    'Invalid parent_id. Has to be bigger than 1.')

    def validate_ungrib_part(self):
        """Validate the ungrib section of the config."""
        # Check if we understand the dates
        self.config_dict['start_date'] = dateparser.parse(
            self.config_dict['start_date'])
        self.config_dict['end_date'] = dateparser.parse(
            self.config_dict['end_date'])

        if not isinstance(self.config_dict['start_date'], datetime.datetime):
            raise WrfException("Cannot parse the start date")

        if not isinstance(self.config_dict['end_date'], datetime.datetime):
            raise WrfException("Cannot parse the end date")

    def validate(self):
        """Validate the configuration.

        Raises an exception if the config is invalid or incomplete.
        """
        try:
            jsonschema.validate(self.config_dict, WPS_CONFIGURATION_SCHEMA)
        except jsonschema.ValidationError as exception:
            raise WrfException("Configuration error", exception)

        self.validate_geogrid_part()
        self.validate_ungrib_part()

    def get_namelist(self):
        """Generate the namelist.wps and return it as a string."""
        namelist_dict = namelist_wps.config_to_namelist(self.config_dict)
        return namelist.generate_config_file(namelist_dict)

    def __getitem__(self, key):
        return self.config_dict[key]
