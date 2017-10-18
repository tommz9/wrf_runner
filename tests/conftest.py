import json
import os

import pytest

from .test_cli import resources_directory


@pytest.fixture
def valid_config_1():
    return json.load(open(os.path.join(
        resources_directory, 'valid_config.json')))
