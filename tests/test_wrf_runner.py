#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `wrf_runner` package."""
import asyncio
from datetime import datetime

import aiohttp
import async_timeout

import pytest
from wrf_runner import WrfException

from wrf_runner import wrf_runner


class TestConfiguration:

    @pytest.mark.parametrize("config", [{}, 5, 'nonsense'])
    def test_basic_wrong(self, config):
        with pytest.raises(WrfException):
            wrf_runner.check_configuration(config)


def test_web_starts():

    class Tester:
        def __init__(self):
            self.response_text = None
            self.response_status = None

        async def fetch(self):
            await asyncio.sleep(1)
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(1):
                    async with session.get("http://127.0.0.1:8000/") as response:
                        self.response_text = await response.text()
                        self.response_status = response.status

    class Waiting:

        def __init__(self, waiting_time=10):
            self.waiting_time = waiting_time
            self.start_time = None

        async def run(self):
            self.start_time = datetime.now()
            await asyncio.sleep(self.waiting_time)

        def __str__(self):
            if self.start_time:
                now = datetime.now()

                remaining = self.waiting_time - (now - self.start_time).seconds
                return f"Dummy waiting step. Remaining {remaining} seconds."
            else:
                return f"Dummy waiting step. Not active."

    tester = Tester()

    loop = asyncio.get_event_loop()
    loop.create_task(tester.fetch())
    runner = wrf_runner.WrfRunner(event_loop=loop)
    runner.add_step(Waiting(2))

    runner.run()

    assert (tester.response_status == 200)
    assert (tester.response_text is not None)
