# -*- coding: utf-8 -*-

import pytest
import asyncio
import os
from wrf_runner import geogrid, WrfException

from wrf_runner.namelist import generate_config_file
from .test_cli import resources_directory


def test_config_to_namelist_basic(valid_config_1):
    # Should not fail
    geogrid.Geogrid(valid_config_1)


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
    async def test_run_changes_cwd(self, mocker, valid_config_1):

        mocked_chdir = mocker.patch('os.chdir')

        geo = geogrid.Geogrid(config=valid_config_1)

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
    async def test_run(self, mocker, process_simulator, valid_config_1):

        # The process_simulator fixture creates and mocks the create_subprocess_exec call
        # It prepares the mock with a fake output and provides the expected_result in the
        # process_simulator parameter

        # process_simulator is the expected result
        geo = geogrid.Geogrid(config=valid_config_1)
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
