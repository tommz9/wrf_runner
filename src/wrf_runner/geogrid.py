# -*- coding: utf-8 -*-

"""
Code to represent and manipulate the GEOGRID program.
"""

import jsonschema

from . import namelist_geogrid
from .wrf_exceptions import WrfException

two_numbers = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}

configuration_schema = {
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
                    "parent_start": two_numbers,
                    "size": two_numbers,
                    "step_size": two_numbers
                },
                "required": ["parent_id", "parent_ratio", "parent_start", "size"]
            }},
        "projection": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "ref_location": two_numbers,
                "truelat": two_numbers,
                "stand_lot": {"type": "number"}
            },
            "required": ["type", "ref_location", "truelat", "stand_lot"]
        },
        "data_path": {"type": "string"}
    },
    "required": ["domains", "projection", "data_path"]
}


def check_config(config):
    """
    Checks if the config file has all that we need to generate the input file for geogrid
    :param config: a dictionary with the configuration
    :return: nothing if the config is OK, raises WrfException on error
    """
    try:
        jsonschema.validate(config, configuration_schema)

        # Check if it has stepsize in the first domain but not the others
        if 'step_size' not in config['domains'][0]:
            raise WrfException("Step size not specified in the first domain")

        if any(['step_size' in domain for domain in config['domains'][1:]]):
            raise WrfException("Step size can be specified only on the first domain")

        # Check first domain id
        if config['domains'][0]['parent_id'] != 1:
            raise WrfException('First domain parent id has to be 1.')

        # Check other domains ids
        for i, domain in enumerate(config['domains'][1:]):
            if domain['parent_id'] > i:
                raise WrfException('Invalid parent_id (too large)')
            if domain['parent_id'] < 1:
                raise WrfException('Invalid parent_id. Has to be bigger than 1.')

    except jsonschema.ValidationError as e:
        raise WrfException("Configuration error", e)


class Geogrid:
    def __init__(self, config=None):
        """"""
        try:
            self.config = config['geogrid']
        except KeyError:
            self.config = config

    def set_config(self, config):
        check_config(config)
        self.config = config

    def generate_namelist_dict(self):
        """
        Uses the config file to generate the namelist for GEOGRID
        :return: dictionary with the configuration for the namelist. Can be passed to the Namelist class to merge it
        with the configuration for the other programs
        """

        return namelist_geogrid.config_to_namelist(self.config)
