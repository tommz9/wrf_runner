# -*- coding: utf-8 -*-

"""
Code to represent and manipulate the GEOGRID program.
"""

import re
from typing import Callable
import os
import logging

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

        self.logger = logging.getLogger(__name__ + '.' + Geogrid.__name__)

        def log_progress(current_domain, max_domains):
            self.logger.info(
                f'Processing domain {current_domain} out of {max_domains}.')

        domains_count = len(self.config['domains'])
        self.state_machine = WpsStateMachine(
            domains_count,
            check_progress_update,
            lambda line: 'Successful completion of geogrid.' in line,
            lambda line: 'ERROR' in line,
            log_progress)

        self.program = Program(
            './geogrid.exe',
            self.state_machine.process_line,
            self.state_machine.process_line,
            log_file=log_file)

    def __str__(self):
        if self.state_machine.current_domain == 0:
            return 'Geogrid (not running)'

        return f'Geogrid(processing domain '\
            '{self.state_machine.current_domain} '\
            'out of {self.state_machine.max_domains}'

    async def run(self):
        self.logger.info('Starting.')

        os.chdir(system_config['wps_path'])

        self.logger.info('Processing the configuration file...')

        # Generate the config file and save it
        config_file_content = self.config.get_namelist()

        # Generate the namelist
        with open('namelist.wps', 'w') as namelist_file:
            namelist_file.write(config_file_content)

        self.state_machine.reset()
        self.logger.info('Initializing...')

        return_code = await self.program.run()

        return self.state_machine.state == 'done' and return_code == 0
