# -*- coding: utf-8 -*-

import logging
import os
from typing import Callable
import glob

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
                 log_file=None):
        """"""

        if isinstance(config, WpsConfiguration):
            self.config = config
        else:
            self.config = WpsConfiguration(config)

        files_count = 10  # TODO

        self.logger = logging.getLogger(__name__ + '.' + Ungrib.__name__)

        def log_progress(current_domain, max_domains):
            self.logger.info(f'Processing next time ...')

        self.state_machine = WpsStateMachine(
            files_count,
            check_progress_update,
            lambda line: 'Successful completion of ungrib.' in line,
            lambda line: 'ERROR' in line,
            log_progress
        )

        self.program = Program(
            './ungrib.exe',
            self.state_machine.process_line,
            self.state_machine.process_line,
            log_file=log_file
        )

    def __str__(self):
        return 'Ungrib ()'

    async def run(self):
        self.logger.info('Ungrib starting.')

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


def grib_alphabetical_extensions():
    """Generate file extensions AAA, AAB, AAC, ..."""

    current = 'AAA'
    yield current

    while current != 'ZZZ':
        numbers = [ord(c) for c in current]

        numbers[2] += 1

        if numbers[2] > ord('Z'):
            numbers[2] = ord('A')
            numbers[1] += 1
            if numbers[1] > ord('Z'):
                numbers[1] = ord('A')
                numbers[0] += 1

        current = ''.join(map(chr, numbers))

        yield current


def link_grib(path_pattern):
    """Link the data files into the working directory.

    Python implementation of the script linkgrib.classmethod
    """

    # Delete all links
    current_links = glob.glob('GRIBFILE.???')

    for link in current_links:
        os.remove(link)

    # Get the new files
    if len(path_pattern) == 1:
        new_files = glob.glob(path_pattern)
    else:
        new_files = path_pattern

    # Link the new paths
    for extension, new_file in zip(grib_alphabetical_extensions(), new_files):
        os.symlink(new_file, 'GRIBFILE.' + extension)
