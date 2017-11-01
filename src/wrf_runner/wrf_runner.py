# -*- coding: utf-8 -*-

"""Main module."""

from os import getenv
import asyncio
import logging

import jsonschema
from sanic import Sanic
from sanic import response

from .wrf_exceptions import WrfException
from .configuration import WpsConfiguration

configuration_schema = {
    "type": "object",
    "properties": {
        "geogrib": {"type": "object"},
        "ungrib": {"type": "object"},
        "metgrib": {"type": "object"},
        "real": {"type": "object"},
        "wrf": {"type": "object"}
    },
    "required": ["geogrib", "ungrib", "metgrib", "real", "wrf"]
}

system_config = {
    'wps_path': getenv('WPS_PATH', None)
}


def check_configuration(config):
    WpsConfiguration(config)


class WrfRunner:
    def __init__(self, event_loop=None):
        self.steps = []

        if event_loop is None:
            self.event_loop = asyncio.get_event_loop()
        else:
            self.event_loop = event_loop

        self.app = Sanic(__name__)
        self.app.add_route(self.html_handler, '/')

        self.current_step = None

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('INFO')

    def add_step(self, step):
        """Add a step to the pipeline.

        step: an object with a run() coroutine
        """
        self.steps.append(step)
        self.logger.info(f'Step registered: `{step}`')

        return self

    async def run_steps(self):
        for step in self.steps:
            self.logger.info(f'Starting step `{step}`.')
            self.current_step = step
            return_code = await step.run()
            if not return_code:
                self.logger.error(f'Failed step `{step}`')
                return False
        self.logger.info('Finished all steps.')
        return True

    async def html_handler(self, request):
        header = '<html><body><h1>WRF Runner</h1>'
        footer = '</body></html>'
        if self.current_step is None:
            return response.html(header + '<p>Nothing is running</p>' + footer)

        return response.html(
            header +
            f'<p>Step `{self.current_step}` is running.</p>' +
            footer)

    def run(self):

        server = self.app.create_server(host="0.0.0.0", port=8000)
        self.event_loop.create_task(server)

        self.logger.info('Starting the event loop.')
        retcode = self.event_loop.run_until_complete(self.run_steps())

        return retcode
