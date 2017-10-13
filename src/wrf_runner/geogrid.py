# -*- coding: utf-8 -*-

"""
Code to represent and manipulate the GEOGRID program.
"""

import re
from enum import Enum
from typing import Callable
import jsonschema
import os

from . import namelist_geogrid
from .namelist import generate_config_file
from .wrf_exceptions import WrfException
from .wrf_runner import system_config
from .program import Program

two_numbers = {"type": "array", "items": {
    "type": "number"}, "minItems": 2, "maxItems": 2}

configuration_schema = {
    "type": "object",
    "properties": {
        "domains": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "parent_id": {"type": "number"},
                    "parent_ratio": {"type": "number"},
                    "parent_start": two_numbers,
                    "size": two_numbers,
                    "step_size": two_numbers
                },
                "required": ["parent_id", "parent_ratio", "parent_start", "size"]
            }},
        "projection": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "ref_location": two_numbers,
                "truelat": two_numbers,
                "stand_lot": {"type": "number"}
            },
            "required": ["type", "ref_location", "truelat", "stand_lot"]
        },
        "data_path": {"type": "string"}
    },
    "required": ["domains", "projection", "data_path"]
}


def check_config(config):
    """
    Checks if the config file has all that we need to generate the input file for geogrid
    :param config: a dictionary with the configuration
    :return: nothing if the config is OK, raises WrfException on error
    """
    try:
        jsonschema.validate(config, configuration_schema)

        # Check if it has stepsize in the first domain but not the others
        if 'step_size' not in config['domains'][0]:
            raise WrfException("Step size not specified in the first domain")

        if any(['step_size' in domain for domain in config['domains'][1:]]):
            raise WrfException(
                "Step size can be specified only on the first domain")

        # Check first domain id
        if config['domains'][0]['parent_id'] != 1:
            raise WrfException('First domain parent id has to be 1.')

        # Check other domains ids
        for i, domain in enumerate(config['domains'][1:]):
            if domain['parent_id'] > i:
                raise WrfException('Invalid parent_id (too large)')
            if domain['parent_id'] < 1:
                raise WrfException(
                    'Invalid parent_id. Has to be bigger than 1.')

    except jsonschema.ValidationError as e:
        raise WrfException("Configuration error", e)


class RunState(Enum):
    """
    States to track the progression of the GEOGRID program
    """
    Idle = 1
    Initialization = 2
    DomainProcessing = 3
    Done = 4


def check_progress_update(line: str):
    """
    Scans one line of the output of GEOGRID to check if the program started working on a new domain.
    :param line: one line of GEOGRID stdout
    :return: tuple (current_domain, domain_count) if the status changed, None otherwise
    """
    result = re.search(r"Processing domain (\d+) of (\d+)", line)

    if result:
        return int(result.group(1)), int(result.group(2))

    return None


class Geogrid():
    def __init__(self,
                 config=None,
                 progress_update_cb: Callable[[int, int], None] = None,
                 print_message_cb: Callable[[str], None] = None,
                 log_file=None):
        """

        :param config: a dict with the configuration
        :param progress_update_cb: Callback that will get called everytime a domain processing
        is finished.
        :param print_message_cb: will be called for printing messages
        """

        self.program = Program(
            './geogrid.exe',
            self.stdout_callback,
            self.stderr_callback,
            log_file=log_file)

        try:
            self.config = config['geogrid']
        except KeyError:
            self.config = config

        self.error_run = True
        self.run_state = RunState.Idle
        self.current_domain = 0
        self.domains_count = len(self.config['domains'])

        self.progress_update_cb = progress_update_cb
        self.print_message_cb = print_message_cb

    def set_config(self, config):
        check_config(config)
        self.config = config

    def generate_namelist_dict(self):
        """
        Uses the config file to generate the namelist for GEOGRID
        :return: dictionary with the configuration for the namelist. Can be passed to the Namelist class to merge it
        with the configuration for the other programs
        """

        return namelist_geogrid.config_to_namelist(self.config)

    def stderr_callback(self, line: str):
        if 'ERROR' in line:
            self.error_run = True

    def update_progress(self):
        if self.run_state is RunState.DomainProcessing:
            if self.progress_update_cb:
                self.progress_update_cb(
                    self.current_domain - 1, self.domains_count)
        elif self.run_state is RunState.Done:
            if self.progress_update_cb:
                self.progress_update_cb(self.domains_count, self.domains_count)

    def print_message(self, message):
        if self.print_message_cb:
            self.print_message_cb(message)

    def stdout_callback(self, line: str):
        if 'ERROR' in line:
            self.error_run = True

        if self.run_state is RunState.Initialization:
            progress_update = check_progress_update(line)
            if progress_update:
                assert (self.domains_count == progress_update[1])
                self.current_domain, self.domains_count = progress_update
                self.run_state = RunState.DomainProcessing
                self.print_message('Processing domains...')
                self.update_progress()

        elif self.run_state is RunState.DomainProcessing:
            progress_update = check_progress_update(line)
            if progress_update:
                assert (self.domains_count == progress_update[1])
                self.current_domain, self.domains_count = progress_update
                self.update_progress()

            if "Successful completion of geogrid." in line:
                self.run_state = RunState.Done
                self.error_run = False
                self.update_progress()

    async def run(self):

        os.chdir(system_config['wps_path'])

        self.print_message('Processing the configuration file...')

        # Generate the config file and save it
        config_file_content = generate_config_file(
            self.generate_namelist_dict())

        # Generate the namelist
        with open('namelist.wps', 'w') as namelist_file:
            namelist_file.write(config_file_content)

        self.run_state = RunState.Initialization
        self.print_message('Initializing...')

        return_code = await self.program.run()

        return (self.error_run is not True) and return_code == 0
