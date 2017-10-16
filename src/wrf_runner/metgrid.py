import os
from typing import Callable

from .wrf_runner import system_config
from .namelist import generate_config_file
from .wps_state_machine import WpsStateMachine
from . import geogrid
from .program import Program
from . import namelist_metgrid

class Metgrid:
    def __init__(self,
                config,
                progress_update_cb: Callable[[int, int], None] = None,
                print_message_cb: Callable[[str], None] = None,
                log_file=None):
        
        try:
            self.config = config['metgrid']
        except KeyError:
            self.config = config

        domain_count = 3 # TODO

        self.state_machine = WpsStateMachine(
            domain_count,
            geogrid.check_progress_update,
            lambda line: 'Successful completion of metgrid.' in line,
            lambda line: 'ERROR' in line,
            progress_update_cb
        )

        self.program = Program(
            './metgrid.exe',
            self.state_machine.process_line,
            self.state_machine.process_line,
            log_file=log_file
        )

        self.print_message_cb = print_message_cb

    def generate_namelist_dict(self):
        return namelist_metgrid.config_to_namelist(self.config)

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