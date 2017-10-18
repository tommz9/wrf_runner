
import asyncio
import os

import pytest

from unittest.mock import MagicMock

from wrf_runner.metgrid import Metgrid

from .test_geogrid import FakeProcess
from .test_cli import resources_directory


class TestRunMethods:

    @pytest.fixture(autouse=True)
    def mock_system_config(self, mocker):
        self.test_working_directory = "/tmp"

        mock_system_config = {
            'wps_path': self.test_working_directory
        }

        mocker.patch('wrf_runner.metgrid.system_config', mock_system_config)

    @pytest.fixture
    def valid_process_simulator(self, mocker):

        with open(os.path.join(resources_directory, 'metgrid.success.stdout.txt'), 'r') as stdout:
            lines = stdout.readlines()

        async def fake_create_subprocess(*args, **kwargs):
            return FakeProcess(lines, [], 0)

        mocker.patch(
            'wrf_runner.program.asyncio.create_subprocess_exec', fake_create_subprocess)

    @pytest.mark.asyncio
    async def test_success_run(self, valid_process_simulator, valid_config_1):

        progress_update_mock = MagicMock()

        ungrib = Metgrid(
            config=valid_config_1, progress_update_cb=progress_update_mock)
        result = await ungrib.run()

        # Success
        assert(result)

        assert(progress_update_mock.call_count == 4)
