# -*- coding: utf-8 -*-

import pytest
import asyncio
import os
from wrf_runner import geogrid, WrfException
from wrf_runner.namelist_geogrid import geogrid_namelist, list_from_list_of_dict, \
    config_to_namelist

from wrf_runner.namelist import generate_config_file
from .test_cli import resources_directory


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
                # Step size specified on the second domain
                "step_size": [9000, 9000]
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
    assert (list_from_list_of_dict(test_list, 'size',
                                   selector=lambda x: x[0]) == [74, 100])
    assert (list_from_list_of_dict(test_list, 'size',
                                   selector=lambda x: x[1]) == [61, 200])


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


success_stdout_from_file = open(os.path.join(
    resources_directory, 'geogrid.success.stdout.txt'), 'r').readlines()


class TestRunMethods:

    @pytest.fixture(autouse=True)
    def mock_system_config(self, mocker):
        self.test_working_directory = "/tmp"
        mock_system_config = {
            'wps_path': self.test_working_directory
        }

        mocker.patch('wrf_runner.geogrid.system_config', mock_system_config)

    @pytest.mark.asyncio
    async def test_run_changes_cwd(self, mocker):

        mocked_chdir = mocker.patch('os.chdir')

        geo = geogrid.Geogrid(config=valid_config_3_domains)

        try:
            result = await geo.run()
        except FileNotFoundError:  # We probably don't have the executable
            pass

        mocked_chdir.assert_called_with(self.test_working_directory)

    # the param is a list of tuples (Expected result, list of stdout lines)
    @pytest.fixture(params=[
        (False, ['', 'some ERROR happened', '']),
        (False, ['Messages', 'something happened',
                 'Processing domain 1 of 3', 'there is not final message']),
        (True, ['Messages', 'something happened', 'Processing domain 1 of 3',
                'Something else', '*   Successful completion of geogrid.   *']),
        (True, success_stdout_from_file)])
    def process_simulator(self, request, mocker):
        async def fake_create_subprocess(*args, **kwargs):
            return FakeProcess(request.param[1], [], 0)

        mocker.patch(
            'wrf_runner.program.asyncio.create_subprocess_exec', fake_create_subprocess)

        return request.param[0]

    @pytest.mark.asyncio
    async def test_run(self, mocker, process_simulator):

        # The process_simulator fixture creates and mocks the create_subprocess_exec call
        # It prepares the mock with a fake output and provides the expected_result in the
        # process_simulator parameter

        # process_simulator is the expected result
        geo = geogrid.Geogrid(config=valid_config_3_domains)
        result = await geo.run()
        assert(result == process_simulator)


class FakeStreamReader:
    def __init__(self, lines):
        self.lines = lines
        self.counter = 0

    @asyncio.coroutine
    async def readline(self):
        if self.counter < len(self.lines):
            line = self.lines[self.counter]

            if(len(line) == 0 or line[-1] != '\n'):
                line += '\n'

            self.counter += 1
            return line.encode('ASCII')
        else:
            return ''.encode('ASCII')


class FakeProcess:
    def __init__(self, stdout_lines, stderr_lines, return_code):
        self.stdout = FakeStreamReader(stdout_lines)
        self.stderr = FakeStreamReader(stderr_lines)
        self.return_code = return_code

    async def wait(self):
        return self.return_code
