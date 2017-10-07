# -*- coding: utf-8 -*-

import pytest
from wrf_runner import geogrid, WrfException
from wrf_runner.namelist_geogrid import geogrid_namelist, list_from_list_of_dict, \
    config_to_namelist

from wrf_runner.namelist import generate_config_file


@pytest.mark.parametrize("config", [{}, 5, 'nonsense'])
def test_basic_wrong_configuration(config):
    with pytest.raises(WrfException):
        geogrid.check_config(config)


valid_config_1 = {
    "domains": [{
        "parent_id": 1,
        "parent_ratio": 1,
        "parent_start": [1, 1],
        "size": [74, 61],
        "step_size": [9000, 9000]
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
    },

    {
        "domains": [{
            "parent_id": 1,
            "parent_ratio": 1,
            "parent_start": [1, 1],
            "size": [74, 61]
            # "step_size": [9000, 9000]    Step size missing
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
        "domains": [
            {
                "parent_id": 1,
                "parent_ratio": 1,
                "parent_start": [1, 1],
                "size": [74, 61],
                "step_size": [9000, 9000]
            },
            {
                "parent_id": 1,
                "parent_ratio": 1,
                "parent_start": [1, 1],
                "size": [74, 61],
                "step_size": [9000, 9000]  # Step size specified on the second domain
            }
        ],

        "projection": {
            "type": "lambert",
            "ref_location": [34.83, -81.03],
            "truelat": [30, 60],
            "stand_lot": -98
        },
        "data_path": "/datasets/GEOGDATA"
    },

    # First domain wrong parent id
    {
        "domains": [
            {
                "parent_id": 2,
                "parent_ratio": 1,
                "parent_start": [1, 1],
                "size": [74, 61],
                "step_size": [9000, 9000]
            },
            {
                "parent_id": 1,
                "parent_ratio": 1,
                "parent_start": [1, 1],
                "size": [74, 61]
            }
        ],

        "projection": {
            "type": "lambert",
            "ref_location": [34.83, -81.03],
            "truelat": [30, 60],
            "stand_lot": -98
        },
        "data_path": "/datasets/GEOGDATA"
    },

    # No domains
    {
        "domains": [],

        "projection": {
            "type": "lambert",
            "ref_location": [34.83, -81.03],
            "truelat": [30, 60],
            "stand_lot": -98
        },
        "data_path": "/datasets/GEOGDATA"
    },

    # Second domain wrong parent id
    {
        "domains": [
            {
                "parent_id": 1,
                "parent_ratio": 1,
                "parent_start": [1, 1],
                "size": [74, 61],
                "step_size": [9000, 9000]
            },
            {
                "parent_id": 2,
                "parent_ratio": 1,
                "parent_start": [1, 1],
                "size": [74, 61]
            }
        ],

        "projection": {
            "type": "lambert",
            "ref_location": [34.83, -81.03],
            "truelat": [30, 60],
            "stand_lot": -98
        },
        "data_path": "/datasets/GEOGDATA"
    },

    # Second domain wrong parent id
    {
        "domains": [
            {
                "parent_id": 1,
                "parent_ratio": 1,
                "parent_start": [1, 1],
                "size": [74, 61],
                "step_size": [9000, 9000]
            },
            {
                "parent_id": 0,
                "parent_ratio": 1,
                "parent_start": [1, 1],
                "size": [74, 61]
            }
        ],

        "projection": {
            "type": "lambert",
            "ref_location": [34.83, -81.03],
            "truelat": [30, 60],
            "stand_lot": -98
        },
        "data_path": "/datasets/GEOGDATA"
    },
]


@pytest.mark.parametrize("config", invalid_configs)
def test_basic_invalid_configuration(config):
    with pytest.raises(WrfException):
        geogrid.check_config(config)


def test_geogrid_namelist_documentation():
    """
    Checks if all of the definitions in the structure are copied correctly.

    Only check if the first word of the documentation is equal to the key.
    :return:
    """

    for _, section_config in geogrid_namelist.items():
        for option, config_tuple in section_config.items():
            first_word = config_tuple[0].split()[0]

            assert (option.lower() == first_word.lower())


def test_list_from_list_of_dict():
    test_list = [{
        "parent_id": 1,
        "parent_ratio": 1,
        "parent_start": [1],  # Only one
        "size": [74, 61]
    }, {
        "parent_id": 1,
        "parent_ratio": 3,
        "parent_start": [1],  # Only one
        "size": [100, 200]
    }]

    assert (list_from_list_of_dict(test_list, 'parent_ratio') == [1, 3])
    assert (list_from_list_of_dict(test_list, 'size', selector=lambda x: x[0]) == [74, 100])
    assert (list_from_list_of_dict(test_list, 'size', selector=lambda x: x[1]) == [61, 200])


valid_config_3_domains = {
    "domains": [
        {
            "parent_id": 1,
            "parent_ratio": 1,
            "parent_start": [30, 30],
            "size": [74, 61],
            "step_size": [9000, 9000]
        },
        {
            "parent_id": 2,
            "parent_ratio": 3,
            "parent_start": [30, 30],
            "size": [100, 120],
            "step_size": [9000, 9000]
        },
        {
            "parent_id": 3,
            "parent_ratio": 3,
            "parent_start": [50, 50],
            "size": [120, 100]
        },
    ],

    "projection": {
        "type": "lambert",
        "ref_location": [34.83, -81.03],
        "truelat": [30, 60],
        "stand_lot": -98
    },
    "data_path": "/datasets/GEOGDATA"
}


def test_config_to_namelist_basic():
    # Should not fail
    namelist = config_to_namelist(valid_config_3_domains)

    # Should be accepted by the file generator without any exception
    generate_config_file(namelist)
