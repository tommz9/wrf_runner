# -*- coding: utf-8 -*-

import asyncio
import datetime
import os
from types import SimpleNamespace
from typing import Callable

import dateparser
import jsonschema

from . import namelist_ungrib
from .namelist import generate_config_file
from .wrf_exceptions import WrfException
from .wrf_runner import system_config
from .program import Program
from .wps_state_machine import WpsStateMachine

configuration_schema = {
    "type": "object",
    "properties": {
        "start_date": {"type": "string"},
        "end_date": {"type": "string"},
        "interval": {"type": "number"},
        "prefix": {"type": "string"}
    },

    "required": ["start_date", "end_date", "interval", "prefix"]
}


def check_config(config):
    try:
        jsonschema.validate(config, configuration_schema)

        # Check if we understand the dates
        config['start_date'] = dateparser.parse(config['start_date'])
        config['end_date'] = dateparser.parse(config['end_date'])

        if not isinstance(config['start_date'], datetime.datetime):
            raise WrfException("Cannot parse the start date")

        if not isinstance(config['end_date'], datetime.datetime):
            raise WrfException("Cannot parse the end date")

    except jsonschema.ValidationError as e:
        raise WrfException("Configuration error", e)


def check_progress_update(line: str):
    if 'Inventory for date' in line:
        return 1, 10
    
    return None

class Ungrib:
    def __init__(self,
                 config,
                 progress_update_cb: Callable[[int, int], None] = None,
                 print_message_cb: Callable[[str], None] = None,
                 log_file=None):
        """"""

        try:
            self.config = config['ungrib']
        except KeyError:
            self.config = config

        # Process the datetime
        if isinstance(self.config['start_date'], str):
            self.config['start_date'] = dateparser.parse(
                self.config['start_date'])
        if isinstance(self.config['end_date'], str):
            self.config['end_date'] = dateparser.parse(self.config['end_date'])

        files_count = 10 # TODO

        self.state_machine = WpsStateMachine(
            files_count,
            check_progress_update,
            lambda line: 'Successful completion of ungrib.' in line,
            lambda line: 'ERROR' in line,
            progress_update_cb
        )

        self.program = Program(
            './ungrib.exe',
            self.state_machine.process_line,
            self.state_machine.process_line,
            log_file=log_file
        )

        self.print_message_cb = print_message_cb

    def generate_namelist_dict(self):
        return namelist_ungrib.config_to_namelist(self.config)

    def print_message(self, message):
        if self.print_message_cb:
            self.print_message_cb(message)

    async def run(self):
        # cd to the WPS folder
        os.chdir(system_config['wps_path'])

        self.print_message('Processing the configuration file...')

        # Generate the config file and save it
        config_file_content = generate_config_file(
            self.generate_namelist_dict())

        # Generate the namelist
        with open('namelist.wps', 'w') as namelist_file:
            namelist_file.write(config_file_content)

        self.state_machine.reset()

        # Wait for the program to end
        return_code = await self.program.run()

        # Evaluate the result
        return self.state_machine.state == 'done' and return_code == 0
