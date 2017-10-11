# -*- coding: utf-8 -*-

import asyncio
import datetime
import os

import dateparser
import jsonschema

from . import namelist_ungrib
from .namelist import generate_config_file
from .wrf_exceptions import WrfException
from .wrf_runner import system_config

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


class Ungrib:
    def __init__(self, config, environment_config=None):
        """"""

        if environment_config is None:
            self.environment_config = system_config

        try:
            self.config = config['ungrib']
        except KeyError:
            self.config = config

        self.error_run = False

        # Process the datetime
        if isinstance(self.config['start_date'], str):
            self.config['start_date'] = dateparser.parse(self.config['start_date'])
        if isinstance(self.config['end_date'], str):
            self.config['end_date'] = dateparser.parse(self.config['end_date'])

    def generate_namelist_dict(self):
        return namelist_ungrib.config_to_namelist(self.config)

    def stderr_callback(self, line: str):
        print('UNGRIB stderr:', line)
        if 'ERROR' in line:
            self.error_run = True

    def stdout_callback(self, line: str):
        print('UNGRIB stdout:', line)

        if 'ERROR' in line:
            self.error_run = True

    def print_message(self, message):
        print(message)

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
                    cb(line.decode('ASCII').strip())
                else:
                    return

        self.print_message('Initializing...')

        # Run the program
        process = await asyncio.create_subprocess_exec('./ungrib.exe', stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)

        # Setup the line callbacks
        await stream_reader(process.stdout, self.stdout_callback)
        await stream_reader(process.stderr, self.stderr_callback)

        # Wait for the program to end
        return_code = await process.wait()

        # Evaluate the result
        return not return_code
