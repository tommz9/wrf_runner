# -*- coding: utf-8 -*-

import json
import os

import pytest

from wrf_runner import WrfException
from wrf_runner.configuration import WpsConfiguration

from .test_cli import resources_directory


@pytest.mark.parametrize("config", [{}, 5, 'nonsense'])
def test_basic_wrong_configuration(config):
    with pytest.raises(WrfException):
        WpsConfiguration(config)


def test_valid_configuration(valid_config_1):
    WpsConfiguration(valid_config_1)


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
    assert (list_from_list_of_dict(test_list, 'size',
                                   selector=lambda x: x[0]) == [74, 100])
    assert (list_from_list_of_dict(test_list, 'size',
                                   selector=lambda x: x[1]) == [61, 200])
