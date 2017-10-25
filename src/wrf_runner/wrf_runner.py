# -*- coding: utf-8 -*-

"""Main module."""

from os import getenv
import asyncio

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
        self.app.add_route(self.test, '/')

        self.current_step = None

    def add_step(self, step):
        self.steps.append(step)

    async def run_steps(self):
        for step in self.steps:
            print(step)
            self.current_step = step
            await step.run()

    async def test(self, request):
        header = '<html><body><h1>WRF Runner</h1>'
        footer = '</body></html>'
        if self.current_step is None:
            return response.html(header + '<p>Nothing is running</p>' + footer)

        return response.html(
            header +
            '<p>Step `{}` is running.</p>'.format(str(self.current_step)) +
            footer)

    def run(self):

        server = self.app.create_server(host="0.0.0.0", port=8000)
        # asyncio.ensure_future(server)

        self.event_loop.create_task(server)

        self.event_loop.run_until_complete(self.run_steps())
