# -*- coding: utf-8 -*-

import pytest

from wrf_runner import geogrid, WrfException


@pytest.mark.parametrize("config", [{}, 5, 'nonsense'])
def test_basic_wrong_configuration(config):
    with pytest.raises(WrfException):
        geogrid.check_config(config)


valid_config_1 = {
    "domains": [{
        "id": 1,
        "parent_id": 1,
        "parent_ratio": 1,
        "parent_start": [1, 1],
        "size": [74, 61]
    }],

    "projection": {
        "type": "lambert",
        "ref_location": [34.83, -81.03],
        "truelat": [30, 60],
        "stand_lot": -98
    },
    "data_path": "/datasets/GEOGDATA"
}


@pytest.mark.parametrize("config", [valid_config_1])
def test_valid_configuration(config):
    geogrid.check_config(config)


invalid_configs = [
    {
        "domains": [{
            "id": 1,
            "parent_ratio": 1,
            "parent_start": [1, 1],
            "size": ["WRONG", 61]
        }],

        "projection": {
            "type": "lambert",
            "ref_location": [34.83, -81.03],
            "truelat": [30, 60],
            "stand_lot": -98
        },
        "data_path": "/datasets/GEOGDATA"
    },

    {
        "domains": [{
            "id": 1,
            # "parent_id": 1, MISSSING!
            "parent_ratio": 1,
            "parent_start": [1, 1],
            "size": [74, 61]
        }],

        "projection": {
            "type": "lambert",
            "ref_location": [34.83, -81.03],
            "truelat": [30, 60],
            "stand_lot": -98
        },
        "data_path": "/datasets/GEOGDATA"
    },

    {
        "domains": [{
            "id": 1,
            "parent_id": 1,
            "parent_ratio": 1,
            "parent_start": [1],  # Only one
            "size": [74, 61]
        }],

        "projection": {
            "type": "lambert",
            "ref_location": [34.83, -81.03],
            "truelat": [30, 60],
            "stand_lot": -98
        },
        "data_path": "/datasets/GEOGDATA"
    }
]


@pytest.mark.parametrize("config", invalid_configs)
def test_basic_invalid_configuration(config):
    with pytest.raises(WrfException):
        geogrid.check_config(config)
