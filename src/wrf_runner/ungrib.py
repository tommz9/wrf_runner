# -*- coding: utf-8 -*-

import asyncio
import datetime
import os
from types import SimpleNamespace
from typing import Callable

import dateparser
import jsonschema

from .namelist import generate_config_file
from .wrf_exceptions import WrfException
from .wrf_runner import system_config
from .program import Program
from .wps_state_machine import WpsStateMachine
from .configuration import WpsConfiguration


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

        if isinstance(config, WpsConfiguration):
            self.config = config
        else:
            self.config = WpsConfiguration(config)

        files_count = 10  # TODO

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

    def print_message(self, message):
        if self.print_message_cb:
            self.print_message_cb(message)

    async def run(self):
        # cd to the WPS folder
        os.chdir(system_config['wps_path'])

        self.print_message('Processing the configuration file...')

        # Generate the config file and save it
        config_file_content = self.config.get_namelist()

        # Generate the namelist
        with open('namelist.wps', 'w') as namelist_file:
            namelist_file.write(config_file_content)

        self.state_machine.reset()

        # Wait for the program to end
        return_code = await self.program.run()

        # Evaluate the result
        return self.state_machine.state == 'done' and return_code == 0
