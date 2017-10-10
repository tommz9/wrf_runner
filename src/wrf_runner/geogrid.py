# -*- coding: utf-8 -*-

"""
Code to represent and manipulate the GEOGRID program.
"""

import asyncio
import os
import re
from enum import Enum

import jsonschema

from . import namelist_geogrid
from .namelist import generate_config_file
from .wrf_exceptions import WrfException
from .wrf_runner import system_config

two_numbers = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}

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
            raise WrfException("Step size can be specified only on the first domain")

        # Check first domain id
        if config['domains'][0]['parent_id'] != 1:
            raise WrfException('First domain parent id has to be 1.')

        # Check other domains ids
        for i, domain in enumerate(config['domains'][1:]):
            if domain['parent_id'] > i:
                raise WrfException('Invalid parent_id (too large)')
            if domain['parent_id'] < 1:
                raise WrfException('Invalid parent_id. Has to be bigger than 1.')

    except jsonschema.ValidationError as e:
        raise WrfException("Configuration error", e)


class RunState(Enum):
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


class Geogrid:
    def __init__(self, config=None, environment_config=None, progress_update_cb=None, print_message_cb=None):
        """"""
        try:
            self.config = config['geogrid']
        except KeyError:
            self.config = config

        if environment_config is None:
            self.environment_config = system_config

        self.stderr = []
        self.stdout = []

        self.error_run = False
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
        line.strip()
        self.stderr.append(line)
        if 'ERROR' in line:
            self.error_run = True
            # print('Geogrid stderr:', line)

    def update_progress(self):
        if self.run_state is RunState.DomainProcessing:
            if self.progress_update_cb:
                self.progress_update_cb(self.current_domain - 1, self.domains_count)
        elif self.run_state is RunState.Done:
            if self.progress_update_cb:
                self.progress_update_cb(self.domains_count, self.domains_count)

    def print_message(self, message):
        if self.print_message_cb:
            self.print_message_cb(message)

    def stdout_callback(self, line: str):
        line = line.strip()
        self.stdout.append(line)
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
                self.update_progress()

    async def run(self):
        # cd to the WPS folder
        os.chdir(self.environment_config['wps_path'])

        self.print_message('Processing the configuration file...')

        # Generate the config file and save it
        config_file_content = generate_config_file(self.generate_namelist_dict())

        # Generate the namelist
        with open('namelist.wps', 'w') as f:
            f.write(config_file_content)

        async def stream_reader(stream, cb):
            while True:
                line = await stream.readline()
                if len(line):
                    cb(line.decode('ASCII'))
                else:
                    return

        self.run_state = RunState.Initialization

        self.print_message('Initializing...')
        # Run the program
        process = await asyncio.create_subprocess_exec('./geogrid.exe', stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)

        # Setup the line callbacks
        await stream_reader(process.stdout, self.stdout_callback)
        await stream_reader(process.stderr, self.stderr_callback)

        # Wait for the program to end
        return_code = await process.wait()

        # Evaluate the result
        return not (return_code != 0 or self.error_run)
