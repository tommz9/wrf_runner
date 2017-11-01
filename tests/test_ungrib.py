import pytest
import os
from wrf_runner import WrfException
from wrf_runner import namelist
from wrf_runner.ungrib import Ungrib, grib_alphabetical_extensions
from unittest.mock import MagicMock

from .test_geogrid import FakeProcess
from .test_cli import resources_directory


class TestRunMethods:

    @pytest.fixture(autouse=True)
    def mock_system_config(self, mocker):
        self.test_working_directory = "/tmp"

        mock_system_config = {
            'wps_path': self.test_working_directory
        }

        mocker.patch('wrf_runner.ungrib.system_config', mock_system_config)

    @pytest.fixture
    def valid_process_simulator(self, mocker):

        with open(os.path.join(resources_directory, 'ungrib.success.stdout.txt'), 'r') as stdout:
            lines = stdout.readlines()

        async def fake_create_subprocess(*args, **kwargs):
            return FakeProcess(lines, [], 0)

        mocker.patch(
            'wrf_runner.program.asyncio.create_subprocess_exec', fake_create_subprocess)

    @pytest.mark.asyncio
    async def test_success_run(self, valid_process_simulator, valid_config_1):

        ungrib = Ungrib(
            config=valid_config_1)
        result = await ungrib.run()

        # Success
        assert(result)


def test_grib_alphabetical_extensions():

    generator = grib_alphabetical_extensions()

    assert(next(generator) == 'AAA')
    assert(next(generator) == 'AAB')
    assert(next(generator) == 'AAC')


def test_grib_alphabetical_extensions2():

    generator = grib_alphabetical_extensions()

    extensions = list(generator)

    assert(len(extensions) == (ord('Z') - ord('A') + 1)**3)
    assert(extensions[0] == 'AAA')
    assert(extensions[-1] == 'ZZZ')
