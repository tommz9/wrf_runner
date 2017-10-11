# -*- coding: utf-8 -*-

import os
from shutil import copy

import wrf_runner.cli as cli
from click.testing import CliRunner

resources_directory = os.path.join(os.path.dirname(__file__), 'resources')


def test_generate_namelist_wps_nonexisting_file():
    runner = CliRunner()
    result = runner.invoke(cli.wps_namelist, ['nonexisting'])
    assert (result.exit_code != 0)


def test_generate_namelist_wps_missing_parameter():
    runner = CliRunner()
    result = runner.invoke(cli.wps_namelist, [])
    assert (result.exit_code != 0)


def test_generate_namelist_wps():
    # Get the config file
    config_fn = os.path.join(resources_directory, 'valid_config.json')

    runner = CliRunner()

    with runner.isolated_filesystem():
        copy(config_fn, '.')
        result = runner.invoke(cli.wps_namelist, ['valid_config.json'])
        assert (result.exit_code == 0)
