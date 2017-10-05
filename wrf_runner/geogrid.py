# -*- coding: utf-8 -*-

"""
Code to represent and manipulate the GEOGRID program.
"""

import jsonschema
from .wrf_exceptions import WrfException

two_numbers = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}

configuration_schema = {
    "type": "object",
    "properties": {
        "domains": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "number"},
                    "parent_id": {"type": "number"},
                    "parent_ratio": {"type": "number"},
                    "parent_start": two_numbers,
                    "size": two_numbers
                },
                "required": ["id", "parent_id", "parent_ratio", "parent_start", "size"]
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
    try:
        jsonschema.validate(config, configuration_schema)

    except jsonschema.ValidationError as e:
        raise WrfException("Configuration error", e)
