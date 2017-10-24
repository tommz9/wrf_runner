# -*- coding: utf-8 -*-

"""
Code to represent and manipulate the GEOGRID program.
"""

import re
from typing import Callable
import os

from .wrf_runner import system_config
from .program import Program
from .wps_state_machine import WpsStateMachine
from .configuration import WpsConfiguration


def check_progress_update(line: str):
    """
    Scan one line of the output of GEOGRID to check if the program started working on a new domain.

    :param line: one line of GEOGRID stdout
    :return: tuple (current_domain, domain_count) if the status changed, None otherwise
    """
    result = re.search(r"Processing domain (\d+) of (\d+)", line)

    if result:
        return int(result.group(1)), int(result.group(2))

    return None


class Geogrid():
    def __init__(self,
                 config,
                 progress_update_cb: Callable[[int, int], None] = None,
                 print_message_cb: Callable[[str], None] = None,
                 log_file=None):
        """

        :param config: WpsConfiguration class
        :param progress_update_cb: Callback that will get called everytime a domain processing
        is finished.
        :param print_message_cb: will be called for printing messages
        """

        if isinstance(config, WpsConfiguration):
            self.config = config
        else:
            self.config = WpsConfiguration(config)

        domains_count = len(self.config['domains'])
        self.state_machine = WpsStateMachine(
            domains_count,
            check_progress_update,
            lambda line: 'Successful completion of geogrid.' in line,
            lambda line: 'ERROR' in line,
            progress_update_cb)

        self.program = Program(
            './geogrid.exe',
            self.state_machine.process_line,
            self.state_machine.process_line,
            log_file=log_file)

        self.print_message_cb = print_message_cb

    def print_message(self, message):
        if self.print_message_cb:
            self.print_message_cb(message)

    async def run(self):

        os.chdir(system_config['wps_path'])

        self.print_message('Processing the configuration file...')

        # Generate the config file and save it
        config_file_content = self.config.get_namelist()

        # Generate the namelist
        with open('namelist.wps', 'w') as namelist_file:
            namelist_file.write(config_file_content)

        self.state_machine.reset()
        self.print_message('Initializing...')

        return_code = await self.program.run()

        return self.state_machine.state == 'done' and return_code == 0
