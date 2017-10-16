import pytest
import os
from wrf_runner import WrfException
from wrf_runner import namelist
from wrf_runner.ungrib import check_config, Ungrib
from unittest.mock import MagicMock

from .test_geogrid import FakeProcess
from .test_cli import resources_directory


@pytest.mark.parametrize("invalid_config", [{}, '', 45])
def test_check_config_fails_simple(invalid_config):
    with pytest.raises(WrfException):
        check_config(invalid_config)


invalid_samples = [
    {
        # 'start_date': '2017-09-10',
        'end_date': '2017-09-11',
        'interval': 3600,
        'prefix': 'FILE'
    },
    {
        'start_date': '2017-09-10',
        # 'end_date': '2017-09-11',
        'interval': 3600,
        'prefix': 'FILE'
    },
    {
        'start_date': '',
        'end_date': '2017-09-11',
        'interval': 3600,
        'prefix': 'FILE'
    },
    {
        'start_date': '2017-09-10',
        'end_date': 'what?',
        'interval': 3600,
        'prefix': 'FILE'
    }
]


@pytest.mark.parametrize("invalid_config", invalid_samples)
def test_check_config_fails(invalid_config):
    with pytest.raises(WrfException):
        check_config(invalid_config)


valid_samples = [
    {
        'start_date': '2017-09-10',
        'end_date': '2017-09-11',
        'interval': 3600,
        'prefix': 'FILE'
    }
]


@pytest.mark.parametrize("valid_config", valid_samples)
def test_check_valid_config(valid_config):
    check_config(valid_config)


@pytest.mark.parametrize("valid_config", valid_samples)
def test_accepted_by_namelist_generator(valid_config):
    ungrib = Ungrib(valid_config)
    X = ungrib.generate_namelist_dict()
    config_file = namelist.generate_config_file(X)
    print(config_file)


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
    async def test_success_run(self, valid_process_simulator):

        progress_update_mock = MagicMock()

        ungrib = Ungrib(
            config=valid_samples[0], progress_update_cb=progress_update_mock)
        result = await ungrib.run()

        # Success
        assert(result == True)

        # The progress has been updated 25 times
        assert(progress_update_mock.call_count == 25)
