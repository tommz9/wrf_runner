# -*- coding: utf-8 -*-

import os
from typing import Callable
import logging

from .wrf_runner import system_config
from .wps_state_machine import WpsStateMachine
from . import geogrid
from .program import Program
from .configuration import WpsConfiguration


class Metgrid:
    def __init__(self,
                 config,
                 progress_update_cb: Callable[[int, int], None] = None,
                 log_file=None):

        if isinstance(config, WpsConfiguration):
            self.config = config
        else:
            self.config = WpsConfiguration(config)

        domain_count = len(config['domains'])

        self.logger = logging.getLogger(
            __name__ + '.' + Metgrid.__name__)

        def log_progress(current_domain, max_domains):
            self.logger.info(
                f'Processing domain {current_domain} out of {max_domains}.')

        self.state_machine = WpsStateMachine(
            domain_count,
            geogrid.check_progress_update,
            lambda line: 'Successful completion of metgrid.' in line,
            lambda line: 'ERROR' in line,
            log_progress
        )

        self.program = Program(
            './metgrid.exe',
            self.state_machine.process_line,
            self.state_machine.process_line,
            log_file=log_file
        )

    def __str__(self):
        if self.state_machine.current_domain == 0:
            return 'Metgrid (not running)'
        else:
            return f'Metgrid (processing domain {self.state_machine.current_domain} '\
                'out of {self.state_machine.max_domains})'

    async def run(self):
        self.logger.info('Metgrid starting.')

        # cd to the WPS folder
        os.chdir(system_config['wps_path'])

        self.logger.info('Processing the configuration file...')

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
